import numpy as np
import streamlit as st
from typing import Tuple, List, Dict, Any, Optional
from src.core.magi import robust_goertzel_magi, calculate_band_energy
from src.config import DEFAULT_WINDOW_SIZE_SEC
from skimage.filters import threshold_otsu
from src.core.audio import load_audio

# --- V5.7 Configuration ---
CHUNK_DURATION_SEC = 5.0
CONF_ID = {'freq': 535.0, 'bw': 10.0, 'gap_min': 2.0, 'min_dur_min': 1.0} # Gap & MinDur in Minutes
CONF_SURGE_60 = {'freq': 60.0, 'bw': 2.0}
CONF_SURGE_120 = {'freq': 120.0, 'bw': 2.0}
CONF_DIAG = {'freq': 180.0, 'bw': 2.0}

@st.cache_data(show_spinner="Smart Analyzer V5.7 분석 중...")
def process_signal_heavy(uploaded_file: Any, target_freq: float, bandwidth: float, smart_mode: bool = True) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    SMART UNIVERSAL ANALYZER V5.7 (SAFE TRIMMING) Implementation.
    """
    # 1. Load File
    sample_rate, signal = load_audio(uploaded_file)
    
    # Mono Conversion
    if len(signal.shape) > 1:
        signal = signal.mean(axis=1)

    # Convert settings
    # User might want to override CONF_ID freq with their target_freq input
    # If target_freq is significantly different from default 60Hz (e.g., user set 535 manually), use it.
    # OR strictly follow V5.7 spec (535Hz).
    # Generically, we use target_freq if provided, else 535.
    # However, standard V5.7 is hardcoded to 535. 
    # Let's use target_freq as the "ID" Frequency.
    ID_FREQ = target_freq if target_freq > 0 else CONF_ID['freq']
    ID_BW = bandwidth if bandwidth > 0 else CONF_ID['bw']
    
    chunk_bytes = int(CHUNK_DURATION_SEC * sample_rate)
    n_samples = len(signal)
    num_chunks = n_samples // chunk_bytes
    
    results = []
    
    # --- Step 1: Feature Extraction ---
    # Progress Bar context is managed by Streamlit in the caller usually, but we can print logs or fast loop
    
    energies_id = []
    energies_60 = []
    energies_120 = []
    energies_180 = []
    
    # Normalize signal to -1.0 ~ 1.0 if not already (WAV read might be int)
    # wavfile.read returns int16 usually.
    if signal.dtype != np.float32 and signal.dtype != np.float64:
        if signal.dtype == np.int16:
            signal = signal.astype(np.float32) / 32768.0
        elif signal.dtype == np.uint8:
            signal = (signal.astype(np.float32) - 128) / 128.0

    for i in range(num_chunks):
        start = i * chunk_bytes
        end = start + chunk_bytes
        chunk = signal[start:end]
        
        # Calculate Energies
        e_id = calculate_band_energy(chunk, sample_rate, ID_FREQ, ID_BW)
        e_60 = calculate_band_energy(chunk, sample_rate, CONF_SURGE_60['freq'], CONF_SURGE_60['bw'])
        e_120 = calculate_band_energy(chunk, sample_rate, CONF_SURGE_120['freq'], CONF_SURGE_120['bw'])
        e_180 = calculate_band_energy(chunk, sample_rate, CONF_DIAG['freq'], CONF_DIAG['bw'])
        
        energies_id.append(e_id)
        energies_60.append(e_60)
        energies_120.append(e_120)
        energies_180.append(e_180)
        
        results.append({
            'id': i,
            'time_min': (i * CHUNK_DURATION_SEC) / 60.0,
            'time_sec': i * CHUNK_DURATION_SEC,
            'state': 'OFF',
            'note': '',
            'diag': 'NORMAL'
        })

    energies_id = np.array(energies_id)
    energies_60 = np.array(energies_60)
    energies_120 = np.array(energies_120)
    
    # --- Step 2: Threshold Calculation (Otsu) ---
    try:
        otsu_val = threshold_otsu(energies_id)
    except:
        otsu_val = 0.0 # Fallback if uniform
        
    THRESHOLD_ID = otsu_val * 1.5
    
    # Surge Thresholds
    median_60 = np.median(energies_60) if len(energies_60) > 0 else 0
    median_120 = np.median(energies_120) if len(energies_120) > 0 else 0
    
    SURGE_THRES_60 = median_60 * 2.0
    SURGE_THRES_120 = median_120 * 2.0
    
    # --- Step 3: Logic Application (State Machine) ---
    current_state = 'OFF'
    
    for i, r in enumerate(results):
        val_id = energies_id[i]
        val_60 = energies_60[i]
        val_120 = energies_120[i]
        
        is_id_active = val_id > THRESHOLD_ID
        is_surge = (val_60 > SURGE_THRES_60) and (val_120 > SURGE_THRES_120)
        
        if current_state == 'OFF':
            if is_id_active:
                current_state = 'ON'
                r['state'] = 'ON'
                r['note'] = 'ID_Wide_Start'
            elif is_surge:
                current_state = 'ON'
                r['state'] = 'ON'
                r['note'] = 'Startup_Surge_Start'
            else:
                r['state'] = 'OFF'
        else:
            # Current ON
            if is_id_active:
                r['state'] = 'ON' # Sustain
                r['note'] = 'ID_Wide_Sustain'
            else:
                if val_id < THRESHOLD_ID * 0.8:
                    current_state = 'OFF'
                    r['state'] = 'OFF'
                else:
                    r['state'] = 'ON' # Hysteresis Sustain
                    r['note'] = 'Hysteresis_Sustain'

    # --- Step 4: Post-Processing 1 (Gap Filling) ---
    last_on = -1
    for i, r in enumerate(results):
        if r['state'] == 'ON':
            if last_on != -1:
                gap_min = r['time_min'] - results[last_on]['time_min'] - (CHUNK_DURATION_SEC/60.0)
                if 0 < gap_min <= CONF_ID['gap_min']:
                    # Fill Gap
                    for k in range(last_on + 1, i):
                        results[k]['state'] = 'ON'
                        results[k]['note'] = 'Gap_Filled'
            last_on = i
            
    # --- Step 5: Post-Processing 2 (Smart Trimming - SAFE MODE) ---
    if smart_mode:
        seg_start = -1
        for i in range(len(results)):
            r = results[i]
            if r['state'] == 'ON':
                if seg_start == -1: seg_start = i
                
                # Safety Buffer: Ignore first 1 minute (12 chunks)
                # 1 min / 5 sec = 12 chunks
                chunks_1min = int(60 / CHUNK_DURATION_SEC)
                
                if i > seg_start + chunks_1min:
                    prev_val = energies_id[i-1]
                    curr_val = energies_id[i]
                    
                    ratio = (curr_val / prev_val) if prev_val > 0 else 1.0
                    
                    # Stricter Cutoff
                    if ratio < 0.5 and curr_val < THRESHOLD_ID * 0.5:
                        # Cut remaining
                        for k in range(i, len(results)):
                            if results[k]['state'] == 'OFF': break
                            results[k]['state'] = 'OFF'
                            results[k]['note'] = 'Trimmed_DropOff'
                        seg_start = -1 # Reset segment
            else:
                seg_start = -1

    # --- Step 6: Post-Processing 3 (Noise Removal) ---
    on_start = -1
    for i, r in enumerate(results):
        if r['state'] == 'ON':
            if on_start == -1: on_start = i
        else:
            if on_start != -1:
                duration_min = r['time_min'] - results[on_start]['time_min']
                if duration_min < CONF_ID['min_dur_min']:
                    # Remove Noise
                    for k in range(on_start, i):
                        results[k]['state'] = 'OFF'
                        results[k]['note'] = 'Noise_Removed'
                on_start = -1
                
    # Check last segment
    if on_start != -1:
        duration_min = results[-1]['time_min'] - results[on_start]['time_min']
        if duration_min < CONF_ID['min_dur_min']:
            for k in range(on_start, len(results)):
                results[k]['state'] = 'OFF'
                results[k]['note'] = 'Noise_Removed'

    # --- Step 7: Final Formatting for UI ---
    # UI expects (timestamps, magnitudes, info)
    
    # We will use the 'energies_id' as the main magnitude to show
    # But UI usually expects "Anomalies" to be calculated in 'light' step.
    # To integrate with existing UI, we return the calculated energies.
    # The 'state' info is lost if we just return floats.
    # But we can pass the Threshold in 'info' so Light Analysis can use it.
    
    # Actually, we should map the raw 5s chunks back to a timestamps array
    final_timestamps = np.array([r['time_sec'] for r in results])
    final_magnitudes = energies_id # Already array
    
    # We can also inject the specific "ON" state as a mask into info?
    # Or we can return 'magnitudes' processed such that OFF is 0?
    # User's JS Summary: "ON: ... - ..."
    # If we zero out OFF sections, the chart will show the trimming result visually.
    
    final_magnitudes_processed = np.copy(final_magnitudes)
    for i, r in enumerate(results):
        if r['state'] == 'OFF':
            final_magnitudes_processed[i] = 0.0 # Or low value? 0.0 effectively hides it in linear plot logic if we want.
            
    # Normalize for UI (0-100%)
    if len(final_magnitudes_processed) > 0 and final_magnitudes_processed.max() > 0:
         # Normalize based on original max to keep scale
         final_magnitudes_processed = (final_magnitudes_processed / energies_id.max()) * 100.0
         
    # Info update
    analysis_info = {
        "active_threshold": THRESHOLD_ID,
        "detected_bandwidth": ID_BW,
        "smart_mode": smart_mode,
        "v5_results": results, # Store full results for advanced usage
        "otsu_val": otsu_val
    }
    
    return final_timestamps, final_magnitudes_processed, analysis_info

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
