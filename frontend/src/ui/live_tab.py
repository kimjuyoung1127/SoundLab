import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from src.core.supabase_client import fetch_latest_logs, fetch_logs_by_range
from src.core.stream_processor import StreamProcessor
from src.ui.plots import plot_live_trend
from src.config import COLOR_PRIMARY, COLOR_ACCENT_CYAN, COLOR_ANOMALY_RED

def render_live_tab(otsu_multiplier):
    """
    Renders the Live Monitoring tab.
    """
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
    
    # --- Render Function (Internal helper) ---
    def render_dashboard(latest_mag, latest_threshold, latest_state, latest_score, current_time):
         # 1. Status Banner
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

    # Interval Control
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
                     initial_logs = fetch_logs_by_range(start_time.isoformat())
                elif interval_mode == "📅 최근 24시간 (Recent 24h)":
                     start_time = datetime.utcnow() - timedelta(hours=24)
                     initial_logs = fetch_logs_by_range(start_time.isoformat())
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
                    raw_ts = log.get('created_at', '')
                    ts_dt = datetime.fromisoformat(raw_ts.replace('Z', '+00:00'))
                    t_label = ts_dt.strftime("%m/%d %H:%M:%S") if ts_dt.date() < datetime.utcnow().date() else ts_dt.strftime("%H:%M:%S")
                    
                    mag, _, stt, _, thres = processor.process_features(feat, sensitivity=otsu_multiplier)
                    st.session_state["live_history_mag_60"].append(mag)
                    st.session_state["live_history_time"].append(t_label)
                    st.session_state["live_history_state"].append(stt)
                    st.session_state["live_last_threshold"] = thres

                if st.session_state["live_history_mag_60"]:
                    render_dashboard(
                        st.session_state["live_history_mag_60"][-1],
                        st.session_state.get("live_last_threshold", 0.0),
                        st.session_state["live_history_state"][-1],
                        0.0,
                        st.session_state["live_history_time"][-1]
                    )
        
        # Polling Loop
        st.info("🔄 실시간 감지 시작됨")
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
                        live_log.error(f"⚠️ [{time_str}] 가동 탐지!")
                    else:
                        live_log.success(f"✅ [{time_str}] 대기 중")
            
            time.sleep(2)
    else:
        if "live_history_mag_60" in st.session_state and st.session_state["live_history_mag_60"]:
            st.warning("⏱️ 모니터링이 중지되었습니다. 마지막 데이터가 표시됩니다.")
            render_dashboard(
                st.session_state["live_history_mag_60"][-1], 
                st.session_state.get("live_last_threshold", 0.0), 
                st.session_state["live_history_state"][-1], 
                0.0, ""
            )
            
            if st.button("🗑️ 기록 초기화 (Clear All Data)", use_container_width=True):
                del st.session_state["live_history_mag_60"]
                del st.session_state["live_history_time"]
                del st.session_state["live_history_state"]
                st.rerun()
            
            # Export
            st.markdown("---")
            st.subheader("📊 데이터 내보내기 (Export Data)")
            export_df = pd.DataFrame({
                "시간": st.session_state["live_history_time"],
                "신호레벨": st.session_state["live_history_mag_60"],
                "가동상태": st.session_state["live_history_state"]
            })
            csv = export_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 현재 실시간 기록 CSV 저장", data=csv,
                             file_name=f"live_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime='text/csv')
        else:
            st.info("위 스위치를 켜서 실시간 모니터링을 시작하세요.")
