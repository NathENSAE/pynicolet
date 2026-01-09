# API Reference

## `pynicolet.reader.NicoletReader`

The main class for interacting with Nicolet files.

### `__init__(self, filename)`
Initializes the reader.
- `filename`: Absolute or relative path to a `.e` Nicolet file.

### `read_header(self)`
Parses the file header and returns a comprehensive metadata dictionary.
- **Returns**: `dict` containing:
    - `Segments`: List of segment objects (start time, duration, sample count).
    - `tsInfos`: Detailed channel/amplifier settings.
    - `events`: List of processed, sample-based markers.
    - `raw_events`: Original binary event data.

### `read_data(self, segment=0, chIdx=None, range_=None)`
Reads raw signal data into a NumPy array.
- `segment` (int): 0-based index of the segment to read.
- `chIdx` (list): List of 0-based channel indices. If `None`, returns all matching channels.
- `range_` (list): `[start, end]` inclusive 1-based sample range.
- **Returns**: `numpy.ndarray` of shape `(samples, channels)`.

### `read_events(self)`
Retrieves the list of event markers.
- **Returns**: `list` of dictionaries. Each dictionary contains:
    - `sample`: Index of the event in the data array.
    - `type`: String category (e.g., 'Seizure', 'Annotation').
    - `value`: Additional label or duration info.

---

## Internal Functions

While these are used internally by the reader, they can be accessed for low-level debugging.

### `pynicolet.header.read_nervus_header(f)`
The core binary parser for the `.e` header structure. Handles static and dynamic packet reconstruction.

### `pynicolet.data.read_nervus_data(header, segment, range_, chIdx)`
Calculates file offsets and performs the binary read of the actual EEG samples.
