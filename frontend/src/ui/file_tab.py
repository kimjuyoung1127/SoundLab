import streamlit as st
import pandas as pd
from datetime import datetime
import src.core.services as services
from src.ui.plots import plot_analysis_results
from src.ui.components import render_metrics
from src.ui.timeline import render_timeline_section
from src.ui.analyzer import show_spectral_analysis_dialog
from src.config import DEFAULT_BANDWIDTH

def render_file_tab(uploaded_file, target_freq, otsu_multiplier, smart_mode):
    """
    Renders the File Upload analysis tab.
    """
    if uploaded_file:
        # Auto-open Modal if flag is set
        if st.session_state.get("show_auto_modal", False):
            st.session_state["show_auto_modal"] = False
            show_spectral_analysis_dialog(uploaded_file)
            
        if st.session_state.get("analysis_triggered", False):
            with st.spinner("🔄 신호 분석 및 데이터 처리 중..."):
                timestamps, magnitudes, heavy_proc_time, analysis_info = services.perform_heavy_analysis(
                    uploaded_file, target_freq, DEFAULT_BANDWIDTH, smart_mode
                )
                
            if smart_mode:
                with st.expander("📊 스마트 분석 결과 요약", expanded=True):
                    st.info("💡 **스마트 엔진**이 오디오 신호를 분석하여 최적의 환경을 자동으로 설정했습니다.")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "신호 추출 정밀도 (Bandwidth)", 
                            f"{analysis_info['detected_bandwidth']:.2f} Hz", 
                            help="타겟 주파수 주변에서 실제 신호가 밀집된 범위를 자동으로 감지하여 분석 정밀도를 높였습니다."
                        )
                    with col2:
                        st.metric(
                            "가동 판단 기준점 (Threshold)", 
                            f"{analysis_info.get('threshold_pct', 0.0):.1f} %",
                            help="전체 신호 대비 상위 몇 % 이상의 에너지를 '기계 가동(ON)'으로 볼 것인지 결정하는 자동 임계값입니다."
                        )
                    
                    st.caption("※ 이 값들은 정밀한 이상 징후 포착을 위해 매 신호마다 지능적으로 가변됩니다.")
                
                render_timeline_section(analysis_info)
            
            v5_results = analysis_info.get("v5_results")
            anomalies_mask, final_thresh, anomaly_list = services.perform_light_analysis(
                timestamps, magnitudes, otsu_multiplier, None, v5_results
            )
            
            metrics_data = services.get_dashboard_metrics(heavy_proc_time, len(anomaly_list))
            render_metrics(metrics_data)
            
            plot_placeholder = st.empty()
            st.subheader("🎧 오디오 재생 및 구간 확인")
            st.audio(uploaded_file)
            
            highlight_timestamps = []
            if anomaly_list:
                st.subheader("⚡ 가동 중 주요 고점(Peak) 이벤트 로그")
                df = pd.DataFrame(anomaly_list)
                def format_time(seconds):
                    return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"
                df["발생 시각"] = df["timestamp"].apply(format_time)
                display_df = df[["발생 시각", "magnitude", "threshold"]].copy()
                display_df.columns = ["발생 시각 (MM:SS)", "신호 레벨 (%)", "가동 임계값 (%)"]
                
                event = st.dataframe(display_df, use_container_width=True, on_select="rerun", selection_mode="multi-row" , hide_index=True)
                if event.selection.rows:
                    for idx in event.selection.rows:
                        highlight_timestamps.append(df.iloc[idx]["timestamp"])
            
            with plot_placeholder:
                st.plotly_chart(
                    plot_analysis_results(timestamps, magnitudes, final_thresh, anomalies_mask, highlight_timestamps=highlight_timestamps), 
                    use_container_width=True
                )
            
            with st.expander("📥 분석 결과 저장 (Export)", expanded=False):
                export_df = pd.DataFrame({"Timestamp (sec)": timestamps, "Magnitude": magnitudes, "Is_Anomaly": anomalies_mask})
                csv_file = export_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(label="📊 분석 데이터 CSV 다운로드", data=csv_file,
                                 file_name=f"analysis_{uploaded_file.name.split('.')[0]}_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("💡 분석 대기 중: 주파수를 확인한 후 아래 버튼을 눌러 정밀 분석을 시작하세요.")
            if st.button("🚀 분석 시작 (Start Analysis)", type="primary", use_container_width=True):
                st.session_state["analysis_triggered"] = True
                st.rerun()
    else:
        st.info("👈 왼쪽 사이드바에서 WAV 파일을 업로드하여 분석을 시작하세요.")
