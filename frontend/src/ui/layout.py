import streamlit as st
from src.ui.styles import inject_custom_css
from src.ui.sidebar import render_sidebar
from src.ui.live_tab import render_live_tab
from src.ui.file_tab import render_file_tab

def render_app():
    """
    Main entry point for the SignalCraft dashboard UI.
    Orchestrates sidebar controls and delegates content rendering to tabs.
    """
    # 1. Setup & Style Injection
    st.set_page_config(page_title="SignalCraft Lab", layout="wide", page_icon="📡")
    inject_custom_css()
    
    # 2. Sidebar Controls
    is_live_mode, uploaded_file, target_freq, otsu_multiplier, smart_mode = render_sidebar()

    # 3. Main Content Rendering (Delegated to Tab Components)
    if is_live_mode:
        st.subheader("📡 실시간 모니터링 (Live Monitor)")
        render_live_tab(otsu_multiplier)
    else:
        st.subheader("📁 파일 분석 (File Analysis)")
        render_file_tab(uploaded_file, target_freq, otsu_multiplier, smart_mode)
