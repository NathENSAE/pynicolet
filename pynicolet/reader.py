import numpy as np
from pynicolet.header import read_nervus_header
from pynicolet.data import read_nervus_data
from collections import Counter
from pynicolet.events import get_events

class NicoletReader:
    def __init__(self, filename):
        self.filename = filename
        self.header = {}
        self.data = None

    def read_header(self):
        result = read_nervus_header(self.filename)
        if result is None:
            raise ValueError(f"read_nervus_header returned None for file: {self.filename}")

        # If the header function returns a dict, merge it into self.header
        if isinstance(result, dict):
            self.header.update(result)
            return self.header

        # Otherwise expect an iterable with eight elements and unpack safely
        try:
            tags, index, qi, dynamic_packets, info, ts_infos, segments, raw_events = result
        except Exception as exc:
            raise ValueError("Unexpected return value from read_nervus_header") from exc

        self.header["filename"] = self.filename
        self.header["StaticPackets"] = tags
        self.header["MainIndex"] = index
        self.header["Qi"] = qi
        self.header["dynamicPackets"] = dynamic_packets
        self.header["info"] = info
        self.header["tsInfos"] = ts_infos
        self.header["Segments"] = segments
        self.header["raw_events"] = raw_events
        
        # Compute the most common sampling rate without scipy
        samplerates = self.header["Segments"][0]["samplingRate"]
        if samplerates:
            self.header["targetSamplingRate"] = Counter(samplerates).most_common(1)[0][0]
        else:
            self.header["targetSamplingRate"] = 0

        # Find channels matching or not matching the target rate
        self.header["matchingChannels"] = np.where(np.array(self.header["Segments"][0]["samplingRate"]) == self.header["targetSamplingRate"])[0]
        self.header["excludedChannels"] = np.where(np.array(self.header["Segments"][0]["samplingRate"]) != self.header["targetSamplingRate"])[0]

        # Get the first matching channel and count how many there are
        self.header["targetNumberOfChannels"] = len(self.header["matchingChannels"])
        
        # targetSampleCount should represent the count in the current segment or total?
        # Let's keep total for reference but read_data will handle segments.
        totalSampleCount = 0
        for segment in self.header["Segments"]:
            totalSampleCount += segment["sampleCount"]
        self.header["totalSampleCount"] = totalSampleCount
        
        # Provide a quick way to see duration/samples of first segment
        if self.header["Segments"]:
            self.header["targetSampleCount"] = self.header["Segments"][0]["sampleCount"]

        self.header["allIndexIDs"] = [entry["sectionIdx"] for entry in self.header["MainIndex"]]
        
        # Calculate event sample positions and add boundaries
        self.header["events"] = get_events(self.header)

        return self.header

    def read_data(self, segment=0, chIdx=None, range_=None):
        """
        Read data for specified segment and channels.
        
        chIdx: list of 0-based channel indices. If None, uses matchingChannels.
        range_: [start, end] 1-based sample range. If None, reads whole segment.
        """
        if not self.header:
            self.read_header()
            
        if chIdx is None:
            chIdx = self.header["matchingChannels"]
            
        self.data = read_nervus_data(self.header, segment=segment, range_=range_, chIdx=chIdx)
        return self.data

    def read_events(self):
        """
        Returns the list of processed events (sample-based).
        """
        if not self.header:
            self.read_header()
        return self.header.get("events", [])
