import numpy as np
from pynicolet.header import read_nervus_header
from pynicolet.data import read_nervus_data
from scipy import stats

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

        # Otherwise expect an iterable with seven elements and unpack safely
        try:
            tags, index, qi, dynamic_packets, info, ts_infos, segments = result
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
        
        # Compute the most common sampling rate
        self.header["targetSamplingRate"] = stats.mode(self.header["Segments"][0]["samplingRate"], keepdims=True)[0][0]

        # Find channels matching or not matching the target rate
        self.header["matchingChannels"] = np.where(np.array(self.header["Segments"][0]["samplingRate"]) == self.header["targetSamplingRate"])[0]
        self.header["excludedChannels"] = np.where(np.array(self.header["Segments"][0]["samplingRate"]) != self.header["targetSamplingRate"])[0]

        # Get the first matching channel and count how many there are
        firstMatchingChannel = self.header["matchingChannels"][0]
        self.header["targetNumberOfChannels"] = len(self.header["matchingChannels"])
        
        targetSampleCount = 0
        for segment in self.header["Segments"]:
            targetSampleCount += segment["sampleCount"]

        self.header["targetSampleCount"] = targetSampleCount
        
        self.header["allIndexIDs"] = [entry["sectionIdx"] for entry in self.header["MainIndex"]]

        
        return self.header

    def read_data(self, chIdx):
        if not self.header:
            raise ValueError("Header must be read before reading data.")
        self.data = read_nervus_data(self.header, segment=0, chIdx=chIdx)
        return self.data
