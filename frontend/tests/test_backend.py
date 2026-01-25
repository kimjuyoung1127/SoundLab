import sys
import os
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.magi import robust_goertzel_magi

def test_magi_pure_sine():
    """
    Verifies that the backend logic (MAGI) detects a pure sine wave correctly.
    """
    print("Testing Backend Logic (MAGI Algorithm)...")
    
    # Generate 1 sec of 60Hz sine wave at 44.1kHz
    fs = 44100
    t = np.linspace(0, 1.0, fs, endpoint=False)
    target_freq = 60.0
    signal = np.sin(2 * np.pi * target_freq * t)
    
    # Run Goertzel (Low level)
    mag = robust_goertzel_magi(signal, fs, target_freq, bandwidth=1.0)
    print(f"Goertzel Magnitude at {target_freq}Hz: {mag:.4f} (Expected > 0)")
    
    assert mag > 1000, "Magnitude matches expected high energy for matched freq"
    
    # Run off-target
    mag_off = robust_goertzel_magi(signal, fs, target_freq=120.0, bandwidth=1.0)
    print(f"Goertzel Magnitude at 120Hz: {mag_off:.4f} (Expected near 0)")
    
    assert mag_off < mag * 0.1, "Off-target magnitude should be low"
    
    print("Backend Verification Passed! ✅")

if __name__ == "__main__":
    test_magi_pure_sine()
