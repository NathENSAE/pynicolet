import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pynicolet.reader import NicoletReader
import matplotlib.pyplot as plt
import numpy as np

def plot_downsampled(data, max_points=5000):
    if len(data) > max_points:
        idx = np.linspace(0, len(data)-1, max_points).astype(int)
        data_ds = data[idx]
    else:
        data_ds = data
    
    plt.plot(data_ds)
    plt.title("Downsampled signal")
    plt.show()

def main():
    filename = r"./example/EEG_test_data.e"
    reader = NicoletReader(filename)
    
    header = reader.read_header()
    print("Header Information:")
    for key, value in header.items():
        if key == "events" and value:
            print(f"{key}: Found {len(value)} calculated events")
            for i, ev in enumerate(value[:10]):
                print(f"  Event {i}: {ev}")
            if len(value) > 10:
                print("  ...")
            continue
            
        if key == "raw_events" and value:
            print(f"{key}: Found {len(value)} raw binary events")
            continue
            
        if key == "dynamicPackets" and value:
            ids = set(p.get("IDStr") for p in value)
            print(f"dynamicPackets: Found {len(value)} packets. Unique IDs: {ids}")
            continue

        # Truncate long lists for display
        if isinstance(value, list) and len(value) > 5:
            value = value[:5] + ["..."]
        print(f"{key}: {value}")
        
    ch_to_read = 0
    data = reader.read_data(chIdx=[ch_to_read])
    print(f"\nData shape (pynicolet [samples x channels]): {data.shape}")
    
    events = reader.read_events()
    print(f"Events read via read_events(): Found {len(events)} events")
    if events:
        print(f"  First event: {events[0]}")
    
    # Calculate stats for comparison (channel 0 in Python = channel 1 in MATLAB)
    print(f"Channel {ch_to_read + 1} mean: {np.mean(data):.4f}")
    print(f"Channel {ch_to_read + 1} std:  {np.std(data):.4f}")
    
    plot_downsampled(data.flatten()[:5000])


if __name__ == "__main__":
    main()