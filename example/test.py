import sys
import time
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
    
    t0 = time.time()
    header = reader.read_header()
    print(f"Header reading and parsing time: {time.time() - t0:.4f} seconds")
    """print("Header Information:")
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
        print(f"{key}: {value}")"""
        
    # Read all channels
    t0 = time.time()
    data = reader.read_data(verbose=True)   
    print(f"Data reading time: {time.time() - t0:.4f} seconds")
    """print(f"\nData shape (pynicolet [samples x channels]): {data.shape}")
    
    events = reader.read_events()
    print(f"Events read via read_events(): Found {len(events)} events")
    if events:
        print(f"  First event: {events[0]}")"""
    
    # Calculate stats for comparison (channel 0 in Python = channel 1 in MATLAB)
    # We use the first channel (index 0) for stats comparison
    print(f"Channel 1 mean: {np.mean(data[:, 0]):.4f}")
    print(f"Channel 1 std:  {np.std(data[:, 0]):.4f}")
    
    plot_downsampled(data[:, 0])


if __name__ == "__main__":
    main()