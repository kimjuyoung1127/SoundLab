import streamlit as st

def render_header():
    col1, col2 = st.columns([1, 10])
    with col1:
        st.markdown("## 📡")
    with col2:
        st.markdown("### SignalCraft Lab")
    st.divider()

def render_metrics(data):
    """
    Renders the dashboard metrics.
    Args:
        data (dict): Expected keys: 'memory_usage_mb', 'algo_time_ms', 'anomalies_count'
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("메모리 사용량", f"{data['memory_usage_mb']:.0f} MB")
    with col2:
        st.metric("처리 속도", f"{data['algo_time_ms']:.0f} ms")
    with col3:
        st.metric("감지된 이상징후", f"{data['anomalies_count']} 건", delta_color="inverse")

