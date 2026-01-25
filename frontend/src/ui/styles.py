import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Main background */
        .stApp {
            background-color: #0E1117;
            color: #ffffff;
        }
        
        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #0B141D;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Primary Color Accents */
        .stButton button {
            background-color: #00BFFF;
            color: #000000;
            font-weight: bold;
            border: none;
            border-radius: 4px;
        }
        .stButton button:hover {
            background-color: #00FFFF;
            color: #000000;
             box-shadow: 0 0 10px rgba(0, 191, 255, 0.4);
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.02);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 191, 255, 0.4);
        }
        
        /* Metrics styling */
        div[data-testid="stMetricValue"] {
            color: #00BFFF;
            font-family: 'Space Grotesk', sans-serif;
        }
        div[data-testid="stMetricLabel"] {
            color: #9CA3AF;
        }
        </style>
    """, unsafe_allow_html=True)
