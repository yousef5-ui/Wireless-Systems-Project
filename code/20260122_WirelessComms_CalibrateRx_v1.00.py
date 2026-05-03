"""
Wireless Systems Project - Receiver Calibration Tool

This script connects to the ESP receiver, configures the transmitter
frequencies, collects RSSI samples and applies Kalman filtering to produce
stable reference power values for each transmitter.

The file is version controlled in GitHub so that improvements to the
calibration process can be documented, reviewed and tracked.
"""
import requests
import time
import numpy as np

# ==========================================
#  1. CONFIGURATION
# ==========================================
ESP_IP = "http://192.168.4.1" 

# Define your transmitters here
TRANSMITTERS = {
    "TX_FL": {"freq": 870.5},
    "TX_FR": {"freq": 872.5},
    "TX_BL": {"freq": 868.0},
    "TX_BR": {"freq": 865.5},
}

# ==========================================
#  2. KALMAN FILTER CLASS
# ==========================================
class KalmanFilter:
    """Simple Kalman filter used to smooth RSSI readings during calibration."""
    def __init__(self, process_noise=0.01, measurement_noise=20.0, est_error=1.0, initial_value=-50):
        """Initialise the filter constants and starting RSSI estimate."""
        self.q = process_noise      
        self.r = measurement_noise  
        self.p = est_error          
        self.x = initial_value      

    def update(self, measurement):
        """Update the RSSI estimate using the latest measurement."""
        self.p = self.p + self.q
        k = self.p / (self.p + self.r)
        self.x = self.x + k * (measurement - self.x)
        self.p = (1 - k) * self.p
        return self.x

# ==========================================
#  3. HELPER FUNCTIONS
# ==========================================
def configure_sensor():
    """Send transmitter IDs and frequency settings to the ESP receiver."""
    print(f"Connecting to Sensor at {ESP_IP}...")
    payload = {"transmitters": []}
    for t_id, info in TRANSMITTERS.items():
        payload["transmitters"].append({"id": t_id, "freq": info["freq"]})
    
    try:
        r = requests.post(f"{ESP_IP}/config", json=payload, timeout=5)
        if r.status_code == 200:
            print(f"✅ Sensor Configured. Scanning {len(TRANSMITTERS)} channels.")
        else:
            print(f"⚠️ Config Error: {r.text}")
    except:
        print(f"❌ Connection Failed. Connect laptop to 'NavGrid_Field' WiFi.")
        exit()

def get_rssi(target_id):
    """Request the latest RSSI value for a selected transmitter."""
    try:
        r = requests.get(f"{ESP_IP}/data", timeout=0.5)
        data = r.json()
        return data.get(target_id)
    except:
        return None

# ==========================================
#  4. CALIBRATION ROUTINE
# ==========================================
def calibrate_transmitter(tx_id):
    """Collect RSSI samples and calculate a filtered reference power value."""
    freq = TRANSMITTERS[tx_id]['freq']
    print(f"\n\n=== CALIBRATING: {tx_id} ({freq} MHz) ===")
    print(f"1. Place Receiver EXACTLY 1.0m away.")
    input("   Press Enter to start sampling...")

    # Initialize Filter
    kf = KalmanFilter(initial_value=-30.0)
    
    raw_readings = []
    filtered_val = -30.0
    
    # Take 50 samples
    samples_target = 50
    
    print(f"   {'Sample':<8} | {'Raw RSSI':<10} | {'Filtered (Stable)':<15}")
    print("   " + "-"*40)
    
    while len(raw_readings) < samples_target:
        val = get_rssi(tx_id)
        
        # Valid range check (-20 to -95)
        if val is not None and val > -65 and val < -20:
            
            # 1. Update Kalman Filter
            filtered_val = kf.update(val)
            
            # 2. Store Raw for comparison
            raw_readings.append(val)
            
            # 3. Live Print
            print(f"   {len(raw_readings)}/{samples_target:<4} | {val:<10} | {filtered_val:.2f}", end='\r')
        
        time.sleep(0.1)

    # Final Statistics
    raw_std = np.std(raw_readings)
    raw_mean = np.mean(raw_readings)
    
    print(f"\n   " + "-"*40)
    print(f"   ✅ CALIBRATION COMPLETE")
    print(f"   Raw Variance (Jitter): +/- {raw_std:.2f} dB")
    
    if raw_std > 4.0:
        print(f"   ⚠️  HIGH JITTER DETECTED! (Normal is < 2.0 dB)")
        print(f"       Possible multipath or interference at {freq}MHz.")
        print(f"       Using the Kalman filtered value is highly recommended.")
    
    print(f"   Final Ref Power: {filtered_val:.2f}")
    return filtered_val

# ==========================================
#  5. MAIN MENU
# ==========================================
if __name__ == "__main__":
    configure_sensor()
    time.sleep(1) 
    
    results = {}
    
    for tx_id in TRANSMITTERS:
        choice = input(f"\nCalibrate {tx_id}? (y/n): ")
        if choice.lower().startswith('y'):
            ref_val = calibrate_transmitter(tx_id)
            results[tx_id] = round(ref_val, 1)
        else:
             # Default if skipped
            results[tx_id] = -30.0

    print("\n\n=== PASTE THIS INTO YOUR APP ===")
    print("TRANSMITTERS = {")
    for tx_id, info in TRANSMITTERS.items():
        final_ref = results.get(tx_id)
        print(f'    "{tx_id}": {{ "freq": {info["freq"]}, "pos": [0.0, 0.0], "ref_power": {final_ref} }},')
    print("}")
