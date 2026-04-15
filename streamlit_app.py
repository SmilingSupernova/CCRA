import streamlit as st
from PIL import Image
import time

processedImage1 = "sampleImage1.png"
processedImage2 = "/workspaces/blank-app/sampleImage1_annotated.jpg"

st.set_page_config(layout="wide") 
st.title("LLM Legal Risk Analysis Model")
st.divider()

# Create two columns for the "Drag and Drop" vs "Output" look
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    st.text_area("Enter your legal document here", height=500)

with col2:
    st.subheader("Model Output")
    st.text_area("Results will appear here", height=500)