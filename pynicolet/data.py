import numpy as np
import tqdm

def read_nervus_data(nrvHdr, segment=0, range_=None, chIdx=None):
    """
    Read data from Nicolet .e file (Python translation of FieldTrip's read_nervus_data.m)

    Parameters
    ----------
    nrvHdr : dict or object
        Header returned by read_nervus_header
    segment : int
        Segment number in the file to read from (1-based)
    range_ : list[int]
        [startIndex, endIndex] range of samples (1-based)
    chIdx : list[int]
        List of channel indices (1-based)

    Returns
    -------
    np.ndarray
        2D array [samples, channels] of doubles
    """

    # Default arguments
    if nrvHdr is None:
        raise ValueError("Missing argument nrvHdr")

    if range_ is None:
        range_ = [1, nrvHdr["targetSampleCount"]]
    if chIdx is None:
        chIdx = np.array(nrvHdr["matchingChannels"], dtype=int)

    assert len(range_) == 2, "Range must be [firstIndex, lastIndex]"
    assert range_[0] > 0, "Range must start at 1 or higher"
    assert np.isscalar(segment), "Segment must be a single value"

    # --- Cumulative sum of segment durations
    cSumSegments = np.concatenate(([0], np.cumsum([s["duration"] for s in nrvHdr["Segments"]]))).tolist()

    # --- Open .e file
    with open(nrvHdr["filename"], "rb") as h:

        lChIdx = len(chIdx)
        sectionIdx = np.zeros(lChIdx, dtype=int)

        # --- Find sectionID for each channel
        for i, ch in enumerate(chIdx):
            ch_tag = str(ch)
            tmp = next(
                (sp for sp in nrvHdr["StaticPackets"] if sp["tag"] == ch_tag),
                None
            )
            if tmp is None:
                raise ValueError(f"Channel {ch} not found in StaticPackets")
            sectionIdx[i] = tmp["index"]

        # --- Prepare output array
        out = np.zeros((range_[1] - range_[0] + 1, lChIdx), dtype=float)

        # --- Iterate over channels
        for i, ch in tqdm.tqdm(enumerate(chIdx), total=lChIdx, desc="Reading channel data"):
            # Sampling rate and scale for this channel
            curSF = nrvHdr["Segments"][segment]["samplingRate"][ch]
            mult = nrvHdr["Segments"][segment]["scale"][ch]

            # --- Find all sections for this channel
            allSectionIdx = np.array(nrvHdr["allIndexIDs"]) == sectionIdx[i]
            allSections = np.where(allSectionIdx)[0]

            sectionLengths = np.array([nrvHdr["MainIndex"][s]["sectionL"] for s in allSections]) / 2
            cSectionLengths = np.concatenate(([0], np.cumsum(sectionLengths)))

            skipValues = cSumSegments[segment] * curSF
            firstSectionForSegment = np.where(cSectionLengths > skipValues)[0][0] - 1
            lastSectionForSegment = len(cSectionLengths) - 1

            offsetSectionLengths = cSectionLengths - cSectionLengths[firstSectionForSegment]
            firstSection = np.where(offsetSectionLengths < range_[0])[0][-1]

            samplesInChannel = nrvHdr["Segments"][segment]["sampleCount"]
            endRange = min(range_[1], samplesInChannel)

            lastSection_candidates = np.where(offsetSectionLengths >= endRange)[0]
            lastSection = (lastSection_candidates[0] - 1) if len(lastSection_candidates) > 0 else len(offsetSectionLengths) - 1

            if lastSection > lastSectionForSegment:
                raise IndexError(f"Index out of range for current section: {range_[1]} > {cSectionLengths[lastSectionForSegment+1]}, channel {ch}")

            useSections = allSections[firstSection:lastSection + 1]
            useSectionL = sectionLengths[firstSection:lastSection + 1]

            # --- Read the first partial segment
            curIdx = 0
            curSec = nrvHdr["MainIndex"][useSections[0]]
            h.seek(curSec["offset"])

            firstOffset = range_[0] - offsetSectionLengths[firstSection]
            lastOffset = min(range_[1], useSectionL[0])
            lsec = int(lastOffset - firstOffset + 1)

            h.seek(int((firstOffset - 1) * 2), 1)
            data = np.fromfile(h, dtype="<i2", count=lsec) * mult
            out[curIdx:curIdx + lsec, i] = data
            curIdx += lsec

            # --- Middle full sections
            if len(useSections) > 1:
                for j in range(1, len(useSections) - 1):
                    curSec = nrvHdr["MainIndex"][useSections[j]]
                    h.seek(curSec["offset"])
                    data = np.fromfile(h, dtype="<i2", count=int(useSectionL[j])) * mult
                    out[curIdx:curIdx + len(data), i] = data
                    curIdx += len(data)

                # --- Final partial segment
                curSec = nrvHdr["MainIndex"][useSections[-1]]
                h.seek(curSec["offset"])
                lastReadLength = len(out) - curIdx
                lastData = np.fromfile(h, dtype="<i2", count=lastReadLength)
                actualReadLength = len(lastData)
                out[curIdx:curIdx + actualReadLength, i] = lastData * mult

    return out