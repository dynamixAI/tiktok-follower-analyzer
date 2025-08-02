import streamlit as st
import zipfile
import os
import tempfile
import pandas as pd

st.set_page_config(page_title="TikTok Follower Analyzer", layout="centered")

st.title("📊 TikTok Follower Analyzer")

st.markdown("""
Welcome! This tool helps you analyze your TikTok followers and following data.

---

### 🔑 Step 1: Request Your Data from TikTok

To get started:

1. Tap the link below to open TikTok and **log into your account**.
2. Navigate to **Settings > Privacy > Download your data**.
3. Choose **TXT format** and submit your request.
4. Wait for TikTok to notify you when the ZIP file is ready.
5. Download it to your device.

👉 [Open TikTok Login Page](https://www.tiktok.com/login)

---

### ⬆️ Step 2: Upload the TikTok ZIP File

Once your ZIP file is ready, upload it below:
""")

uploaded_zip = st.file_uploader("Upload your TikTok data (.zip)", type="zip")

if uploaded_zip:
    st.success("ZIP file uploaded successfully!")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "tiktok_data.zip")
        
        # Save the uploaded file
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getvalue())

        # Extract contents
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        # Show extracted file names for reference
        extracted_files = os.listdir(tmp_dir)
        st.write("Extracted files:", extracted_files)
