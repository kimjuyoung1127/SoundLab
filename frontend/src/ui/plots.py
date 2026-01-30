import plotly.graph_objects as go
from src.config import COLOR_PRIMARY, COLOR_ANOMALY_RED, COLOR_ACCENT_CYAN

def plot_analysis_results(timestamps, magnitudes, threshold, anomalies, highlight_timestamps=None):
    """
    Renders time-series data using WebGL (scattergl) for performance.
    Args:
        highlight_timestamps (list, optional): List of timestamps to highlight.
    """
    # Force reload trigger
    fig = go.Figure()
    
    # 0. Convert timestamps to datetime for MM:SS formatting through Plotly
    # We use a dummy date (e.g., today) to represent duration as time of day
    import pandas as pd
    
    # If timestamps are empty, skip
    if len(timestamps) == 0:
        return fig
    
    # Create datetime objects relative to a base date. 
    # This allows Plotly to format "0" as "00:00:00" and "305" as "00:05:05"
    # We use a fixed reference date so time is consistent.
    t_pd = pd.to_datetime(timestamps, unit='s', origin='unix')
    
    # 1. Main Signal Line (WebGL)
    fig.add_trace(go.Scattergl(
        x=t_pd,
        y=magnitudes,
        mode='lines',
        name='Signal Energy',
        line=dict(color=COLOR_PRIMARY, width=1.5),
        hoverinfo='x+y'
    ))
    
    # 2. Threshold Line
    # Create a line across the whole time range
    if len(timestamps) > 0:
        fig.add_shape(
            type="line",
            x0=t_pd[0],
            y0=threshold,
            x1=t_pd[-1],
            y1=threshold,
            line=dict(color=COLOR_ACCENT_CYAN, width=1, dash="dash"),
        )
        fig.add_annotation(
            x=t_pd[0],
            y=threshold,
            text=f"Threshold: {threshold:.2f}",
            showarrow=False,
            yshift=10,
            font=dict(color=COLOR_ACCENT_CYAN)
        )

    # 3. Anomaly Markers (WebGL)
    # Filter only anomalies for plotting
    if len(timestamps) > 0 and anomalies.any():
        anomaly_times = t_pd[anomalies]
        anomaly_mags = magnitudes[anomalies]
        
        fig.add_trace(go.Scattergl(
            x=anomaly_times,
            y=anomaly_mags,
            mode='markers',
            name='Anomaly',
            marker=dict(
                size=8,
                color=COLOR_ANOMALY_RED,
                symbol='circle-open',
                line=dict(width=2)
            )
        ))
        
    # 4. Interactive Highlights (Multi-Select)
    if highlight_timestamps:
        # Ensure it's a list (handle single value edge case if passed incorrectly)
        if not isinstance(highlight_timestamps, list):
            highlight_timestamps = [highlight_timestamps]
            
        highlight_pd = pd.to_datetime(highlight_timestamps, unit='s', origin='unix')
        for t in highlight_pd:
            fig.add_vline(
                x=t, 
                line_width=2, 
                line_dash="dot", 
                line_color="yellow"
            )

    # --- Dynamic Focus (Auto-Zoom on Anomalies) ---
    xaxis_config = dict(
        title="Time (MM:SS)", 
        showgrid=True, 
        gridcolor='rgba(255,255,255,0.1)',
        tickformat="%M:%S",
        hoverformat="%M:%S",
        nticks=10 # Prevent label crowding
    )

    if anomalies.any():
        anomaly_times = t_pd[anomalies]
        t_start = anomaly_times.min() - pd.Timedelta(seconds=5)
        t_end = anomaly_times.max() + pd.Timedelta(seconds=5)
        xaxis_config['range'] = [t_start, t_end]

    # Layout styling to match "App Dark"
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=xaxis_config,
        yaxis=dict(
            title="Magnitude (dB-ish)", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def plot_live_trend(time_labels, magnitudes, threshold, state_history=None):
    """
    Renders live trend with IDENTICAL styling to the main analysis plot.
    Enhanced UX: tilted labels, precision hover.
    """
    fig = go.Figure()

    # Create detailed hover text
    hover_texts = []
    for i in range(len(time_labels)):
        state = state_history[i] if (state_history and i < len(state_history)) else "N/A"
        txt = (f"<b>Time:</b> {time_labels[i]}<br>"
               f"<b>Magnitude:</b> {magnitudes[i]:.4f}<br>"
               f"<b>Status:</b> {'⚠️ ON (Anomaly)' if state=='ON' else '✅ OFF (Normal)'}")
        hover_texts.append(txt)

    # 1. Main Signal
    fig.add_trace(go.Scattergl(
        x=time_labels,
        y=magnitudes,
        mode='lines+markers',
        name='Signal Energy',
        line=dict(color=COLOR_PRIMARY, width=2),
        marker=dict(size=4, opacity=0.8),
        text=hover_texts,
        hoverinfo='text'
    ))

    # 2. Threshold Line
    if len(time_labels) > 0:
        fig.add_shape(
            type="line",
            x0=time_labels[0],
            y0=threshold,
            x1=time_labels[-1],
            y1=threshold,
            line=dict(color=COLOR_ACCENT_CYAN, width=1.5, dash="dash"),
        )

    # 3. Anomaly Markers (Visible Red Dots)
    if state_history and len(state_history) == len(time_labels):
        anomaly_indices = [i for i, s in enumerate(state_history) if s == 'ON']
        if anomaly_indices:
            anomaly_x = [time_labels[i] for i in anomaly_indices]
            anomaly_y = [magnitudes[i] for i in anomaly_indices]
            anomaly_hover = [hover_texts[i] for i in anomaly_indices]
            
            fig.add_trace(go.Scattergl(
                x=anomaly_x,
                y=anomaly_y,
                mode='markers',
                name='Anomaly Detected',
                text=anomaly_hover,
                hoverinfo='text',
                marker=dict(
                    size=12, # Slightly larger for better targeting
                    color=COLOR_ANOMALY_RED,
                    symbol='circle',
                    line=dict(width=1, color="white")
                ),
                hoverlabel=dict(
                    bgcolor=COLOR_ANOMALY_RED,
                    font_size=16,
                    font_family="Inter, sans-serif",
                    font_color="white",
                    bordercolor="white"
                )
            ))

    # --- Dynamic Focus (Auto-Zoom on Anomalies) ---
    xaxis_config = dict(
        title="시간", 
        showgrid=True, 
        gridcolor='rgba(255,255,255,0.05)',
        tickangle=-30,
        automargin=True,
        nticks=10,
        # Spikes for "Targeting" feel
        showspikes=True,
        spikemode='across',
        spikesnap='cursor',
        spikedash='dot',
        spikecolor=COLOR_PRIMARY,
        spikethickness=1
    )

    if state_history and 'ON' in state_history:
        on_indices = [i for i, s in enumerate(state_history) if s == 'ON']
        # Zoom into the range from 5 points before the first ON to 5 points after the last ON
        start_idx = max(0, on_indices[0] - 5)
        end_idx = min(len(time_labels) - 1, on_indices[-1] + 5)
        xaxis_config['range'] = [time_labels[start_idx], time_labels[end_idx]]

    # Layout styling with Improved Readability
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=20, b=60),
        height=400,
        xaxis=xaxis_config,
        yaxis=dict(
            title="신호레벨", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)'
        )
    )
    
    return fig
