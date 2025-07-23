import streamlit as st
import pandas as pd

st.set_page_config(page_title="TikTok Follower Analyzer", layout="centered")

st.title("📊 TikTok Follower Analyzer")
st.markdown("Upload your **Followers.csv** and **Following.csv** files from TikTok data download.")

followers_file = st.file_uploader("Upload followers CSV", type=["csv"])
following_file = st.file_uploader("Upload following CSV", type=["csv"])

if followers_file and following_file:
    followers_df = pd.read_csv(followers_file)
    following_df = pd.read_csv(following_file)

    try:
        followers_set = set(followers_df['Username'].str.lower())
        following_set = set(following_df['Username'].str.lower())

        not_following_back = following_set - followers_set
        not_followed_by_you = followers_set - following_set

        st.subheader("🚫 You follow them, but they don’t follow back")
        st.write(sorted(not_following_back))

        st.subheader("💡 They follow you, but you don’t follow back")
        st.write(sorted(not_followed_by_you))

    except Exception as e:
        st.error(f"Something went wrong: {e}")
