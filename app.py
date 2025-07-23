# app.py

import streamlit as st
import pandas as pd

st.title("TikTok Follower Analyzer")

st.markdown("### Enter your TikTok handle:")
username = st.text_input("TikTok username")

if username:
    st.success(f"Welcome, @{username}!")

    st.markdown("### Paste your following list (one username per line):")
    following_raw = st.text_area("Your Following", height=200)
    
    st.markdown("### Paste your followers list (one username per line):")
    followers_raw = st.text_area("Your Followers", height=200)

    if st.button("Analyze"):
        following = set(following_raw.strip().splitlines())
        followers = set(followers_raw.strip().splitlines())

        not_following_back = following - followers
        not_followed_by_you = followers - following

        st.subheader("You follow them, but they don't follow you back:")
        st.write(not_following_back or "🎉 None!")

        st.subheader("They follow you, but you're not following back:")
        st.write(not_followed_by_you or "🎉 None!")
