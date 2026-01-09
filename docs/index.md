# pynicolet Documentation

Welcome to the documentation for **pynicolet**, a high-performance Python library for reading legacy Nicolet EEG recordings.

## Introduction
Nicolet EEG systems (now part of Natus) have been a standard in clinical neurophysiology for decades. However, their binary formats (`.e` files) are proprietary and complex. `pynicolet` provides a clean, Pythonic interface to extract metadata (patient info, sampling rates, amplifier settings) and raw brain signals directly into NumPy arrays.

## Key Concepts

### 1. The Nicolet Reader
All interactions start with the `NicoletReader` class. It manages the file stream and provides methods to access different parts of the recording.

### 2. Multi-Segment Support
Long-term monitoring recordings often contain multiple recording segments (e.g., when the technician pauses and resumes the recording). `pynicolet` allows you to target specific segments or read them sequentially.

### 3. Events and Markers
Clinical EEG involves many markers (Exam Start, Seizure onset, Photic stimulation, etc.). `pynicolet` automatically parses these from the binary header and calculates their precise sample index relative to the start of the recording.

## Navigation
- [API Reference](api_reference.md)
- [Reading Data](data_reading.md)
- [Managing Events](events.md)
- [Binary Format Details](file_format.md)
