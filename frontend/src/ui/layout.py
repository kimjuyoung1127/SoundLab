import streamlit as st
import pandas as pd
from src.ui.styles import inject_custom_css
from src.ui.plots import plot_analysis_results, plot_live_trend
from src.ui.components import render_header, render_metrics
from src.ui.timeline import render_timeline_section
from src.ui.analyzer import render_frequency_explorer, show_spectral_analysis_dialog
from src.config import (DEFAULT_TARGET_FREQ, DEFAULT_OTSU_MULTIPLIER, DEFAULT_BANDWIDTH, 
                        COLOR_PRIMARY, COLOR_ACCENT_CYAN, COLOR_ANOMALY_RED)
import src.core.services as services
import src.core.services as services
from src.core.supabase_client import fetch_latest_logs, fetch_logs_by_range
from src.core.stream_processor import StreamProcessor
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go

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
        
        # Data Source Toggle
        data_source = st.radio("데이터 소스 (Data Source)", ["📁 파일 업로드 (File)", "📡 실시간 스트림 (Live)"], horizontal=True)
        
        uploaded_file = None
        is_live_mode = "Live" in data_source

        if is_live_mode:
            st.info("📡 ESP32 디바이스에서 실시간 데이터를 수신합니다 (Supabase).")
            # In live mode, we don't need a file uploader
        else:
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
    if is_live_mode:
        st.subheader("📡 실시간 모니터링 (Live Monitor)")
        
        # Initialize Processor in Session State
        if "stream_processor" not in st.session_state:
            st.session_state["stream_processor"] = StreamProcessor()
            
        processor = st.session_state["stream_processor"]
        
        # Dashboard Placeholder
        live_status_banner = st.empty() # For high-level status
        live_metrics = st.empty()
        live_chart = st.empty()
        live_log = st.empty()
        
        # --- Legend & Help ---
        with st.expander("ℹ️ 모니터링 가이드 (Legend & Help)", expanded=False):
            st.markdown(f"""
            - <span style='color:{COLOR_PRIMARY}'>●</span> **실시간 신호**: 현재 감지된 60Hz 대역의 에너지 강도
            - <span style='color:{COLOR_ACCENT_CYAN}'>--</span> **임계값 (Threshold)**: 시스템이 '가동'으로 판단하는 기준 (Otsu 알고리즘으로 자동 조절)
            - <span style='color:{COLOR_ANOMALY_RED}'>●</span> **탐지 (ON)**: 기계 가동이나 특이 신호가 감지된 시점
            """, unsafe_allow_html=True)
        
        # --- Render Function (Reusable) ---
        def render_dashboard(latest_mag, latest_threshold, latest_state, latest_score, current_time):
             # 1. Status Banner (Eye-friendly high visibility)
             if latest_state == "ON":
                 live_status_banner.error(f"### ⚠️ 탐지 중 (Machine ON) - {current_time}")
             else:
                 live_status_banner.success(f"### ✅ 대기 중 (Machine OFF) - {current_time}")

             # 2. Metrics
             with live_metrics.container():
                c1, c2, c3 = st.columns(3)
                c1.metric("상태 (Status)", latest_state)
                c2.metric("60Hz 강도 (Peak)", f"{latest_mag:.4f}")
                c3.metric("이상 점수", f"{latest_score*100:.1f}%")
                
             # 3. Chart
             live_chart.plotly_chart(
                 plot_live_trend(
                     st.session_state["live_history_time"],
                     st.session_state["live_history_mag_60"],
                     latest_threshold,
                     st.session_state.get("live_history_state", [])
                 ),
                 use_container_width=True
             )

        # New Interval Control
        interval_mode = st.radio("조회 범위 (Time Range)", 
                                ["🕒 최근 30분 (Recent 30m)", "📅 최근 24시간 (Recent 24h)", "📅 지정 기간 (Custom)"], 
                                horizontal=True)
        
        custom_start = None
        custom_end = None
        
        if interval_mode == "📅 지정 기간 (Custom)":
            c1, c2 = st.columns(2)
            with c1:
                custom_start = st.text_input("시작 시간 (YYYY-MM-DD HH:MM:SS)", value=(datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"))
            with c2:
                custom_end = st.text_input("종료 시간 (YYYY-MM-DD HH:MM:SS)", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if st.toggle("🔴 모니터링 시작 (Start Stream)", value=False):
            # 1. Initialize Buffer with History (Run Once or when mode changes)
            current_mode_id = f"{interval_mode}_{custom_start}_{custom_end}"
            if "live_mode_id" not in st.session_state or st.session_state["live_mode_id"] != current_mode_id:
                st.session_state["live_history_mag_60"] = []
                st.session_state["live_history_time"] = []
                st.session_state["live_history_state"] = []
                st.session_state["live_mode_id"] = current_mode_id
                
                with st.spinner("⏳ 초기 데이터 로딩 중 (Fetching History)..."):
                    initial_logs = []
                    if interval_mode == "🕒 최근 30분 (Recent 30m)":
                         start_time = datetime.utcnow() - timedelta(minutes=30)
                         start_iso = start_time.isoformat()
                         initial_logs = fetch_logs_by_range(start_iso)
                    elif interval_mode == "📅 최근 24시간 (Recent 24h)":
                         start_time = datetime.utcnow() - timedelta(hours=24)
                         start_iso = start_time.isoformat()
                         initial_logs = fetch_logs_by_range(start_iso)
                    else:
                        try:
                            initial_logs = fetch_logs_by_range(
                                custom_start.replace(" ", "T"), 
                                custom_end.replace(" ", "T")
                            )
                        except:
                            st.error("날짜 형식이 올바르지 않습니다.")
                    
                    for log in reversed(initial_logs):
                        feat = log.get('features', [])
                        raw_ts = log.get('created_at', '') # ISO 8601
                        ts_dt = datetime.fromisoformat(raw_ts.replace('Z', '+00:00'))
                        if ts_dt.date() < datetime.utcnow().date():
                            t_label = ts_dt.strftime("%m/%d %H:%M:%S")
                        else:
                            t_label = ts_dt.strftime("%H:%M:%S")
                            
                        mag, _, stt, _, thres = processor.process_features(feat, sensitivity=otsu_multiplier)
                        st.session_state["live_history_mag_60"].append(mag)
                        st.session_state["live_history_time"].append(t_label)
                        st.session_state["live_history_state"].append(stt)
                        st.session_state["live_last_threshold"] = thres

                    # --- CRITICAL FIX: Render immediately after loading history ---
                    if st.session_state["live_history_mag_60"]:
                        render_dashboard(
                            st.session_state["live_history_mag_60"][-1],
                            st.session_state.get("live_last_threshold", 0.0),
                            st.session_state["live_history_state"][-1],
                            0.0, # Initial score 0
                            st.session_state["live_history_time"][-1]
                        )
            
            # Polling Loop
            st.info("🔄 실시간 폴링 루프 시작됨 (Polling Loop Started)")
            while True:
                if interval_mode == "📅 지정 기간 (Custom)":
                     if st.session_state["live_history_mag_60"]:
                         render_dashboard(st.session_state["live_history_mag_60"][-1], 
                                         st.session_state.get("live_last_threshold", 0.0), 
                                         st.session_state["live_history_state"][-1], 0.0, "")
                         st.success(f"데이터 로드 완료: {len(st.session_state['live_history_mag_60'])}개 포인트")
                     else:
                         st.warning("해당 기간에 데이터가 없습니다.")
                     break 
                
                logs = fetch_latest_logs(limit=1)
                if logs and len(logs) > 0:
                    latest_entry = logs[0]
                    features = latest_entry.get('features', [])
                    raw_ts = latest_entry.get('created_at', '')
                    time_str = raw_ts[11:19] 
                    
                    last_time_label = st.session_state["live_history_time"][-1] if st.session_state["live_history_time"] else ""
                    
                    if time_str not in last_time_label: 
                        mag, m120, stt, thres, score = processor.process_features(features, sensitivity=otsu_multiplier)
                        
                        st.session_state["live_history_mag_60"].append(mag)
                        st.session_state["live_history_time"].append(time_str)
                        st.session_state["live_history_state"].append(stt)
                        st.session_state["live_last_threshold"] = thres 
                        
                        if len(st.session_state["live_history_mag_60"]) > 500:
                            st.session_state["live_history_mag_60"] = st.session_state["live_history_mag_60"][-500:]
                            st.session_state["live_history_time"] = st.session_state["live_history_time"][-500:]
                            st.session_state["live_history_state"] = st.session_state["live_history_state"][-500:]

                        render_dashboard(mag, thres, stt, score, time_str)
                        
                        if stt == "ON":
                            live_log.error(f"⚠️ [{time_str}] 가동 감지!")
                        else:
                            live_log.success(f"✅ [{time_str}] 대기 중")
                
                time.sleep(2)
        else:
            # When OFF, just show the last captured state if history exists
            if "live_history_mag_60" in st.session_state and st.session_state["live_history_mag_60"]:
                st.warning("⏱️ 모니터링이 중지되었습니다. 마지막 데이터가 표시됩니다.")
                
                # Fetch threshold from state (fallback to 0.0)
                saved_thres = st.session_state.get("live_last_threshold", 0.0)
                
                render_dashboard(
                    st.session_state["live_history_mag_60"][-1], 
                    saved_thres, 
                    st.session_state["live_history_state"][-1], 
                    0.0, 
                    ""
                )
                
                if st.button("🗑️ 기록 초기화 (Clear All Data)", use_container_width=True):
                    del st.session_state["live_history_mag_60"]
                    del st.session_state["live_history_time"]
                    del st.session_state["live_history_state"]
                    st.rerun()
            else:
                st.info("위 스위치를 켜서 실시간 모니터링을 시작하세요.")

    elif uploaded_file:
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

