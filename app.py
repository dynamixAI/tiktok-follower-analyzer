import streamlit as st
import pandas as pd
import zipfile
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading

def run_selenium_login():
    options = Options()
    options.add_argument("--start-maximized")
    # Uncomment below to run headless but then manual login is impossible
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiktok.com/login")
    
    st.info("Browser opened. Please log in manually.")
    time.sleep(60)  # Wait time for user to log in
    
    driver.get("https://www.tiktok.com/privacy/setting/download-your-data")
    st.info("Now navigate to 'Download your data' page in the browser.")
    time.sleep(300)  # Time to request data manually
    
    driver.quit()
    st.success("Selenium task complete. You can now upload your TikTok data ZIP file.")

def start_selenium_thread():
    thread = threading.Thread(target=run_selenium_login)
    thread.start()

st.title("📊 TikTok Follower Analyzer with TikTok Login")

if st.button("Open TikTok Login and Data Request (local only)"):
    st.warning("This will open a Chrome browser window locally. Run this only on your local machine.")
    start_selenium_thread()

uploaded_zip = st.file_uploader("Upload your TikTok Data ZIP file", type="zip")

if uploaded_zip:
    with zipfile.ZipFile(uploaded_zip) as z:
        st.write("Files in ZIP:", z.namelist())
        
        followers_file = None
        following_file = None
        
        for file in z.namelist():
            if "Followers" in file:
                followers_file = file
            elif "Following" in file:
                following_file = file
        
        if not followers_file or not following_file:
            st.error("Could not find Followers or Following files in the ZIP.")
        else:
            with z.open(followers_file) as f:
                followers = f.read().decode("utf-8").splitlines()
            with z.open(following_file) as f:
                following = f.read().decode("utf-8").splitlines()
            
            df_followers = pd.DataFrame(followers, columns=["username"])
            df_following = pd.DataFrame(following, columns=["username"])
            
            not_following_back = df_following[~df_following.username.isin(df_followers.username)]
            not_followed_back = df_followers[~df_followers.username.isin(df_following.username)]
            
            st.subheader("People you follow who don't follow you back")
            st.dataframe(not_following_back)
            
            st.subheader("People who follow you but you don't follow back")
            st.dataframe(not_followed_back)
            
            csv1 = not_following_back.to_csv(index=False).encode("utf-8")
            st.download_button("Download: Not Following Back CSV", data=csv1, file_name="not_following_back.csv")
            
            csv2 = not_followed_back.to_csv(index=False).encode("utf-8")
            st.download_button("Download: Not Followed Back CSV", data=csv2, file_name="not_followed_back.csv")
