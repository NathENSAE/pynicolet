# nicoletpy/io.py
import os
import logging
import struct
import numpy as np
from datetime import datetime, timedelta
import math

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def read_nervus_header(filename):
    # --- Check file extension ---
    folder, name = os.path.split(filename)
    base, ext = os.path.splitext(filename)
    assert ext.lower() == ".e", "File extension must be .e"
    if not folder:
        filename = os.path.join(os.getcwd(), filename)

    # --- Open binary file ---
    with open(filename, "rb") as f:
        # Read header
        misc1 = struct.unpack("<5I", f.read(4 * 5))  # 5 uint32
        unknown = struct.unpack("<I", f.read(4))[0]
        indexIdx = struct.unpack("<I", f.read(4))[0]

        # Go to tags
        f.seek(172, os.SEEK_SET)
        nrTags = struct.unpack("<I", f.read(4))[0]

        Tags = []
        for i in range(nrTags):
            tag_raw = struct.unpack("<40H", f.read(2 * 40))  # 40 uint16
            # Decode UTF-16LE chars, remove nulls and trailing spaces
            tag = ''.join(chr(c) for c in tag_raw).rstrip('\x00').strip()
            index = struct.unpack("<I", f.read(4))[0]

            # Identify known GUIDs / tags
            mapping = {
                "ExtraDataTags": "ExtraDataTags",
                "SegmentStream": "SegmentStream",
                "DataStream": "DataStream",
                "InfoChangeStream": "InfoChangeStream",
                "InfoGuids": "InfoGuids",
                "{A271CCCB-515D-4590-B6A1-DC170C8D6EE2}": "TSGUID",
                "{8A19AA48-BEA0-40D5-B89F-667FC578D635}": "DERIVATIONGUID",
                "{F824D60C-995E-4D94-9578-893C755ECB99}": "FILTERGUID",
                "{02950361-35BB-4A22-9F0B-C78AAA5DB094}": "DISPLAYGUID",
                "{8E94EF21-70F5-11D3-8F72-00105A9AFD56}": "FILEINFOGUID",
                "{E4138BC0-7733-11D3-8685-0050044DAAB1}": "SRINFOGUID",
                "{C728E565-E5A0-4419-93D2-F6CFC69F3B8F}": "EVENTTYPEINFOGUID",
                "{D01B34A0-9DBD-11D3-93D3-00500400C148}": "AUDIOINFOGUID",
                "{BF7C95EF-6C3B-4E70-9E11-779BFFF58EA7}": "CHANNELGUID",
                "{2DEB82A1-D15F-4770-A4A4-CF03815F52DE}": "INPUTGUID",
                "{5B036022-2EDC-465F-86EC-C0A4AB1A7A91}": "INPUTSETTINGSGUID",
                "{99A636F2-51F7-4B9D-9569-C7D45058431A}": "PHOTICGUID",
                "{55C5E044-5541-4594-9E35-5B3004EF7647}": "ERRORGUID",
                "{223A3CA0-B5AC-43FB-B0A8-74CF8752BDBE}": "VIDEOGUID",
                "{0623B545-38BE-4939-B9D0-55F5E241278D}": "DETECTIONPARAMSGUID",
                "{CE06297D-D9D6-4E4B-8EAC-305EA1243EAB}": "PAGEGUID",
                "{782B34E8-8E51-4BB9-9701-3227BB882A23}": "ACCINFOGUID",
                "{3A6E8546-D144-4B55-A2C7-40DF579ED11E}": "RECCTRLGUID",
                "{D046F2B0-5130-41B1-ABD7-38C12B32FAC3}": "GUID TRENDINFOGUID",
                "{CBEBA8E6-1CDA-4509-B6C2-6AC2EA7DB8F8}": "HWINFOGUID",
                "{E11C4CBA-0753-4655-A1E9-2B2309D1545B}": "VIDEOSYNCGUID",
                "{B9344241-7AC1-42B5-BE9B-B7AFA16CBFA5}": "SLEEPSCOREINFOGUID",
                "{15B41C32-0294-440E-ADFF-DD8B61C8B5AE}": "FOURIERSETTINGSGUID",
                "{024FA81F-6A83-43C8-8C82-241A5501F0A1}": "SPECTRUMGUID",
                "{8032E68A-EA3E-42E8-893E-6E93C59ED515}": "SIGNALINFOGUID",
                "{30950D98-C39C-4352-AF3E-CB17D5B93DED}": "SENSORINFOGUID",
                "{F5D39CD3-A340-4172-A1A3-78B2CDBCCB9F}": "DERIVEDSIGNALINFOGUID",
                "{969FBB89-EE8E-4501-AD40-FB5A448BC4F9}": "ARTIFACTINFOGUID",
                "{02948284-17EC-4538-A7FA-8E18BD65E167}": "STUDYINFOGUID",
                "{D0B3FD0B-49D9-4BF0-8929-296DE5A55910}": "PATIENTINFOGUID",
                "{7842FEF5-A686-459D-8196-769FC0AD99B3}": "DOCUMENTINFOGUID",
                "{BCDAEE87-2496-4DF4-B07C-8B4E31E3C495}": "USERSINFOGUID",
                "{B799F680-72A4-11D3-93D3-00500400C148}": "EVENTGUID",
                "{AF2B3281-7FCE-11D2-B2DE-00104B6FC652}": "SHORTSAMPLESGUID",
                "{89A091B3-972E-4DA2-9266-261B186302A9}": "DELAYLINESAMPLESGUID",
                "{291E2381-B3B4-44D1-BB77-8CF5C24420D7}": "GENERALSAMPLESGUID",
                "{5F11C628-FCCC-4FDD-B429-5EC94CB3AFEB}": "FILTERSAMPLESGUID",
                "{728087F8-73E1-44D1-8882-C770976478A2}": "DATEXDATAGUID",
                "{35F356D9-0F1C-4DFE-8286-D3DB3346FD75}": "TESTINFOGUID"
            }

            IDStr = mapping.get(tag, str(tag) if tag.isdigit() else "UNKNOWN")
            Tags.append({"tag": tag, "index": index, "IDStr": IDStr})
    
        f.seek(172208, os.SEEK_SET)

        Qi = {}
        Qi["nrEntries"] = struct.unpack("<I", f.read(4))[0]   # uint32
        Qi["misc1"]     = struct.unpack("<I", f.read(4))[0]   # uint32
        Qi["indexIdx"]  = struct.unpack("<I", f.read(4))[0]   # uint32
        Qi["misc3"]     = struct.unpack("<I", f.read(4))[0]   # uint32
        Qi["LQi"]       = struct.unpack("<Q", f.read(8))[0]   # uint64
        Qi["firstIdx"]  = np.frombuffer(f.read(8 * nrTags), dtype="<u8")  # uint64[nrTags]

        """
        Parse the main Index from a Nicolet .e file.
        Equivalent of the MATLAB 'Get Main Index' block.
        """
        Index = []
        cur_idx = 0
        next_index_pointer = indexIdx
        cur_idx2 = 1

        while cur_idx < Qi["nrEntries"]:

            f.seek(next_index_pointer)
            nr_idx = struct.unpack("<Q", f.read(8))[0]  # uint64
            var = np.frombuffer(f.read(8 * 3 * nr_idx), dtype="<u8")  # 3 * uint64 values

            for i in range(nr_idx):
                sectionIdx = int(var[3 * i])
                offset = int(var[3 * i + 1])
                var3 = int(var[3 * i + 2])
                blockL = var3 % (2 ** 32)
                sectionL = round(var3 / (2 ** 32))

                Index.append({
                    "sectionIdx": sectionIdx,
                    "offset": offset,
                    "blockL": blockL,
                    "sectionL": sectionL
                })

            next_index_pointer = struct.unpack("<Q", f.read(8))[0]
            cur_idx += nr_idx
            cur_idx2 += 1

        
        """
        Translate of MATLAB 'READ DYNAMIC PACKETS' section.
        Reads and parses dynamic packet headers and data from a Nicolet .e file.
        """
        dynamicPackets = []

        # --- Locate InfoChangeStream section ---
        info_change_tag = next((t for t in Tags if t['IDStr'] == 'InfoChangeStream'), None)
        if info_change_tag is None:
             logger.warning("No InfoChangeStream found in Tags. Dynamic packets might be missing.")
             nrDynamicPackets = 0
             offset = 0
        else:
            offset = Index[info_change_tag['index']]['offset']
            section_len = Index[info_change_tag['index']]['sectionL']
            nrDynamicPackets = section_len // 48
    
        if nrDynamicPackets > 0:
            f.seek(offset, os.SEEK_SET)

        # --- Read packet headers (without actual data) ---
        for i in range(nrDynamicPackets):
            packet_offset = offset + (i + 1) * 48

            guidmixed = np.frombuffer(f.read(16), dtype=np.uint8)
            # MATLAB indexing pattern translated to Python:
            reorder = [3, 2, 1, 0, 5, 4, 7, 6, 8, 9, 10, 11, 12, 13, 14, 15]
            guidnonmixed = guidmixed[reorder]

            guid_hex = ''.join([f'{x:02X}' for x in guidnonmixed])
            guid_str = '{{{:02X}{:02X}{:02X}{:02X}-{:02X}{:02X}-{:02X}{:02X}-{:02X}{:02X}-{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}}}'.format(*guidnonmixed)

            date_serial = struct.unpack('<d', f.read(8))[0]
            datefrac = struct.unpack('<d', f.read(8))[0]
            internalOffsetStart = struct.unpack('<Q', f.read(8))[0]
            packetSize = struct.unpack('<Q', f.read(8))[0]

            base_date = datetime(1899, 12, 31)
            if not math.isfinite(date_serial) or date_serial < 0 or date_serial > 1e7:
                # Invalid or absurd value → skip or set default
                date = None
            else:
                date = base_date + timedelta(days=date_serial)

            # Identify packet type based on GUID
            guid_map = {
                'BF7C95EF6C3B4E709E11779BFFF58EA7': 'CHANNELGUID',
                '8A19AA48BEA040D5B89F667FC578D635': 'DERIVATIONGUID',
                'F824D60C995E4D949578893C755ECB99': 'FILTERGUID',
                '0295036135BB4A229F0BC78AAA5DB094': 'DISPLAYGUID',
                '782B34E88E514BB997013227BB882A23': 'ACCINFOGUID',
                'A271CCCB515D4590B6A1DC170C8D6EE2': 'TSGUID',
                'D01B34A09DBD11D393D300500400C148': 'AUDIOINFOGUID'
            }

            IDStr = guid_map.get(guid_hex, 'UNKNOWN')

            dynamicPackets.append({
                'offset': packet_offset,
                'guid': guid_hex,
                'guidAsStr': guid_str,
                'date': date,
                'datefrac': datefrac,
                'internalOffsetStart': internalOffsetStart,
                'packetSize': packetSize,
                'data': bytearray(),
                'IDStr': IDStr
            })

        # --- Read actual data for each packet ---
        for dp in dynamicPackets:
            # Find tag corresponding to this GUID.
            # Tag formatting in the header may differ in case, braces or hyphens from the
            # GUID string we build here, so normalize both sides before comparing.
            def _norm_guid(s):
                if not isinstance(s, str):
                    return ""
                return s.upper().replace('{', '').replace('}', '').replace('-', '').strip()

            infoIdx = None
            dp_norm = _norm_guid(dp.get('guidAsStr', ''))
            for t in Tags:
                if _norm_guid(t.get('tag', '')) == dp_norm:
                    infoIdx = t.get('index')
                    break

            # Fallback: sometimes Tags carry an IDStr (mapping name). Try matching by IDStr
            # against the packet IDStr computed earlier.
            if infoIdx is None:
                for t in Tags:
                    if t.get('IDStr') and t.get('IDStr') == dp.get('IDStr'):
                        infoIdx = t.get('index')
                        break

            if infoIdx is None:
                # No matching tag found for this dynamic packet - log and skip it instead
                logger.warning("No tag found matching dynamic packet GUID %s (hex=%s). Skipping packet.", dp.get('guidAsStr'), dp.get('guid'))
                # leave dp['data'] empty and continue
                continue

            # Get matching index segments
            indexInstances = [ix for ix in Index if ix['sectionIdx'] == infoIdx]

            internalOffset = 0
            remainingData = dp['packetSize']
            currentTargetStart = dp['internalOffsetStart']

            for currentInstance in indexInstances:
                sectionL = currentInstance['sectionL']
                offset = currentInstance['offset']

                if internalOffset <= currentTargetStart < (internalOffset + sectionL):
                    startAt = currentTargetStart
                    stopAt = min(startAt + remainingData, internalOffset + sectionL)
                    readLength = stopAt - startAt
                    filePosStart = offset + (startAt - internalOffset)

                    f.seek(filePosStart, 0)
                    dataPart = f.read(int(readLength))
                    dp['data'].extend(dataPart)

                    remainingData -= readLength
                    currentTargetStart += readLength

                internalOffset += sectionL

        # Define property names
        info_props = [
            'patientID', 'firstName', 'middleName', 'lastName',
            'altID', 'mothersMaidenName', 'DOB', 'DOD', 'street', 'sexID', 'phone',
            'notes', 'dominance', 'siteID', 'suffix', 'prefix', 'degree', 'apartment',
            'city', 'state', 'country', 'language', 'height', 'weight', 'race', 'religion',
            'maritalStatus'
        ]
        info = {}

        # Locate the PATIENTINFOGUID tag
        info_idx_struct = next((t for t in Tags if t['IDStr'] == 'PATIENTINFOGUID'), None)
        if info_idx_struct:
            info_idx = info_idx_struct['index']
            index_instance = next((i for i in Index if i['sectionIdx'] == info_idx), None)
            if index_instance is None:
                return None

            # Move to the offset in the file
            f.seek(index_instance['offset'], 0)

            # Read fields
            guid = f.read(16)  # uint8 * 16
            l_section = struct.unpack('<Q', f.read(8))[0]
            nr_values = struct.unpack('<Q', f.read(8))[0]
            nr_bstr = struct.unpack('<Q', f.read(8))[0]

            # Parse numeric values
            for _ in range(nr_values):
                id_val = struct.unpack('<Q', f.read(8))[0]
                if id_val in (7, 8):  # DOB / DOD
                    unix_days = struct.unpack('<d', f.read(8))[0]
                    unix_time = (unix_days * 86400) - 2209161600
                    date = datetime(1970, 1, 1) + timedelta(seconds=unix_time)
                    value = [date.day, date.month, date.year]
                elif id_val in (23, 24):
                    value = struct.unpack('<d', f.read(8))[0]
                else:
                    value = 0

                if id_val - 1 < len(info_props):
                    info[info_props[id_val - 1]] = value

            # Parse strings
            str_setup = struct.unpack('<' + 'Q' * (nr_bstr * 2), f.read(8 * nr_bstr * 2))

            for i in range(0, len(str_setup), 2):
                id_val = str_setup[i]
                strlen = str_setup[i + 1]
                raw_str = f.read(strlen * 2 + 2)  # +2 like MATLAB reading strSetup(i+1)+1
                # Decode UTF-16LE string (since MATLAB fread(...,'uint16') reads UTF-16 code units)
                value = raw_str.decode('utf-16le').rstrip('\x00').strip()
                if id_val - 1 < len(info_props):
                    info[info_props[id_val - 1]] = value

        # Find TS packets
        ts_packets = [p for p in dynamicPackets if p['IDStr'] == 'TSGUID']
        ts_packets_type = "dynamic"

        # Try to find TSGUID in the tags
        if not ts_packets:
            ts_packets = [t for t in Tags if t['IDStr'] == 'TSGUID']
            ts_packets_type = "tag"
        
        tsInfos = []

        if not ts_packets:
            print("Warning: No TSGUID found")
            
        elif ts_packets_type == "dynamic":

            for ts_packet in ts_packets:
                data = ts_packet['data']

                elems = struct.unpack('<I', data[752:756])[0]
                alloc = struct.unpack('<I', data[756:760])[0]

                offset = 760
                ts_info_list = []

                for _ in range(elems):
                    internal_offset = 0
                    ts_info = {}

                    # Label (UTF-16LE string)
                    ts_info['label'] = data[offset:offset + 64 * 2].decode('utf-16-le').strip('\x00').strip()
                    internal_offset += 64 * 2

                    # Active sensor
                    ts_info['activeSensor'] = data[offset + internal_offset:offset + internal_offset + 64 * 2].decode('utf-16-le', errors='ignore').strip('\x00').strip()
                    internal_offset += 64 * 2

                    # Reference sensor
                    ts_info['refSensor'] = data[offset + internal_offset:offset + internal_offset + 8].decode('utf-16-le', errors='ignore').strip('\x00').strip()
                    internal_offset += 8

                    # Skip 56 bytes
                    internal_offset += 56

                    # Floating-point parameters
                    ts_info['dLowCut'] = struct.unpack('<d', data[offset + internal_offset:offset + internal_offset + 8])[0]
                    internal_offset += 8
                    ts_info['dHighCut'] = struct.unpack('<d', data[offset + internal_offset:offset + internal_offset + 8])[0]
                    internal_offset += 8
                    ts_info['dSamplingRate'] = struct.unpack('<d', data[offset + internal_offset:offset + internal_offset + 8])[0]
                    internal_offset += 8
                    ts_info['dResolution'] = struct.unpack('<d', data[offset + internal_offset:offset + internal_offset + 8])[0]
                    internal_offset += 8
                    ts_info['bMark'] = struct.unpack('<H', data[offset + internal_offset:offset + internal_offset + 2])[0]
                    internal_offset += 2
                    ts_info['bNotch'] = struct.unpack('<H', data[offset + internal_offset:offset + internal_offset + 2])[0]
                    internal_offset += 2
                    ts_info['dEegOffset'] = struct.unpack('<d', data[offset + internal_offset:offset + internal_offset + 8])[0]

                    # Move to next TS entry (552 bytes per entry)
                    offset += 552
                    ts_info_list.append(ts_info)

                tsInfos.append(ts_info_list)
        elif ts_packets_type == "tag":
            ts_packet = ts_packets[0]
            indexInstance = next((i for i in Index if i['sectionIdx'] == ts_packet['index']), None)
            if indexInstance is None:
                logger.error("TSGUID tag found but no corresponding entry in Main Index.")
                return Tags, Index, Qi, dynamicPackets, info, tsInfos, []
            offset = indexInstance['offset']

            f.seek(offset, os.SEEK_SET)

            guidmixed = np.frombuffer(f.read(16), dtype=np.uint8)

            order = [3, 2, 1, 0, 5, 4, 7, 6, 8, 9, 10, 11, 12, 13, 14, 15]
            guidnonmixed = guidmixed[order]

            guid_str = ''.join([f"{x:02X}" for x in guidnonmixed])
            guidAsStr = (
                f"{{{guidnonmixed[0]:02X}{guidnonmixed[1]:02X}{guidnonmixed[2]:02X}{guidnonmixed[3]:02X}-"
                f"{guidnonmixed[4]:02X}{guidnonmixed[5]:02X}-"
                f"{guidnonmixed[6]:02X}{guidnonmixed[7]:02X}-"
                f"{guidnonmixed[8]:02X}{guidnonmixed[9]:02X}-"
                f"{''.join([f'{x:02X}' for x in guidnonmixed[10:]])}}}"
            )

            packetLength = struct.unpack('<Q', f.read(8))[0]

            dataPart = np.frombuffer(f.read(packetLength), dtype=np.uint8)

            elems = struct.unpack('<I', dataPart[728:732].tobytes())[0]
            offset = 736

            # Build a single channel-list for this static TS packet, then
            # wrap it in a list so `tsInfos` has the same shape as the
            # dynamic branch (list of channel-lists per TS packet/segment).
            ts_info_list = []
            for i in range(elems):
                internalOffset = 0

                label_bytes = dataPart[offset:offset + 32 * 2]
                label = label_bytes.tobytes().decode('utf-16-le').strip('\x00').strip()
                internalOffset += 64 * 2

                activeSensor_bytes = dataPart[offset + internalOffset:offset + internalOffset + 64]
                activeSensor = activeSensor_bytes.tobytes().decode('utf-16-le').strip('\x00')
                internalOffset += 64

                refSensor_bytes = dataPart[offset + internalOffset:offset + internalOffset + 8]
                refSensor = refSensor_bytes.tobytes().decode('utf-16-le').strip('\x00')
                internalOffset += 8

                internalOffset += 56

                lowcut = struct.unpack('<d', dataPart[offset + internalOffset:offset + internalOffset + 8].tobytes())[0]
                internalOffset += 8
                hiCut = struct.unpack('<d', dataPart[offset + internalOffset:offset + internalOffset + 8].tobytes())[0]
                internalOffset += 8
                samplingRate = struct.unpack('<d', dataPart[offset + internalOffset:offset + internalOffset + 8].tobytes())[0]
                internalOffset += 8
                resolution = struct.unpack('<d', dataPart[offset + internalOffset:offset + internalOffset + 8].tobytes())[0]
                internalOffset += 8
                specialMark = struct.unpack('<H', dataPart[offset + internalOffset:offset + internalOffset + 2].tobytes())[0]
                internalOffset += 2
                notch = struct.unpack('<H', dataPart[offset + internalOffset:offset + internalOffset + 2].tobytes())[0]
                internalOffset += 2
                eeg_offset = struct.unpack('<d', dataPart[offset + internalOffset:offset + internalOffset + 8].tobytes())[0]

                # Provide both naming conventions so the rest of the code
                # (which expects dynamic-style keys like dSamplingRate) can work.
                ts_info_list.append({
                    "label": label,
                    "activeSensor": activeSensor,
                    "refSensor": refSensor,
                    # add dynamic-style names expected elsewhere
                    "dLowCut": lowcut,
                    "dHighCut": hiCut,
                    "dSamplingRate": samplingRate,
                    "dResolution": resolution,
                    "bMark": specialMark,
                    "bNotch": notch,
                    "dEegOffset": eeg_offset,
                })

                offset += 552

            # Wrap into a list so later code can index per-segment: tsInfos[0] -> channel-list
            tsInfos = [ts_info_list]

        # ---- SEGMENT INFO ----
        seg_tag = next((t for t in Tags if t['IDStr'] == 'SegmentStream'), None)
        if seg_tag is None:
            print("Warning: No SegmentStream tag found")
            return Tags, Index, Qi, dynamicPackets, info, tsInfos, []

        segment_idx = seg_tag['index']
        segment_instance = next(i for i in Index if i['sectionIdx'] == segment_idx)

        nr_segments = int(segment_instance['sectionL'] / 152)
        f.seek(segment_instance['offset'], os.SEEK_SET)

        segments = []
        for _ in range(nr_segments):
            date_OLE = struct.unpack('<d', f.read(8))[0]
            unix_time = (date_OLE * 86400) - 2209161600
            date = datetime(1970, 1, 1) + timedelta(seconds=unix_time)
            start_date = [date.year, date.month, date.day]
            start_time = [date.hour, date.minute, date.second]

            f.seek(8, os.SEEK_CUR)
            duration = struct.unpack('<d', f.read(8))[0]
            f.seek(128, os.SEEK_CUR)

            segments.append({
                'dateOLE': date_OLE,
                'dateStr': date.strftime('%Y-%m-%d %H:%M:%S'),
                'startDate': start_date,
                'startTime': start_time,
                'duration': duration
            })

        # ---- CHANNELS & SAMPLING ----
        for i_seg, seg in enumerate(segments):
            if i_seg >= len(tsInfos):
                tsInfos.append(tsInfos[-1])

            ts_info_list = tsInfos[i_seg]
            seg['chName'] = [ch['label'] for ch in ts_info_list]
            seg['refName'] = [ch['refSensor'] for ch in ts_info_list]
            seg['samplingRate'] = [ch['dSamplingRate'] for ch in ts_info_list]
            seg['scale'] = [ch['dResolution'] for ch in ts_info_list]
            seg['sampleCount'] = max(np.array(segments[i_seg]['duration'] * np.array(seg['samplingRate']), dtype=int))

        # ---- EVENTS ----
        events = read_nervus_header_events(f, Tags, Index)

    return Tags, Index, Qi, dynamicPackets, info, tsInfos, segments, events

