import numpy as np
import streamlit as st
from typing import Tuple, List, Dict, Any, Optional
from src.core.magi import robust_goertzel_magi
from src.config import DEFAULT_WINDOW_SIZE_SEC
from skimage.filters import threshold_otsu
from src.core.audio import load_audio

# --- 레벨 1: 무거운 연산 (신호 처리) ---
# 내부 Goertzel 결과를 캐시하여 파일이 변경되지 않는 한 재계산을 방지합니다.
# 최적화됨: Streamlit이 참조/ID로 스마트하게 해싱하는 uploaded_file 객체를 전달합니다.
@st.cache_data(show_spinner="신호 처리 중 (Heavy)...")
def process_signal_heavy(uploaded_file: Any, target_freq: float, bandwidth: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    신호를 윈도우로 분할하고 각 윈도우에 MAGI 알고리즘을 적용합니다.
    반환값:
        timestamps (np.ndarray): 초 단위의 시간 포인트 배열.
        magnitudes (np.ndarray): 크기(magnitude) 값 배열.
    """
    # 대형 numpy 배열을 캐시 로직에 전달하는 것을 피하기 위해 내부적으로 오디오 로드
    sample_rate, signal = load_audio(uploaded_file)
    
    window_samples = int(DEFAULT_WINDOW_SIZE_SEC * sample_rate)
    step_samples = window_samples // 2 # 부드러움을 위해 50% 중첩
    
    # 신호가 모노인지 확인
    if len(signal.shape) > 1:
        signal = signal.mean(axis=1) # 단순 모노 믹스
        
    n_samples = len(signal)
    
    magnitudes = []
    timestamps = []
    
    # 단순 슬라이딩 윈도우
    for start in range(0, n_samples - window_samples, step_samples):
        end = start + window_samples
        chunk = signal[start:end]
        
        # Hanning 윈도우 적용
        window = np.hanning(len(chunk))
        chunk_windowed = chunk * window
        
        mag = robust_goertzel_magi(chunk_windowed, sample_rate, target_freq, bandwidth)
        magnitudes.append(mag)
        timestamps.append(start / sample_rate)
        
    return np.array(timestamps), np.array(magnitudes)

# --- 레벨 2: 가벼운 연산 (판단 로직) ---
# 슬라이더가 변경될 때 빠르게 재실행됩니다.
@st.cache_data(show_spinner="임계값 적용 중 (Light)...")
def detect_anomalies_light(timestamps: np.ndarray, magnitudes: np.ndarray, otsu_multiplier: float, manual_threshold: Optional[float] = None) -> Tuple[np.ndarray, float, List[Dict[str, float]]]:
    """
    Otsu 임계값과 승수를 적용하여 이상징후를 감지합니다.
    반환값:
        anomalies (np.ndarray): 이상징후 불리언 마스크.
        final_thresh (float): 계산된 임계값.
        results (List[Dict]): UI용 이상징후 세부 정보 리스트.
    """
    if len(magnitudes) == 0:
        return np.array([]), 0.0, []

    if manual_threshold is not None:
        final_thresh = manual_threshold
    else:
        try:
            otsu_val = threshold_otsu(magnitudes)
        except:
             otsu_val = 0.0 # 빈 데이터 또는 균일한 데이터 처리
        final_thresh = otsu_val * otsu_multiplier
    
    anomalies = magnitudes > final_thresh
    
    # UI용 결과 포맷팅
    results = []
    for t, mag, is_anomaly in zip(timestamps, magnitudes, anomalies):
        if is_anomaly:
            results.append({
                "timestamp": t,
                "magnitude": mag,
                "threshold": final_thresh
            })
            
    return anomalies, final_thresh, results
