import streamlit as st
import numpy as np
import plotly.graph_objects as go
from src.core.analysis import calculate_spectral_stats

@st.dialog("🔍 주파수 스펙트럼 분석 (Frequency Explorer)", width="large")
def show_spectral_analysis_dialog(uploaded_file):
    """
    Dialog content for spectral analysis.
    """
    st.markdown("""
    **전체 오디오 파일의 주파수 대역을 분석합니다.**
    가장 에너지가 높은 주파수를 찾아내어, 분석 타겟으로 설정할 수 있습니다.
    """)
    
    # Reset file pointer
    if hasattr(uploaded_file, 'seek'):
        uploaded_file.seek(0)
        
    # Analysis
    with st.spinner("스펙트럼 분석 중... (Calculating PSD)"):
        freqs, psd, top_peaks = calculate_spectral_stats(uploaded_file)
    
    if len(freqs) > 0:
        # 1. Plot Spectrum (Large View)
        fig = go.Figure()
        
        # Transform to dB
        psd_db = 10 * np.log10(psd + 1e-9)
        
        fig.add_trace(go.Scattergl(
            x=freqs, 
            y=psd_db,
            mode='lines', 
            name='PSD (dB/Hz)',
            line=dict(color='#00CC96', width=1.5)
        ))
        
        # Add markers for peaks
        peak_freqs = [p['freq'] for p in top_peaks]
        # Find corresponding dB values (approximate lookup)
        peak_dbs = []
        for pf in peak_freqs:
            idx = (np.abs(freqs - pf)).argmin()
            peak_dbs.append(psd_db[idx])
            
        fig.add_trace(go.Scatter(
            x=peak_freqs,
            y=peak_dbs,
            mode='markers',
            name='Top Peaks',
            marker=dict(color='#FF4B4B', size=10, symbol='x')
        ))
        
        fig.update_layout(
            title="Power Spectral Density (전체 구간)",
            xaxis_title="Frequency (Hz)",
            yaxis_title="Power (dB/Hz)",
            template="plotly_dark",
            xaxis_range=[0, 1000], 
            height=500, # Taller chart for modal
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. Top Peaks Recommendation
        st.subheader("🎯 추천 타겟 주파수 (Click to Apply)")
        st.info("아래 버튼을 누르면 해당 주파수가 **즉시 적용**되고 분석창이 닫힙니다.")
        
        cols = st.columns(len(top_peaks))
        for i, peak in enumerate(top_peaks):
            freq = peak['freq']
            with cols[i]:
                st.metric(f"Rank #{i+1}", f"{freq:.1f} Hz")
                if st.button(f"적용하기", key=f"apply_peak_modal_{i}"):
                    # Update Session State
                    st.session_state["target_freq_input"] = float(f"{freq:.1f}")
                    st.toast(f"✅ 타겟 주파수가 {freq:.1f}Hz로 설정되었습니다! 재분석을 시작합니다.", icon="🔄")
                    st.rerun() # Closes the dialog and reruns the app
    else:
        st.error("분석 데이터를 추출할 수 없습니다.")

def render_frequency_explorer(uploaded_file):
    """
    Renders the trigger button in the sidebar.
    """
    st.markdown("---")
    st.write("🔦 **주파수 탐색기**")
    if st.button("🚀 스펙트럼 분석 (모달 열기)", use_container_width=True):
        show_spectral_analysis_dialog(uploaded_file)
