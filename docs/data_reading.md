# Reading EEG Data

`pynicolet` is designed to be flexible about how much data you load. Because clinical files can be gigabytes in size, you often only want to read specific sections.

## Basic Usage
To read all channels from the first segment:
```python
reader = NicoletReader("file.e")
data = reader.read_data()
```

## Selecting Channels
You can specify a subset of channels using 0-based indexing.
```python
# Read only channels 0, 4, and 5
data = reader.read_data(chIdx=[0, 4, 5])
```

## Reading a Specific Range
If you only need a specific window of time, use the `range_` parameter. Note that `range_` uses **1-based** inclusive indices to match standard EEG tool conventions.
```python
# Read the first 10,000 samples
data = reader.read_data(range_=[1, 10000])
```

## Managing Multiple Segments
Clinical recordings may stop and start. `pynicolet` treats these as "Segments".
```python
header = reader.read_header()
for i, seg in enumerate(header['Segments']):
    print(f"Segment {i} lasts {seg['duration']} seconds.")
    
# Read data from the second segment
data = reader.read_data(segment=1)
```

## Signal Units
The returned data is converted from binary raw integer values into physical units (usually microvolts or volts) using the resolution and gain metadata found in the header.
The shape is always `(samples, channels)`.
