import numpy as np
from numba import jit


@jit(nopython=True, cache=True)
def robust_goertzel_magi(samples, sample_rate, target_freq, bandwidth=1.0):
    """
    Robust Goertzel algorithm considering Frequency Drift.
    Extracts max energy within target_freq +/- bandwidth.
    """
    n_range = len(samples)
    max_magnitude = 0.0
    
    # Scan frequencies: target - bandwidth, target, target + bandwidth
    # Scanning at 0.5Hz steps for precision if needed, but for now 3 points as per PRD
    scan_freqs = np.array([target_freq - bandwidth, target_freq, target_freq + bandwidth])
    
    for f in scan_freqs:
        k = int(0.5 + (n_range * f) / sample_rate)
        w = (2 * np.pi / n_range) * k
        cosine = np.cos(w)
        sine = np.sin(w)
        coeff = 2 * cosine
        
        q1 = 0.0
        q2 = 0.0
        
        for i in range(n_range):
            # Applying Hanning Window logic implicitly or explicitly.
            # Here assuming samples are already windowed or raw.
            # If we need internal windowing for efficiency:
            # val = samples[i] * (0.5 - 0.5 * np.cos(2 * np.pi * i / (n_range - 1)))
            val = samples[i] 
            q0 = coeff * q1 - q2 + val
            q2 = q1
            q1 = q0
            
        real = (q1 - q2 * cosine)
        imag = (q2 * sine)
        mag = np.sqrt(real*real + imag*imag)
        
        if mag > max_magnitude:
            max_magnitude = mag
            
    return max_magnitude
