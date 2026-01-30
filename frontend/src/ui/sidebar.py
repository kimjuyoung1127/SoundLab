import streamlit as st
from src.ui.components import render_header
from src.ui.analyzer import render_frequency_explorer
from src.config import DEFAULT_TARGET_FREQ, DEFAULT_OTSU_MULTIPLIER

def render_sidebar():
    """
    Renders the sidebar controls and returns the configuration values.
    """
    with st.sidebar:
        render_header()
        
        # Help Section
        with st.expander("ℹ️ 앱 사용 가이드", expanded=False):
            st.markdown("""
            **1. 파일 업로드**: 분석할 WAV 파일을 드래그앤드롭 하세요.
            **2. 타겟 주파수**: 감지하고 싶은 특정 주파수(Hz)를 설정합니다.
            **3. 민감도**: 이상징후를 얼마나 엄격하게 판정할지 정합니다.
            """)
        
        # Mode Switcher
        data_source = st.radio("데이터 소스 (Data Source)", 
                              ["📁 파일 업로드", "📡 실시간 감지 "], 
                              horizontal=True)
        
        is_live_mode = "실시간 감지" in data_source
        uploaded_file = None

        if is_live_mode:
            st.info("📡 ESP32 디바이스에서 실시간 데이터를 수신합니다.")
        else:
            st.subheader("📁 분석 대상 파일")
            uploaded_file = st.file_uploader("WAV 파일을 업로드하세요", type=["wav"])

            # File Change Detection Logic
            if uploaded_file:
                current_file_name = uploaded_file.name
                last_file_name = st.session_state.get("last_uploaded_file")
                if current_file_name != last_file_name:
                    st.session_state["analysis_triggered"] = False
                    st.session_state["last_uploaded_file"] = current_file_name
                    st.session_state["show_auto_modal"] = True
        
        # Frequency Explorer (File Mode Only)
        if uploaded_file and not is_live_mode:
            render_frequency_explorer(uploaded_file)
        
        # Global Settings
        st.subheader("🎛️ 분석 설정 (Analysis Settings)")
        target_freq = st.number_input("타겟 주파수 (Hz)", value=DEFAULT_TARGET_FREQ, step=10.0, key="target_freq_input")
        otsu_multiplier = st.slider("민감도 (Sensitivity)", 0.5, 3.0, DEFAULT_OTSU_MULTIPLIER, 0.1)
        
        smart_mode = True
        with st.expander("⚙️ 고급 설정", expanded=False):
            st.caption("대역폭은 내부적으로 최적화된 값(2.0Hz)을 사용합니다.")
            smart_mode = st.toggle("🧠 스마트 분석 모드", value=True)
            
        st.markdown("---")
        
    return is_live_mode, uploaded_file, target_freq, otsu_multiplier, smart_mode
