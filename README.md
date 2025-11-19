# pynicolet

pynicolet is a lightweight Python library for reading legacy Nicolet EEG files and converting them into convenient Python data structures for analysis and visualization.

## Features
- Parse legacy Nicolet EEG file formats (amplifier/channel metadata, timestamps, and samples)
- Export to NumPy arrays, pandas DataFrames, or MNE-compatible structures
- Basic support for annotations and event markers
- Streamlined API for quick loading and inspection
- Small and dependency-light core, optional extras for advanced workflows

## Installation
Install from PyPI (when published):
```
pip install pynicolet
```
Or install from source:
```
git clone https://github.com/your-org/pynicolet.git
cd pynicolet
pip install -e .
```

## Quickstart
Load a Nicolet file and convert to NumPy / pandas:
```python
from pynicolet import Reader

# open file
r = Reader.open("path/to/recording.dat")

# read header and channels info
meta = r.metadata
print(meta.channels)

# read raw samples as NumPy array (channels x samples)
data = r.read_samples()

# or get a pandas DataFrame (time-indexed)
df = r.to_dataframe()
```

Convert to MNE Raw (if mne is installed):
```python
raw = r.to_mne_raw()  # returns mne.io.Raw object
```

## Supported Inputs
- Nicolet legacy binary formats (commonly used clinical EEG recordings)
- Header + data pairs typical of older Nicolet systems
Note: If your files differ, open an issue with sample metadata (not patient data) to help extend support.

## API Overview
- Reader.open(path) -> Reader
- Reader.metadata -> dict-like metadata (channels, sampling rate, start time)
- Reader.read_samples(start=None, stop=None) -> numpy.ndarray
- Reader.to_dataframe() -> pandas.DataFrame
- Reader.to_mne_raw() -> mne.io.Raw (optional dependency)

See the docs/ directory for full API documentation and examples.

## Contributing
Contributions are welcome. Please:
- Open issues for bugs or feature requests
- Add tests for new features
- Follow existing code style and include changelog entries

## Testing
Run tests with pytest:
```
pip install -r dev-requirements.txt
pytest
```

## License
pynicolet is licensed under the MIT License. See LICENSE for details.

## Contact
Project: pynicolet — for questions or help open an issue on the repository.