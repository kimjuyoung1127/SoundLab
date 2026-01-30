
import numpy as np
from src.core.analysis import calculate_otsu_threshold

# --- Stream Processor for JSON Data ---

class StreamProcessor:
    """
    Adapts the V5.7 logic to work with streaming JSON data (82 features)
    instead of raw WAV files.
    """
    
    def __init__(self, history_size=30):
        # Buffer to store historical magnitude values for dynamic thresholding
        self.history_buffer = [] 
        self.history_size = history_size
        self.last_state = "OFF"
    
    def process_features(self, features_json, sensitivity=1.5):
        """
        Process a single JSON record (82 floats).
        Returns: 
            - 60hz_mag (float)
            - 120hz_mag (float)
            - state (str): 'ON' or 'OFF'
            - threshold (float)
            - anomaly_score (float)
        """
        if not features_json or len(features_json) < 82:
            return 0.0, 0.0, "OFF", 0.0, 0.0
            
        # 1. Parse Data (See Latest.md for mapping)
        # 60Hz Band: Indices 0-40 (58.0 - 62.0 Hz)
        # 120Hz Band: Indices 41-81 (116.0 - 124.0 Hz)
        band_60 = features_json[:41]
        band_120 = features_json[41:82]
        
        # 2. Extract Key Metric (Max Magnitude in 60Hz band)
        # We use the PEAK of the 60Hz band as the primary indicator for ON/OFF
        current_mag = np.max(band_60)
        mag_120 = np.max(band_120)
        
        # 3. Update Buffer
        self.history_buffer.append(current_mag)
        if len(self.history_buffer) > self.history_size:
            self.history_buffer.pop(0)
            
        # 4. Calculate Dynamic Threshold (Otsu-lite)
        if len(self.history_buffer) < 5:
             # Not enough data, use fallback
             threshold = 0.5 
        else:
            # We treat the buffer as a mini-histogram
            threshold = calculate_otsu_threshold(np.array(self.history_buffer), sensitivity)
            
        # 5. Determine State (Simple Hysteresis)
        if current_mag > threshold:
            state = "ON"
        else:
            state = "OFF"
            
        # 6. Anomaly Score (How much over threshold?)
        anomaly_score = 0.0
        if state == "ON":
            anomaly_score = (current_mag - threshold) / threshold
            
        return current_mag, mag_120, state, threshold, anomaly_score
