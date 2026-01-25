import plotly.graph_objects as go
from src.config import COLOR_PRIMARY, COLOR_ANOMALY_RED, COLOR_ACCENT_CYAN

def plot_analysis_results(timestamps, magnitudes, threshold, anomalies):
    """
    Renders time-series data using WebGL (scattergl) for performance.
    """
    fig = go.Figure()
    
    # 1. Main Signal Line (WebGL)
    fig.add_trace(go.Scattergl(
        x=timestamps,
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
            x0=timestamps[0],
            y0=threshold,
            x1=timestamps[-1],
            y1=threshold,
            line=dict(color=COLOR_ACCENT_CYAN, width=1, dash="dash"),
        )
        fig.add_annotation(
            x=timestamps[0],
            y=threshold,
            text=f"Threshold: {threshold:.2f}",
            showarrow=False,
            yshift=10,
            font=dict(color=COLOR_ACCENT_CYAN)
        )

    # 3. Anomaly Markers (WebGL)
    # Filter only anomalies for plotting
    if len(timestamps) > 0 and anomalies.any():
        anomaly_times = timestamps[anomalies]
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

    # Layout styling to match "App Dark"
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(
            title="Time (s)", 
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)'
        ),
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
