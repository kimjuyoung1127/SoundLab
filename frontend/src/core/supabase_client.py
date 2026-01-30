
import os
import streamlit as st
from supabase import create_client, Client

# --- Configuration from Latest.md ---
# In production, these should be in st.secrets or environment variables
SUPABASE_URL = "https://zigwndnmxmxctcayeavx.supabase.co"
# Note: Publishable key is safe to be here as it is client-side public
SUPABASE_KEY = "sb_publishable_b8Cotvjt7qt3HOVgVY0KwA_f3h-yOuw"

@st.cache_resource
def init_connection() -> Client:
    """Initialize Supabase connection."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_latest_logs(limit: int = 10):
    """
    Fetch the latest sound logs from Supabase.
    """
    try:
        supabase = init_connection()
        response = supabase.table("sound_logs") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
        return []

def fetch_logs_by_range(start_iso: str, end_iso: str = None):
    """
    Fetch logs within a specific time range.
    start_iso: ISO 8601 string (e.g. '2023-10-27T10:00:00')
    end_iso: Optional ISO 8601 string
    """
    try:
        supabase = init_connection()
        query = supabase.table("sound_logs") \
            .select("*") \
            .order("created_at", desc=True) \
            .gte("created_at", start_iso)
            
        if end_iso:
            query = query.lte("created_at", end_iso)
            
        # Limit to 1000 to prevent crash if range is too huge
        response = query.limit(1000).execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to filter Supabase data: {e}")
        return []
