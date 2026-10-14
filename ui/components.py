"""Small reusable Streamlit UI helpers."""
import streamlit as st

def section_heading(title: str, subtitle: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="subtle">{subtitle}</div>', unsafe_allow_html=True)
