import streamlit as st
import pandas as pd
from src.ui.styles import inject_custom_css
from src.ui.plots import plot_analysis_results
from src.ui.components import render_header, render_metrics
from src.ui.timeline import render_timeline_section
from src.config import DEFAULT_TARGET_FREQ, DEFAULT_OTSU_MULTIPLIER, DEFAULT_BANDWIDTH
import src.core.services as services

def render_app():
    # 1. Setup
    st.set_page_config(page_title="SignalCraft Light-Lab", layout="wide", page_icon="📡")
    inject_custom_css()
    
    # 2. Sidebar Controls
    with st.sidebar:
        render_header()
        
        # --- Info / Help Section ---
        with st.expander("ℹ️ 앱 사용 가이드", expanded=False):
            st.markdown("""
            **1. 파일 업로드**: 분석할 WAV 파일을 드래그앤드롭 하세요.
            **2. 타겟 주파수**: 감지하고 싶은 특정 주파수(Hz)를 설정합니다. (예: 전력 노이즈 60Hz)
            **3. 대역폭**: 타겟 주파수 주변을 얼마나 넓게 볼지 설정합니다.
            **4. 민감도**: 이상징후를 얼마나 엄격하게 판정할지 정합니다. (낮을수록 민감)
            """)
        
        st.subheader("📁 분석 대상 파일")
        uploaded_file = st.file_uploader(
            "WAV 파일을 업로드하세요", 
            type=["wav"], 
            help="분석할 오디오 파일(.wav)을 선택해주세요. 대용량 파일도 지원합니다."
        )
        
        st.subheader("🎛️ 알고리즘 정밀 튜닝")
        target_freq = st.number_input(
            "타겟 주파수 (Hz)", 
            value=DEFAULT_TARGET_FREQ, 
            step=10.0, 
            help="감지하고자 하는 목표 주파수입니다. (예: 60Hz 전원 노이즈)"
        )
        bandwidth = st.slider(
            "대역폭 (Hz)", 
            0.5, 5.0, DEFAULT_BANDWIDTH, 
            help="설정한 주파수 앞뒤로 어느 정도 범위까지 포함할지 결정합니다. 값이 클수록 더 넓은 범위를 감지합니다."
        )
        otsu_multiplier = st.slider(
            "민감도 (Otsu 계수)", 
            0.5, 3.0, DEFAULT_OTSU_MULTIPLIER, 0.1, 
            help="값이 낮을수록 작은 신호 변화도 '이상징후'로 감지합니다. (0.5=매우 민감, 3.0=둔감)"
        )
        
        st.subheader("🔧 수동 제어")
        # Smart Analysis Toggle (New Feature based on feedback)
        smart_mode = st.toggle("🧠 스마트 분석 모드 (권장)", value=True, help="기계 가동(On) 구간 자동 감지, 대역폭지능형 튜닝, 상대 단위(%) 변환을 수행합니다.")
        
        manual_mode = st.checkbox(
            "고정 임계값(Hard Threshold) 사용",
            help="자동 감지(Otsu 알고리즘) 대신, 사용자가 직접 정한 기준값으로 이상 여부를 판단합니다."
        )
        manual_thresh = None
        if manual_mode:
            manual_thresh = st.slider(
                "임계값 직접 설정", 
                0.0, 10000.0, 100.0,
                help="이 값보다 큰 신호는 모두 이상징후로 표시됩니다."
            )

    # 3. Main Analysis Flow
    if uploaded_file:
        
        # Heavy Step (Cached via Service)
        with st.spinner("🔄 신호 분석 및 데이터 처리 중... (초기 로딩)"):
            timestamps, magnitudes, heavy_proc_time, analysis_info = services.perform_heavy_analysis(
                uploaded_file, target_freq, bandwidth, smart_mode
            )
            
        # Display Smart Analysis Info
        if smart_mode:
            with st.expander("📊 스마트 분석 결과", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("감지된 대역폭 (Bandwidth)", f"{analysis_info['detected_bandwidth']:.2f} Hz", delta="Auto-Tuned")
                with col2:
                    st.metric("가동 기준 (Silence Thresh)", f"{analysis_info['active_threshold']:.2f}", help="이 값 미만의 신호는 'Off' 상태로 간주하여 무시했습니다.")
            
            # New Timeline View
            render_timeline_section(analysis_info)
        
        # Light Step (Cached via Service)
        anomalies_mask, final_thresh, anomaly_list = services.perform_light_analysis(
            timestamps, magnitudes, otsu_multiplier, manual_thresh
        )
        
        # 4. Rendering
        
        # Top Metrics
        metrics_data = services.get_dashboard_metrics(heavy_proc_time, len(anomaly_list))
        render_metrics(metrics_data)
        
        # Main Plot (Placeholder for late rendering)
        plot_placeholder = st.empty()
        
        # Audio Player with Region Slicing (Basic implementation for Ph1)
        st.subheader("🎧 오디오 재생 및 구간 확인")
        st.audio(uploaded_file)
        
        # Logs & Interaction
        highlight_timestamps = []
        
        if anomaly_list:
            st.subheader("📋 이상징후 탐지 로그 (클릭하여 차트 강조)")
            st.caption("💡 Shift(범위) 또는 Ctrl(개별) 키를 누른 채 클릭하면 **다중 선택**이 가능합니다.")
            
            df = pd.DataFrame(anomaly_list)
            
            # Formatter for MM:SS
            def format_time(seconds):
                m = int(seconds // 60)
                s = int(seconds % 60)
                return f"{m:02d}:{s:02d}"

            # Apply formatting for display (Keep original for logic if needed, but here we just display)
            # We add a display column
            df["발생 시각"] = df["timestamp"].apply(format_time)
            
            # Select and Rename columns for display
            display_df = df[["발생 시각", "magnitude", "threshold"]].copy()
            display_df.columns = ["발생 시각 (MM:SS)", "신호 강도 (%)", "가동 임계값 (%)"]
            
            # Interactive Dataframe (Multi-Select Enabled)
            event = st.dataframe(
                display_df, 
                use_container_width=True,
                on_select="rerun",
                selection_mode="multi-row",
                hide_index=True
            )
            
            # Capture selection (List of timestamps)
            if event.selection.rows:
                st.caption(f"✅ {len(event.selection.rows)}개 항목 선택됨")
                for idx in event.selection.rows:
                    # Map back to original timestamp using index
                    # Note: display_df and df have same index
                    ts = df.iloc[idx]["timestamp"]
                    highlight_timestamps.append(ts)
        
        # Render Plot into Placeholder (Multi-Highlight)
        with plot_placeholder:
            st.plotly_chart(
                plot_analysis_results(
                    timestamps, 
                    magnitudes, 
                    final_thresh, 
                    anomalies_mask, 
                    highlight_timestamps=highlight_timestamps
                ), 
                use_container_width=True
            )

    else:
        # Empty state with visual cue
        st.info("👈 왼쪽 사이드바에서 WAV 파일을 업로드하여 분석을 시작하세요.")

