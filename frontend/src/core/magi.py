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
