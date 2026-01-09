# Events and Markers

Detailed guide on handling markers in Nicolet files.

## Event Types
Common event types found in Nicolet files include:
- **Exam start**: Typically at sample 1.
- **Seizure**: Marked by a clinician during the recording.
- **Annotation**: Custom text entered by the technician.
- **Photic**: Markers from a photic stimulator.
- **Boundary**: Automatically added by `pynicolet` to indicate where segments join.

## Accessing Events
The simplest way to get events is via `read_events()`:
```python
events = reader.read_events()
for ev in events:
    print(f"[{ev['sample']}] {ev['type']}: {ev['value']}")
```

## Synchronizing with Data
Because `pynicolet` calculates the sample index for you, you can easily find the signal corresponding to an event:

```python
data = reader.read_data()
events = reader.read_events()

# Find the first seizure
seizure = next(e for e in events if e['type'] == 'Seizure')

# Slice data around the seizure (e.g., 5 seconds before and after)
fs = reader.header['targetSamplingRate']
start = int(seizure['sample'] - 5 * fs)
end = int(seizure['sample'] + 5 * fs)

seizure_data = data[start:end, :]
```

## Raw Metadata
If you need clinical timing (date and absolute time), access `raw_events` in the header:
```python
header = reader.read_header()
for rev in header['raw_events']:
    print(f"Clinical Time: {rev['dateStr']}")
    print(f"Added by User: {rev['user']}")
```
