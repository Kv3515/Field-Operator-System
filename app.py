import streamlit as st
import db

db.init_database()

st.set_page_config(
    page_title="Field Ops",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <link rel="manifest" href="/app/static/manifest.json">
    <meta name="theme-color" content="#8B2635">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Field Ops">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/app/static/service-worker.js');
        }
    </script>
""", unsafe_allow_html=True)

pages = [
    st.Page("pages/1_Home.py",            title="Home",           icon="🏠", default=True),
    st.Page("pages/2_Log_Sortie.py",      title="Log Sortie",     icon="✈️"),
    st.Page("pages/3_Drone_Status.py",    title="Drone Status",   icon="🚁"),
    st.Page("pages/4_Fault_Report.py",    title="Fault Report",   icon="⚠️"),
    st.Page("pages/5_Commander_View.py",  title="Commander View", icon="📊"),
]

pg = st.navigation(pages)
pg.run()
