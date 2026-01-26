import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any

def render_timeline_section(analysis_info: Dict[str, Any]):
    """
    Renders the Machine ON/OFF Timeline based on V5.7 segments.
    """
    v5_results = analysis_info.get("v5_results", [])
    
    # 1. Start/End Safety Check
    if not v5_results:
        return

    st.markdown("---")
    st.subheader("📊 신호 감지 타임라인 (Signal Detection Timeline)")
    
    # 2. Aggregate Segments (Consecutive ON chunks)
    segments = []
    current_segment = None
    
    # Chunk duration from results if possible, usually 5s
    # We can infer it from the first two items if available, or assume 5.0
    # In analysis.py we used CHUNK_DURATION_SEC = 5.0
    chunk_dur = 5.0 
    if len(v5_results) > 1:
        chunk_dur = v5_results[1]['time_sec'] - v5_results[0]['time_sec']
    
    for r in v5_results:
        state = r.get('state', 'OFF')
        # Time in result is the START of the chunk
        time_sec = r.get('time_sec', 0.0)
        
        if state == 'ON':
            if current_segment is None:
                current_segment = {'start': time_sec, 'end': time_sec + chunk_dur}
            else:
                # Extend segment
                current_segment['end'] = time_sec + chunk_dur
        else:
            if current_segment is not None:
                segments.append(current_segment)
                current_segment = None
                
    if current_segment is not None:
        segments.append(current_segment)
        
    if not segments:
        st.info("⚠️ 유효 신호가 감지되지 않았습니다. (No Valid Signals Detected)")
        return

    # 3. Metrics
    total_duration_sec = sum([s['end'] - s['start'] for s in segments])
    cycle_count = len(segments)
    
    # Format Helpers
    def fmt_time(s):
        return f"{int(s//60):02d}:{int(s%60):02d}"
    
    def fmt_dur(s):
        m = int(s // 60)
        sec = int(s % 60)
        if m > 0:
            return f"{m}분 {sec}초"
        return f"{sec}초"
    
    m1, m2, m3 = st.columns(3)
    m1.metric("누적 지속 시간", fmt_dur(total_duration_sec))
    m2.metric("감지 횟수 (Segments)", f"{cycle_count}회")
    
    if segments:
        avg_dur = total_duration_sec / len(segments)
        # m3.metric("평균 지속 시간", fmt_dur(avg_dur))
        # User Feedback: Don't imply machine cycles easily. 
        # Maybe show status instead?
        m3.metric("평균 지속 시간", fmt_dur(avg_dur))
    
    # 4. Timeline Chart (Gantt via Barh)
    fig = go.Figure()
    
    # We want a single horizontal bar track, but broken into pieces.
    # To make them distinct, we can use different colors or just one color.
    # Alternating colors might be nice.
    colors = ['#4CAF50', '#66BB6A'] # Green shades
    
    for i, seg in enumerate(segments):
        duration = seg['end'] - seg['start']
        start_time = seg['start']
        end_time = seg['end']
        
        label_text = f"Seg {i+1}<br>{fmt_time(start_time)}~{fmt_time(end_time)}"
        
        fig.add_trace(go.Bar(
            y=["Signal State"],
            x=[duration],
            base=[start_time],
            orientation='h',
            name=f"Seg {i+1}",
            marker_color=colors[i % 2],
            text=f"#{i+1}",
            textposition='auto',
            hovertemplate=f"<b>Segment #{i+1}</b><br>Start: {fmt_time(start_time)}<br>End: {fmt_time(end_time)}<br>Duration: {fmt_dur(duration)}<extra></extra>",
            showlegend=False
        ))
        
    # X-Axis formatting to MM:SS
    # Since x is in seconds, we can try to use tickformat if type was date, but it's linear.
    # We can just let it be seconds or try to override ticktext.
    # For simplicity, keep seconds but add title.
    
    fig.update_layout(
        title="신호 감지 타임라인 (Timeline)",
        xaxis_title="시간 (초)",
        yaxis_title="",
        height=180,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(200,200,200,0.2)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. Data Table (Structured)
    with st.expander("📋 감지 구간 상세 (Segment Details)", expanded=True):
        st.info("💡 **Tip**: 기계는 계속 켜져있는데 횟수가 너무 많다면, '스마트 분석'이 조용한 구간을 '꺼짐'으로 판단했을 수 있습니다.")
        table_data = []
        for i, seg in enumerate(segments):
            table_data.append({
                "ID": f"#{i+1}",
                "시작 시각": fmt_time(seg['start']),
                "종료 시각": fmt_time(seg['end']),
                "지속 시간": fmt_dur(seg['end'] - seg['start'])
            })
        st.table(pd.DataFrame(table_data))
