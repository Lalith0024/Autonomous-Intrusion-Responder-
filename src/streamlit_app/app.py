import streamlit as st

st.set_page_config(page_title="AIR — Cyber Command", layout="wide", initial_sidebar_state="expanded")

from src.streamlit_app.layout import inject_ui
inject_ui()

# Define pages
pg = st.navigation([
    st.Page("dashboard.py", title="Overview", icon="🏠"),
    st.Page("pages/0_About.py", title="About AIR", icon="ℹ️"),
    st.Page("pages/1_Live_Analysis.py", title="Live Analysis", icon="⚡"),
    st.Page("pages/2_Incident_Dashboard.py", title="Incident History", icon="📊"),
    st.Page("pages/3_Eval_Results.py", title="Performance", icon="📈"),
])

pg.run()
