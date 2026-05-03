"""
Wireless Systems Project - Positioning and Heatmap Dashboard

This script receives RSSI data from the ESP receiver, smooths the readings
using Kalman filtering, predicts the likely receiver position using a heatmap
method, and logs estimated position data for later analysis.

The file is version controlled in GitHub so that changes to the positioning
method, logging system and visualisation can be documented and tracked.
"""
import numpy as np
import matplotlib.pyplot as plt
import requests
import time
import csv
import datetime
from matplotlib.colors import LinearSegmentedColormap

# ==========================================
#  1. CONFIGURATION
# ==========================================
ESP_IP = "http://192.168.4.1" 

# Use the values from your Calibration Tool here!
TRANSMITTERS = {
    "TX_FL": {"freq": 870.5, "pos": [2.81, 0.74], "ref_power": -37.8},
    "TX_FR": {"freq": 872.5, "pos": [8.77, 0.79], "ref_power": -30.6},
    "TX_BL": {"freq": 868.0, "pos": [3.93, 10.97], "ref_power": -25.0},
    "TX_BR": {"freq": 865.5, "pos": [8.94, 10.04], "ref_power": -31.3},
}


OBSTACLES = [
    # Bottom Edge
    ((5.175, 3.275), (5.425, 3.275), 10.0), 
    # Top Edge
    ((5.175, 3.525), (5.425, 3.525), 10.0),
    # Left Edge
    ((5.175, 3.275), (5.175, 3.525), 10.0),
    # Right Edge
    ((5.425, 3.275), (5.425, 3.525), 10.0),
]
ROOM_DIM = (10.88, 10.97)

# ==========================================
#  2. CLASSES (Filter & Logger)
# ==========================================
class KalmanFilter:
    """Simple Kalman filter used to smooth live RSSI readings."""
    def __init__(self, process_noise=0.05, measurement_noise=5.0, est_error=1.0, initial_value=-60):
        """Initialise the filter constants and starting RSSI estimate."""
        self.q = process_noise      
        self.r = measurement_noise  
        self.p = est_error          
        self.x = initial_value      

    def update(self, measurement):
        """Update the filtered RSSI estimate using the latest measurement."""
        self.p = self.p + self.q
        k = self.p / (self.p + self.r) 
        self.x = self.x + k * (measurement - self.x)
        self.p = (1 - k) * self.p
        return self.x

