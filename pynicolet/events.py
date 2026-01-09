import numpy as np

def get_events(nrvHdr):
    """
    Construct an event structure from data in the header,
    following the logic from the user's MATLAB script.
    """
    segments = nrvHdr.get("Segments", [])
    raw_events = nrvHdr.get("raw_events", []) # These are the events parsed in header.py
    total_samples = nrvHdr.get("totalSampleCount", 0)
    
    if not segments:
        return []

    # construct a event structure from data in the header
    # maxSampleRate = max([hdr.orig.Segments.samplingRate]);
    all_rates = []
    for s in segments:
        rates = s.get("samplingRate", [])
        if isinstance(rates, (list, np.ndarray)):
            all_rates.extend(rates)
        else:
            all_rates.append(rates)
            
    max_sample_rate = max(all_rates) if all_rates else 0
    
    # earliestDateTime = min([hdr.orig.Segments.dateOLE]);
    earliest_date_ole = min((s.get("dateOLE", float('inf')) for s in segments), default=0)
    
    calculated_events = []
    
    # Process original events
    for raw_ev in raw_events:
        evt_type = raw_ev.get("IDStr", "UNKNOWN")
        evt_value = raw_ev.get("label", "")
        evt_date_ole = raw_ev.get("dateOLE", 0)
        evt_duration_sec = raw_ev.get("duration", 0)
        
        # event(i).sample = (hdr.orig.Events(i).dateOLE-earliestDateTime)*3600*24*maxSampleRate;
        sample = (evt_date_ole - earliest_date_ole) * 3600 * 24 * max_sample_rate
        
        # if event(i).sample == 0, event(i).sample = 1;
        # elseif event(i).sample > hdr.nSamples, event(i).sample = hdr.nSamples;
        if sample <= 0:
            sample = 1
        elif total_samples > 0 and sample > total_samples:
            sample = total_samples
            
        calculated_events.append({
            'type': evt_type,
            'value': evt_value,
            'offset': 0,
            'sample': int(round(sample)),
            'duration': int(round(evt_duration_sec * max_sample_rate))
        })
        
    # Add boundary events to indicate segments
    # for i=2:length(hdr.orig.Segments)
    current_sample_offset = 0
    for i, s in enumerate(segments):
        # The MATLAB code snippet suggests adding boundaries for i=2:end
        # which means starting from the second segment.
        if i > 0:
            boundary_sample = current_sample_offset + 1
            calculated_events.append({
                'type': 'Boundary',
                'value': f'Segment {i+1}',
                'offset': 0,
                'sample': int(boundary_sample),
                'duration': 0
            })
        current_sample_offset += s.get('sampleCount', 0)
        
    # Sort events by sample
    calculated_events.sort(key=lambda x: x['sample'])
    
    return calculated_events