def read_nervus_header_events(f, Tags, Index):
    """
    Get events from the section tagged 'Events'.
    Translated from MATLAB code by Andrei Barborica.
    """
    DAYSECS = 86400.0
    DATETIMEMINUSFACTOR = 2209161600

    # Find sequence of events, that are stored in the section tagged 'Events'
    # Check both 'tag' and 'IDStr' for 'Events'
    events_tag = next((t for t in Tags if t['tag'] == 'Events' or t['IDStr'] == 'Events'), None)
    if events_tag is None:
        return []

    idxSection = events_tag['index']
    index_entry = next((i for i in Index if i['sectionIdx'] == idxSection), None)
    if index_entry is None:
        return []

    offset = index_entry['offset']

    # GUID for event packet header: {B799F680-72A4-11D3-93D3-00500400C148}
    evtPktGUID = bytes([0x80, 0xF6, 0x99, 0xB7, 0xA4, 0x72, 0xD3, 0x11, 0x93, 0xD3, 0x00, 0x50, 0x04, 0x00, 0xC1, 0x48])
    
    HCEVENT_ANNOTATION = "{A5A95612-A7F8-11CF-831A-0800091B5BDA}"
    HCEVENT_SEIZURE = "{A5A95646-A7F8-11CF-831A-0800091B5BDA}"
    HCEVENT_FORMATCHANGE = "{08784382-C765-11D3-90CE-00104B6F4F70}"
    HCEVENT_PHOTIC = "{6FF394DA-D1B8-46DA-B78F-866C67CF02AF}"
    HCEVENT_POSTHYPERVENT = "{481DFC97-013C-4BC5-A203-871B0375A519}"
    HCEVENT_REVIEWPROGRESS = "{725798BF-CD1C-4909-B793-6C7864C27AB7}"
    HCEVENT_EXAMSTART = "{96315D79-5C24-4A65-B334-E31A95088D55}"
    HCEVENT_HYPERVENTILATION = "{A5A95608-A7F8-11CF-831A-0800091B5BDA}"
    HCEVENT_IMPEDANCE = "{A5A95617-A7F8-11CF-831A-0800091B5BDA}"

    f.seek(offset, os.SEEK_SET)
    eventMarkers = []
    
    while True:
        pktGUID = f.read(16)
        if len(pktGUID) < 16 or pktGUID != evtPktGUID:
            break
            
        pktLen = struct.unpack('<Q', f.read(8))[0]
        
        f.seek(8, os.SEEK_CUR) # Skip eventID
        evtDate = struct.unpack('<d', f.read(8))[0]
        evtDateFraction = struct.unpack('<d', f.read(8))[0]
        
        evtPOSIXTime = evtDate * DAYSECS + evtDateFraction - DATETIMEMINUSFACTOR
        dt = datetime(1970, 1, 1) + timedelta(seconds=evtPOSIXTime)
        
        duration = struct.unpack('<d', f.read(8))[0]
        f.seek(48, os.SEEK_CUR)
        
        evtUser_raw = struct.unpack('<12H', f.read(24))
        user = ''.join(chr(c) for c in evtUser_raw).rstrip('\x00').strip()
        
        evtTextLen = struct.unpack('<Q', f.read(8))[0]
        evtGUID_raw = f.read(16)
        # GUID formatting from MATLAB: sprintf('{%.2X%.2X%.2X%.2X-%.2X%.2X-%.2X%.2X-%.2X%.2X-%.2X%.2X%.2X%.2X%.2X%.2X}',evtGUID([4 3 2 1 6 5 8 7 9:16]));
        g = evtGUID_raw
        guid_str = "{{{:02X}{:02X}{:02X}{:02X}-{:02X}{:02X}-{:02X}{:02X}-{:02X}{:02X}-{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}}}".format(
            g[3], g[2], g[1], g[0], g[5], g[4], g[7], g[6], g[8], g[9], g[10], g[11], g[12], g[13], g[14], g[15]
        )
        
        f.seek(16, os.SEEK_CUR) # Skip Reserved4 array
        evtLabel_raw = struct.unpack('<32H', f.read(64))
        label = ''.join(chr(c) for c in evtLabel_raw).split('\x00')[0].strip()
        
        marker = {
            'dateOLE': evtDate,
            'dateFraction': evtDateFraction,
            'dateStr': dt.strftime('%d-%B-%Y %H:%M:%S.%f')[:-3],
            'date': dt,
            'duration': duration,
            'user': user,
            'GUID': guid_str,
            'label': label,
            'IDStr': 'UNKNOWN'
        }
        
        mapping = {
            HCEVENT_SEIZURE: 'Seizure',
            HCEVENT_ANNOTATION: 'Annotation',
            HCEVENT_FORMATCHANGE: 'Format change',
            HCEVENT_PHOTIC: 'Photic',
            HCEVENT_POSTHYPERVENT: 'Posthyperventilation',
            HCEVENT_REVIEWPROGRESS: 'Review progress',
            HCEVENT_EXAMSTART: 'Exam start',
            HCEVENT_HYPERVENTILATION: 'Hyperventilation',
            HCEVENT_IMPEDANCE: 'Impedance'
        }
        marker['IDStr'] = mapping.get(guid_str, 'UNKNOWN')
        
        if guid_str == HCEVENT_ANNOTATION and evtTextLen > 0:
            f.seek(32, os.SEEK_CUR) # Skip Reserved5 array
            evtAnnotation_raw = struct.unpack(f'<{evtTextLen}H', f.read(int(evtTextLen*2)))
            marker['annotation'] = ''.join(chr(c) for c in evtAnnotation_raw).rstrip('\x00').strip()
        
        eventMarkers.append(marker)
        
        offset += pktLen
        f.seek(offset, os.SEEK_SET)

    return eventMarkers
