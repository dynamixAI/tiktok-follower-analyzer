import streamlit as st

st.title("📊 TikTok Follower Analyzer")
st.write("Welcome! This app will help you analyze your TikTok followers and following data.")

st.markdown("""
### How to use:
1. Log in to TikTok on your browser and request your data.
2. When you receive the ZIP file from TikTok, upload it below.
3. The app will analyze your followers and following lists.
""")

uploaded_zip = st.file_uploader("Upload your TikTok data ZIP file", type="zip")

if uploaded_zip:
    st.write("Thanks for uploading your data! Analysis features coming soon.")
    # Here you will add your data extraction and analysis code later.
