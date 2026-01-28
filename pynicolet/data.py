import numpy as np
import tqdm

def read_nervus_data(nrvHdr, segment=0, range_=None, chIdx=None, verbose=False):
    """
    Read data from Nicolet .e file.
    Optimized for sequential reading to minimize disk seeking.

    Parameters
    ----------
    nrvHdr : dict or object
        Header returned by read_nervus_header
    segment : int
        Segment number in the file to read from (0-based)
    range_ : list[int]
        [startIndex, endIndex] range of samples (1-based, inclusive)
    chIdx : list[int]
        List of channel indices (0-based)
    verbose : bool
        If True, show a progress bar. Default is False.

    Returns
    -------
    np.ndarray
        2D array [samples, channels] of doubles
    """

    # Default arguments
    if nrvHdr is None:
        raise ValueError("Missing argument nrvHdr")

    if segment < 0 or segment >= len(nrvHdr["Segments"]):
        raise ValueError(f"Segment index {segment} out of range (0-{len(nrvHdr['Segments'])-1})")

    if range_ is None:
        range_ = [1, nrvHdr["Segments"][segment]["sampleCount"]]
    if chIdx is None:
        chIdx = np.array(nrvHdr["matchingChannels"], dtype=int)

    assert len(range_) == 2, "Range must be [firstIndex, lastIndex]"
    assert range_[0] > 0, "Range must start at 1 or higher"

    # --- Cumulative sum of segment durations
    cSumSegments = np.concatenate(([0], np.cumsum([s["duration"] for s in nrvHdr["Segments"]]))).tolist()
    
    # Pre-build lookup for StaticPackets to avoid linear scan inside loop
    # Maps str(channel_id) -> section_index
    tag_map = {sp["tag"]: sp["index"] for sp in nrvHdr["StaticPackets"]}

    lChIdx = len(chIdx)
    sectionIdx = np.zeros(lChIdx, dtype=int)
    
    # --- Find sectionID for each channel
    for i, ch in enumerate(chIdx):
        ch_tag = str(ch)
        if ch_tag not in tag_map:
            raise ValueError(f"Channel {ch} not found in StaticPackets")
        sectionIdx[i] = tag_map[ch_tag]

    # --- Prepare output array
    total_samples = range_[1] - range_[0] + 1
    out = np.zeros((total_samples, lChIdx), dtype=float)

    # --- Gather all read tasks ---
    # We want to collect all (offset, length) tuples so we can sort them and read sequentially.
    # Task format: (absolute_file_offset, sample_count, channel_out_index, output_start_sample, multiplier)
    read_tasks = []

    # Get the global allIndexIDs array for fast masking
    allIndexIDs = nrvHdr["allIndexIDs"]
    
    for i, ch in enumerate(chIdx):
        # Sampling rate and scale for this channel
        curSF = nrvHdr["Segments"][segment]["samplingRate"][ch]
        mult = nrvHdr["Segments"][segment]["scale"][ch]

        # --- Find all sections for this channel
        # Use vectorized mask on cached ID array
        mask = allIndexIDs == sectionIdx[i]
        allSections = np.where(mask)[0]
        
        # Access structured array directly
        # sectionLengths in samples (bytes / 2)
        section_entries = nrvHdr["MainIndex"][allSections]
        sectionLengths = section_entries["sectionL"] / 2.0
        
        cSectionLengths = np.concatenate(([0], np.cumsum(sectionLengths)))

        skipValues = cSumSegments[segment] * curSF
        
        # Find which sections contain the requested segment time
        # firstSectionForSegment is the index of the section where the segment starts
        candidates = np.where(cSectionLengths > skipValues)[0]
        if len(candidates) == 0:
             # Should not happen if segment exists
             continue
             
        firstSectionForSegment = candidates[0] - 1
        
        # Adjust cumulative lengths to be relative to the start of the valid data for this segment
        offsetSectionLengths = cSectionLengths - cSectionLengths[firstSectionForSegment]
        
        # Find start and end sections for the requested range
        # range_ is 1-based sample index
        
        # Section index where range starts
        # Find last section where cumulative length is less than range start
        start_candidates = np.where(offsetSectionLengths < range_[0])[0]
        firstSection = start_candidates[-1] if len(start_candidates) > 0 else 0

        samplesInChannel = nrvHdr["Segments"][segment]["sampleCount"]
        endRange = min(range_[1], samplesInChannel)
        
        if endRange < range_[0]:
            continue

        # Section index where range ends
        end_candidates = np.where(offsetSectionLengths >= endRange)[0]
        lastSection = (end_candidates[0] - 1) if len(end_candidates) > 0 else len(offsetSectionLengths) - 1

        # We must index relative to the file-wide sections
        # The 'allSections' array contains valid indices into MainIndex
        # We need to slice 'allSections' from [firstSectionForSegment + firstSection] to ...
 
        # Check bounds
        start_idx_in_all = firstSectionForSegment + firstSection
        end_idx_in_all = firstSectionForSegment + lastSection
        
        if start_idx_in_all >= len(allSections):
            continue
            
        useMiddleSectionsCount = end_idx_in_all - start_idx_in_all + 1
        
        # Calculate cursor for output buffer
        curIdx = 0 # 0-based index in 'out' array
        
        # Iterate through the relevant sections
        for k in range(useMiddleSectionsCount):
            sec_list_idx = start_idx_in_all + k
            main_index_idx = allSections[sec_list_idx]
            
            section_entry = section_entries[sec_list_idx] if sec_list_idx < len(section_entries) else nrvHdr["MainIndex"][main_index_idx]
            
            # Determine read range within this section
            # 1-based relative to the start of the segment-adjusted stream
            sec_start_sample_rel = offsetSectionLengths[firstSection + k] + 1
            sec_end_sample_rel = offsetSectionLengths[firstSection + k + 1]
            
            # Intersection with requested range_
            read_start = max(range_[0], sec_start_sample_rel)
            read_end = min(endRange, sec_end_sample_rel)
            
            if read_end < read_start:
                continue
                
            count = int(read_end - read_start + 1)
            
            # Offset within the section (0-based bytes)
            # read_start is 1-based, sec_start_sample_rel is 1-based
            offset_in_section_samples = read_start - sec_start_sample_rel
            
            # Absolute file offset
            file_offset = int(section_entry["offset"]) + int(offset_in_section_samples * 2)
            
            # Output index
            # read_start relative to range_[0]
            out_idx = int(read_start - range_[0])
            
            read_tasks.append((file_offset, count, i, out_idx, mult))

    # --- Sort tasks by file offset for sequential reading ---
    read_tasks.sort(key=lambda x: x[0])
    
    # --- Execute Reads ---
    with open(nrvHdr["filename"], "rb") as h:
        # Use a progress bar for the actual I/O
        # Use a progress bar for the actual I/O
        for offset, count, ch_out_idx, out_idx, mult in tqdm.tqdm(read_tasks, desc="Reading data chunks", mininterval=0.5, disable=not verbose):
            h.seek(offset)
            # Read 16-bit integers
            data = np.fromfile(h, dtype="<i2", count=count)
            
            # Apply scale and store
            # data is 1D array of length 'count'
            out[out_idx : out_idx + count, ch_out_idx] = data * mult

    return out