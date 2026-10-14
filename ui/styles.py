"""CareerAI visual styling."""
import streamlit as st

def inject_css() -> None:
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .stApp { background: #F6F8FC; }
      [data-testid="stSidebar"] { background: #111A35; }
      [data-testid="stSidebar"] * { color: #F3F5FF !important; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #C7CEE6 !important; }
      .hero { padding: 2rem 2.2rem; border-radius: 22px; color: white; background: linear-gradient(120deg,#172449 0%,#3449A8 55%,#6C63FF 100%); margin-bottom: 1.2rem; }
      .hero h1 { font-family: Manrope,sans-serif; font-size: clamp(2rem,4vw,3.1rem); line-height:1.1; margin:0 0 .7rem 0; color:white; }
      .hero p { color:#E2E7FF; font-size:1.05rem; max-width:700px; }
      .eyebrow { text-transform:uppercase; letter-spacing:.13em; font-weight:700; font-size:.72rem; color:#B9C5FF; margin-bottom:.6rem; }
      .metric-card { background:white; border:1px solid #E5E9F2; border-radius:16px; padding:1.05rem 1.2rem; box-shadow:0 4px 18px rgba(25,39,80,.035); min-height:112px; }
      .metric-label { font-size:.84rem; color:#667085; margin-bottom:.4rem; }
      .metric-value { font-family:Manrope,sans-serif; font-size:1.8rem; font-weight:800; color:#182447; }
      .metric-help { font-size:.76rem; color:#7A849A; margin-top:.25rem; }
      .section-title { font-family:Manrope,sans-serif; font-weight:800; font-size:1.35rem; color:#182447; margin:.5rem 0 .25rem; }
      .subtle { color:#667085; }
      div.stButton > button, div.stDownloadButton > button { border-radius:10px; font-weight:600; min-height:2.7rem; }
      div[data-testid="stForm"] { background:#fff; border:1px solid #E6EAF2; border-radius:16px; padding:1rem; }
      [data-testid="stMetric"] { background:#fff; border:1px solid #E5E9F2; padding:1rem; border-radius:14px; }
      .stProgress > div > div > div > div { background-color:#5B6CFF; }
      @media (max-width: 640px) { .hero { padding:1.35rem; } .metric-value {font-size:1.4rem;} }
    </style>
    """, unsafe_allow_html=True)

def metric_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-help">{help_text}</div></div>', unsafe_allow_html=True)
