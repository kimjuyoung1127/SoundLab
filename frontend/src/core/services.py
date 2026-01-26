import psutil
import os
import time
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
import streamlit as st
from src.core.analysis import process_signal_heavy, detect_anomalies_light

# --- Service Layer ---
# This layer provides a 1:1 mapping for UI components to fetch their data.
# It encompasses business logic, system metrics, and calls to core analysis algorithms.

def get_dashboard_metrics(heavy_proc_time_ms: int, anomaly_count: int) -> Dict[str, Any]:
    """
    Retrieves data for the dashboard metrics component.
    Combines system stats (memory) with application state (processing time, count).
    
    Returns:
        Dict matching keys expected by render_metrics
    """
    # 1. System Metrics (Real-time)
    process = psutil.Process(os.getpid())
    mem_usage = process.memory_info().rss / 1024 / 1024 # MB

    # 2. Construct Data Object
    return {
        "memory_usage_mb": mem_usage,
        "algo_time_ms": heavy_proc_time_ms,
        "anomalies_count": anomaly_count
    }

def perform_heavy_analysis(uploaded_file, target_freq: float, bandwidth: float, smart_mode: bool = True) -> Tuple[np.ndarray, np.ndarray, float, Dict[str, Any]]:
    """
    Service wrapper for heavy signal processing.
    Returns: timestamps, magnitudes, execution_time_ms, analysis_info
    """
    start_time = time.time()
    # Updated to receive 3 values from process_signal_heavy
    timestamps, magnitudes, analysis_info = process_signal_heavy(uploaded_file, target_freq, bandwidth, smart_mode)
    duration_ms = (time.time() - start_time) * 1000
    return timestamps, magnitudes, duration_ms, analysis_info

def perform_light_analysis(timestamps: np.ndarray, magnitudes: np.ndarray, otsu_multiplier: float, manual_thresh: Optional[float]) -> Tuple[Any, float, List[Dict]]:
    """
    Service wrapper for light analysis (thresholding).
    """
    return detect_anomalies_light(timestamps, magnitudes, otsu_multiplier, manual_thresh)
