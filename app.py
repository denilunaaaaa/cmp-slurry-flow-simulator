import streamlit as st

st.title("CMP Slurry Flow Simulator")

speed = st.slider("Rotation Speed (rpm)", 10, 300, 100)

st.write(f"Current speed: {speed} rpm")
