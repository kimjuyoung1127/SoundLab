import streamlit as st
import pandas as pd
from src.ui.styles import inject_custom_css
from src.ui.plots import plot_analysis_results
from src.ui.components import render_header, render_metrics
from src.config import DEFAULT_TARGET_FREQ, DEFAULT_OTSU_MULTIPLIER, DEFAULT_BANDWIDTH
import src.core.services as services

def render_app():
    # 1. Setup
    st.set_page_config(page_title="SignalCraft Light-Lab", layout="wide", page_icon="📡")
    inject_custom_css()
    
    # 2. Sidebar Controls
    with st.sidebar:
        render_header()
        
        st.subheader("📁 분석 대상 파일")
        uploaded_file = st.file_uploader("WAV 파일을 업로드하세요", type=["wav"])
        
        st.subheader("🎛️ 알고리즘 정밀 튜닝")
        target_freq = st.number_input("타겟 주파수 (Hz)", value=DEFAULT_TARGET_FREQ, step=10.0, help="감지하고자 하는 목표 주파수입니다.")
        bandwidth = st.slider("대역폭 (Hz)", 0.5, 5.0, DEFAULT_BANDWIDTH, help="주파수 감지 범위의 여유폭을 설정합니다.")
        otsu_multiplier = st.slider("민감도 (Otsu 계수)", 0.5, 3.0, DEFAULT_OTSU_MULTIPLIER, 0.1, help="값이 낮을수록 더 민감하게 이상을 감지합니다.")
        
        st.subheader("🔧 수동 제어")
        manual_mode = st.checkbox("고정 임계값(Hard Threshold) 사용")
        manual_thresh = None
        if manual_mode:
            manual_thresh = st.slider("임계값 직접 설정", 0.0, 10000.0, 100.0)

    # 3. Main Analysis Flow
    if uploaded_file:
        
        # Heavy Step (Cached via Service)
        with st.spinner("🔄 신호 분석 및 데이터 처리 중... (초기 로딩)"):
            timestamps, magnitudes, heavy_proc_time = services.perform_heavy_analysis(
                uploaded_file, target_freq, bandwidth
            )
        
        # Light Step (Cached via Service)
        anomalies_mask, final_thresh, anomaly_list = services.perform_light_analysis(
            timestamps, magnitudes, otsu_multiplier, manual_thresh
        )
        
        # 4. Rendering
        
        # Top Metrics (1:1 Mapping: get_dashboard_metrics -> render_metrics)
        metrics_data = services.get_dashboard_metrics(heavy_proc_time, len(anomaly_list))
        render_metrics(metrics_data)
        
        # Main Plot
        st.plotly_chart(
            plot_analysis_results(timestamps, magnitudes, final_thresh, anomalies_mask), 
            use_container_width=True
        )
        
        # Audio Player with Region Slicing (Basic implementation for Ph1)
        st.subheader("🎧 오디오 재생 및 구간 확인")
        # In Ph2 we will add slicing logic here. For now standard player.
        st.audio(uploaded_file)
        
        # Logs
        if anomaly_list:
            st.subheader("📋 이상징후 탐지 로그")
            df = pd.DataFrame(anomaly_list)
            # Rename columns for display
            df.columns = ["시간 (초)", "크기 (Magnitude)", "임계값 (Threshold)"]
            st.dataframe(df, use_container_width=True)
            
    else:
        # Empty state with visual cue
        st.info("👈 왼쪽 사이드바에서 WAV 파일을 업로드하여 분석을 시작하세요.")

