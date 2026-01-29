import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap');

        /* Global Typography - Safer selector to avoid overriding icon fonts */
        html, body, .stApp, .stMarkdown, p, span, div, label {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', sans-serif;
        }

        /* Prevent 'Inter' from overriding Streamlit's icon font in expanders */
        span[data-testid="stWidgetLabel"] p, 
        .streamlit-expanderHeader p {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Ensure expander arrows remain icons */
        [data-testid="stExpanderChevron"] {
            font-family: inherit !important;
        }

        /* Main background & Soft layout */
        .stApp {
            background-color: #12161E;
            color: #E2E8F0;
        }
        
        /* Sidebar background - Slightly darker but not jet black */
        section[data-testid="stSidebar"] {
            background-color: #0A0E14;
            border-right: 1px solid rgba(255, 255, 255, 0.03);
        }
        
        /* Primary Color Accents - Soft Light Blue */
        .stButton button {
            background-color: #58C7F3;
            color: #0A0E14;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background-color: #7AD4F7;
            color: #0A0E14;
            box-shadow: 0 4px 12px rgba(88, 199, 243, 0.3);
            transform: translateY(-1px);
        }
        
        /* Custom Scrollbar - Muted */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.01);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(88, 199, 243, 0.3);
        }
        
        /* Metrics styling */
        div[data-testid="stMetricValue"] {
            color: #58C7F3;
            letter-spacing: -0.02em;
        }
        div[data-testid="stMetricLabel"] {
            color: #94A3B8;
            font-weight: 500;
        }

        /* Fix Slider Contrast (Red knob -> Theme Blue) */
        div[data-testid="stSlider"] [role="slider"] {
            background-color: #58C7F3;
            border-color: #58C7F3;
        }
        div[data-testid="stSlider"] [data-testid="stThumbValue"] {
            color: #58C7F3;
        }
        
        /* Expander Styling */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        </style>
    """, unsafe_allow_html=True)