class DataLogger:
    """CSV logger used to record estimated position and RSSI values."""
    def __init__(self, filename="nav_log.csv"):
        """Create a new CSV log file and write the column headers."""
        self.filename = filename
        with open(self.filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            headers = ["Timestamp", "Est_X", "Est_Y"] + list(TRANSMITTERS.keys())
            writer.writerow(headers)
    
    def log(self, x, y, rssi_data):
        """Append the latest estimated position and RSSI readings to the log file."""
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            row = [datetime.datetime.now().strftime("%H:%M:%S"), round(x, 2), round(y, 2)]
            for t_id in TRANSMITTERS:
                row.append(rssi_data.get(t_id, ""))
            writer.writerow(row)

# ==========================================
#  3. MATH ENGINE
# ==========================================
def line_intersection(p1, p2, p3, p4):
    """Check whether two line segments intersect."""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0: return False
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    return 0 <= ua <= 1 and 0 <= ub <= 1

def predict_rssi(rx_pos, tx_pos, ref_power, n=3.5):
    """Predict RSSI at a receiver position using distance loss and obstacle loss."""
    dist = np.linalg.norm(np.array(rx_pos) - np.array(tx_pos))
    if dist < 0.1: dist = 0.1
    rssi = ref_power - (10 * n * np.log10(dist))
    for w1, w2, loss in OBSTACLES:
        if line_intersection(rx_pos, tx_pos, w1, w2):
            rssi -= loss
    return rssi

def generate_heatmap(measurements):
    """Generate a heatmap by comparing measured RSSI values with predicted values."""
    res = 0.20
    xs = np.arange(0, ROOM_DIM[0], res)
    ys = np.arange(0, ROOM_DIM[1], res)
    grid = np.zeros((len(ys), len(xs)))

    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            error_sum = 0
            for tx_id, measured_val in measurements.items():
                if tx_id in TRANSMITTERS and measured_val > -99:
                    tx_info = TRANSMITTERS[tx_id]
                    predicted = predict_rssi((x, y), tx_info["pos"], tx_info["ref_power"])
                    error_sum += (measured_val - predicted) ** 2
            grid[i, j] = np.exp(-error_sum / 80.0) 
            
    return xs, ys, grid

# ==========================================
#  4. MAIN LOOP
# ==========================================
def main():
    """Run the live positioning dashboard and update the heatmap display."""
    # Setup
    filters = {t_id: KalmanFilter() for t_id in TRANSMITTERS}
    logger = DataLogger()
    history_x, history_y = [], []

    # Configure Sensor
    print(f"Connecting to Sensor at {ESP_IP}...")
    try:
        payload = {"transmitters": [{"id": k, "freq": v["freq"]} for k,v in TRANSMITTERS.items()]}
        requests.post(f"{ESP_IP}/config", json=payload, timeout=2)
        print("✅ Sensor Configured.")
    except:
        print("❌ Connect Laptop to WiFi!")
        return

    # Visualization Init
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = LinearSegmentedColormap.from_list("heat", ["#000022", "blue", "cyan", "lime", "yellow", "red"])
    
    # Text placeholder for X/Y Display
    pos_text = ax.text(0.05, 0.95, "", transform=ax.transAxes, color="white", 
                       fontsize=12, fontweight='bold', bbox=dict(facecolor='black', alpha=0.5))

    print("Running...")

    while True:
        try:
            r = requests.get(f"{ESP_IP}/data", timeout=0.2)
            raw_data = r.json()
            
            # Kalman Smoothing
            smoothed = {}
            for t_id, val in raw_data.items():
                if val > -95:
                    smoothed[t_id] = filters[t_id].update(val)
                else:
                    smoothed[t_id] = -100

            # Heatmap & Position
            xs, ys, grid = generate_heatmap(smoothed)
            yi, xi = np.unravel_index(grid.argmax(), grid.shape)
            best_x, best_y = xs[xi], ys[yi]

            # Logging
            logger.log(best_x, best_y, raw_data)
            history_x.append(best_x); history_y.append(best_y)
            if len(history_x) > 30: history_x.pop(0); history_y.pop(0)

            # Drawing
            ax.clear()
            ax.pcolormesh(xs, ys, grid, cmap=cmap, shading='auto')
            
            # Draw Obstacles
            for w1, w2, _ in OBSTACLES:
                ax.plot([w1[0], w2[0]], [w1[1], w2[1]], 'w-', lw=3)

            # Draw Transmitters
            for t_id, info in TRANSMITTERS.items():
                p = info['pos']
                ax.plot(p[0], p[1], 'bs', markeredgecolor='white', markersize=8)
                ax.text(p[0], p[1]+0.3, t_id, color='white', ha='center', fontsize=8)

            # Draw User
            ax.plot(history_x, history_y, 'y.', alpha=0.4)
            ax.plot(best_x, best_y, 'rx', markersize=15, markeredgewidth=3)
            
            # UPDATE THE X/Y TEXT INDICATOR
            ax.text(0.02, 0.95, f"POS: ({best_x:.2f}m, {best_y:.2f}m)", 
                    transform=ax.transAxes, color="lime", fontsize=14, fontweight='bold', 
                    bbox=dict(facecolor='black', alpha=0.7, edgecolor='white'))

            ax.set_xlim(0, ROOM_DIM[0]); ax.set_ylim(0, ROOM_DIM[1])
            plt.pause(0.01)

        except KeyboardInterrupt:
            break
        except Exception as e:
            pass

if __name__ == "__main__":
    main()
