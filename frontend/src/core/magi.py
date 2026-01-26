import numpy as np
from numba import jit

@jit(nopython=True, cache=True)
def robust_goertzel_magi(samples: np.ndarray, sample_rate: int, target_freq: float, bandwidth: float = 1.0) -> float:
    """
    주파수 드리프트를 고려한 강력한 Goertzel 알고리즘.
    target_freq +/- 대역폭(bandwidth) 내에서 최대 에너지를 추출합니다.
    """
    n_range = len(samples)
    max_magnitude = 0.0
    
    # 주파수 스캔: 목표 - 대역폭, 목표, 목표 + 대역폭
    # 필요하다면 정밀도를 위해 0.5Hz 단위로 스캔할 수 있지만, PRD에 따라 지금은 3포인트 스캔
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
            # Hanning 윈도우 로직을 암시적 또는 명시적으로 적용.
            # 여기서는 샘플이 이미 윈도우 처리되었거나 원본이라고 가정.
            # 효율성을 위해 내부 윈도우 처리가 필요한 경우:
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

@jit(nopython=True, cache=True)
def calculate_band_energy(samples: np.ndarray, sample_rate: int, center_freq: float, bandwidth: float, step: float = 0.5) -> float:
    """
    특정 대역폭 내의 주파수 에너지를 합산합니다 (V5.7 로직).
    center_freq +/- bandwidth 범위 내에서 step 단위로 에너지를 계산하여 합산.
    """
    n_range = len(samples)
    total_energy = 0.0
    
    # JS: for (let f = startF; f <= endF; f += 0.5)
    start_f = center_freq - bandwidth
    end_f = center_freq + bandwidth
    
    # Floating point loop manually
    current_f = start_f
    while current_f <= end_f + 1e-9:
        # Single Frequency Magnitude (correlation)
        # JS Logic: getMagnitude with step+=8 (Fast scan)
        # We can implement full correlation or strided.
        # Let's do full correlation for accuracy or stride to match JS speed?
        # JS "step+=8" reduces samples by 8x. 
        # Python Numba is fast, let's try stride=1 first (full accuracy).
        # If too slow, we can increase stride.
        
        omega = (2 * np.pi * current_f) / sample_rate
        
        real = 0.0
        imag = 0.0
        
        # Vectorized internal loop is harder in manual loop in numba?
        # No, explicit loop is fast in numba.
        # To match JS "Fast Scan" (step=8), let's use stride 8 if desired, 
        # but for reliability let's use stride 4 or 1. 220k samples is manageable.
        # User JS uses step 8.
        
        stride = 8 
        for j in range(0, n_range, stride):
            angle = omega * j
            val = samples[j]
            real += val * np.cos(angle)
            imag += val * np.sin(angle)
            
        mag = np.sqrt(real*real + imag*imag) / (n_range / stride / 2) # Normalization (approx)
        total_energy += mag
        
        current_f += step
        
    return total_energy

