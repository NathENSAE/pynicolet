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
        # Truncate long lists for display
        if isinstance(value, list) and len(value) > 5:
            value = value[:5] + ["..."]
        print(f"{key}: {value}")
        
    data = reader.read_data(chIdx=[1])
    print(f"\nData shape: {data.shape}")
    
    plot_downsampled(data.flatten())


if __name__ == "__main__":
    main()