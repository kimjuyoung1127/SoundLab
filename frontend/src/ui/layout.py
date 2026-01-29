import streamlit as st
import pandas as pd
from src.ui.styles import inject_custom_css
from src.ui.plots import plot_analysis_results
from src.ui.components import render_header, render_metrics
from src.ui.timeline import render_timeline_section
from src.ui.analyzer import render_frequency_explorer, show_spectral_analysis_dialog
from src.config import DEFAULT_TARGET_FREQ, DEFAULT_OTSU_MULTIPLIER, DEFAULT_BANDWIDTH
import src.core.services as services

def render_app():
    # 1. Setup
    st.set_page_config(page_title="SignalCraft Lab", layout="wide", page_icon="📡")
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

        # File Change Detection (Reset Trigger)
        if uploaded_file:
            current_file_name = uploaded_file.name
            last_file_name = st.session_state.get("last_uploaded_file")
            if current_file_name != last_file_name:
                st.session_state["analysis_triggered"] = False
                st.session_state["last_uploaded_file"] = current_file_name
                st.session_state["show_auto_modal"] = True
        
        # Frequency Explorer Integration
        if uploaded_file:
            render_frequency_explorer(uploaded_file)
        
        st.subheader("🎛️ 분석 설정 (Analysis Settings)")
        
        target_freq = st.number_input(
            "타겟 주파수 (Hz)", 
            value=DEFAULT_TARGET_FREQ, 
            step=10.0, 
            key="target_freq_input",
            help="감지하고자 하는 목표 주파수입니다. (예: 60Hz 전원 노이즈)"
        )
        
        otsu_multiplier = st.slider(
            "민감도 (Sensitivity)", 
            0.5, 3.0, DEFAULT_OTSU_MULTIPLIER, 0.1, 
            help="값이 낮을수록 작은 신호도 '이상징후'로 민감하게 반응합니다. (기본값: 1.5)"
        )
        
        with st.expander("⚙️ 고급 설정", expanded=False):
            # Bandwidth removed (Auto-set to 2.0 internall)
            st.caption("대역폭은 내부적으로 최적화된 값(2.0Hz)을 사용합니다.")
            
            # Smart Analysis Toggle
            smart_mode = st.toggle("🧠 스마트 분석 모드 (권장)", value=True, help="기계 가동(On) 구간 자동 감지 및 지능형 튜닝을 수행합니다.")
            
        st.markdown("---")
        # Start Analysis Button removed from sidebar (Moved to main area)

        # Manual Mode Removed (Hard Threshold deprecatd in favor of Smart V5.7)
        manual_thresh = None

    # 3. Main Analysis Flow
    if uploaded_file:
        # Auto-open Modal if flag is set
        if st.session_state.get("show_auto_modal", False):
            st.session_state["show_auto_modal"] = False
            show_spectral_analysis_dialog(uploaded_file)
            
        # Reset toggle if file changed (naive check, or just rely on user)
        # We rely on session_state "analysis_triggered"
        
        if st.session_state.get("analysis_triggered", False):
            # Heavy Step (Cached via Service)
            with st.spinner("🔄 신호 분석 및 데이터 처리 중..."):
                timestamps, magnitudes, heavy_proc_time, analysis_info = services.perform_heavy_analysis(
                    uploaded_file, target_freq, DEFAULT_BANDWIDTH, smart_mode
                )
                
            # Display Smart Analysis Info
            if smart_mode:
                with st.expander("📊 스마트 분석 결과", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("감지된 대역폭 (Bandwidth)", f"{analysis_info['detected_bandwidth']:.2f} Hz", delta="Auto-Fixed")
                    with col2:
                        st.metric("가동 판정 기준 (Operation Threshold)", f"{analysis_info.get('threshold_pct', 0.0):.1f} %", help="최대 신호 대비 상대적 비율입니다. 이 값 미만의 에너지는 'OFF' 상태로 간주합니다.")
                
                # New Timeline View
                render_timeline_section(analysis_info)
            
            # Light Step (Cached via Service)
            # Pass v5_results to filter anomalies by "ON" state
            v5_results = analysis_info.get("v5_results")
            anomalies_mask, final_thresh, anomaly_list = services.perform_light_analysis(
                timestamps, magnitudes, otsu_multiplier, manual_thresh, v5_results
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
                st.subheader("⚡ 가동 중 주요 고점(Peak) 이벤트 로그")
                st.caption("💡 기계가 **가동 중(ON)**인 상태에서 발생한 주요 에너지 급증 구간입니다.")
                
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
                display_df.columns = ["발생 시각 (MM:SS)", "신호 레벨 (%)", "가동 임계값 (%)"]
                
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
            st.info("💡 분석 대기 중: 주파수를 확인한 후 아래 버튼을 눌러 정밀 분석을 시작하세요.")
            if st.button("🚀 분석 시작 (Start Analysis)", type="primary", use_container_width=True):
                st.session_state["analysis_triggered"] = True
                st.rerun()

    else:
        # Empty state with visual cue
        st.info("👈 왼쪽 사이드바에서 WAV 파일을 업로드하여 분석을 시작하세요.")

