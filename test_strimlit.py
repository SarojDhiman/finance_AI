# test_streamlit.py
import streamlit as st

st.title("Test App")
st.write("If you see this, Streamlit is working!")

if st.button("Test Button"):
    st.success("Button clicked successfully!")