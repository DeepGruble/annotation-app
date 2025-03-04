import streamlit as st

st.set_page_config(page_title="Annotation Tool", layout="centered")

st.title("Annotation Tool")

st.write("Select an annotation task:")

col1, col2 = st.columns(2)

with col1:
    if st.button("Dental Numbering", use_container_width=True):
        st.switch_page("pages/dental_numbering.py")

with col2:
    if st.button("Anomaly Detection", use_container_width=True):
        st.switch_page("pages/dental_anomalies.py")
