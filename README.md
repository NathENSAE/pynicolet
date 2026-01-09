# pynicolet

pynicolet is a lightweight Python library for reading legacy Nicolet EEG files and converting them into convenient Python data structures for analysis and visualization.

## Features
- Parse legacy Nicolet EEG file formats (amplifier/channel metadata, timestamps, and samples)
- Export to NumPy arrays
- Basic support for annotations and event markers
- Streamlined API for quick loading and inspection
- Small and dependency-light core

## Installation
Install from PyPI (when published):
```
pip install pynicolet
```
Or install from source:
```
git clone https://github.com/NathENSAE/pynicolet.git
cd pynicolet
pip install -e .
```

## Quickstart
Load a Nicolet file and convert to NumPy:
```python
from pynicolet import NicoletReader

# open file
reader = NicoletReader(filename)

# read header and channels info (optional, read_data does it automatically)
header = reader.read_header()

# read raw samples as NumPy array (samples x channels)
# defaults to first segment and all matching channels
data = reader.read_data()
```

## Supported Inputs
- Nicolet legacy binary formats (commonly used clinical EEG recordings)
- Header + data pairs typical of older Nicolet systems
Note: If your files differ, open an issue with sample metadata (not patient data) to help extend support.

## API Overview
- `NicoletReader(filename)` -> `NicoletReader`
- `NicoletReader.read_header()` -> `dict` metadata (channels, sampling rate, segments)
- `NicoletReader.read_data(segment=0, chIdx=None, range_=None)` -> `NumPy array` [samples, channels]
  - `segment`: 0-based index of the recording segment.
  - `chIdx`: List of 0-based channel indices.
  - `range_`: `[start, end]` 1-based sample range (inclusive).
- `NicoletReader.read_events()` -> `list` of event dictionaries [sample, type, value]

See the docs/ directory for full API documentation and examples.

## Contributing
Contributions are welcome. Please:
- Open issues for bugs or feature requests
- Add tests for new features
- Follow existing code style and include changelog entries

## Contact
Project: pynicolet — for questions or help open an issue on the repository.