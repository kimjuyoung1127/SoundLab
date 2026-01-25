import numpy as np
import streamlit as st
from src.core.magi import robust_goertzel_magi
from src.config import DEFAULT_WINDOW_SIZE_SEC
from skimage.filters import threshold_otsu

# --- Level 1: Heavy Computation (Signal Processing) ---
# Caches internal Goertzel results to avoid re-calculating unless file changes
@st.cache_data(show_spinner="Processing Signal (Heavy)...")
def process_signal_heavy(signal, sample_rate, target_freq, bandwidth):
    """
    Splits signal into windows and applies MAGI to each window.
    Returns timepoints and magnitude array.
    """
    window_samples = int(DEFAULT_WINDOW_SIZE_SEC * sample_rate)
    step_samples = window_samples // 2 # 50% overlap for smoothness
    
    # Ensure signal is mono
    if len(signal.shape) > 1:
        signal = signal.mean(axis=1) # Simple mono mix
        
    n_samples = len(signal)
    
    magnitudes = []
    timestamps = []
    
    # Simple sliding window
    for start in range(0, n_samples - window_samples, step_samples):
        end = start + window_samples
        chunk = signal[start:end]
        
        # Apply Hanning window
        window = np.hanning(len(chunk))
        chunk_windowed = chunk * window
        
        mag = robust_goertzel_magi(chunk_windowed, sample_rate, target_freq, bandwidth)
        magnitudes.append(mag)
        timestamps.append(start / sample_rate)
        
    return np.array(timestamps), np.array(magnitudes)

# --- Level 2: Light Computation (Decision Logic) ---
# Re-runs quickly when sliders change
@st.cache_data(show_spinner="Applying Thresholds (Light)...")
def detect_anomalies_light(timestamps, magnitudes, otsu_multiplier, manual_threshold=None):
    """
    Applies Otsu thresholding with multiplier to detect anomalies.
    Returns boolean mask of anomalies and the final threshold value.
    """
    if len(magnitudes) == 0:
        return np.array([]), 0.0

    if manual_threshold is not None:
        final_thresh = manual_threshold
    else:
        try:
            otsu_val = threshold_otsu(magnitudes)
        except:
             otsu_val = 0.0 # Handle empty or uniform data
        final_thresh = otsu_val * otsu_multiplier
    
    anomalies = magnitudes > final_thresh
    
    # Format results for UI
    results = []
    for t, mag, is_anomaly in zip(timestamps, magnitudes, anomalies):
        if is_anomaly:
            results.append({
                "timestamp": t,
                "magnitude": mag,
                "threshold": final_thresh
            })
            
    return anomalies, final_thresh, results
