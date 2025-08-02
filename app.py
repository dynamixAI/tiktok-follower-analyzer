import streamlit as st
import zipfile
import os
import tempfile
import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="TikTok Follower Analyzer", layout="centered")

st.title("📊 TikTok Follower Analyzer")

st.markdown("""
Welcome! This tool helps you analyze your TikTok followers and following data.

---

### 🔑 Step 1: Request Your Data from TikTok

To get started:

1. Tap the link below to open TikTok and **log into your account**.
2. Navigate to **Settings and privacy > Account > Download your data**.
3. Choose **All data** and **TXT format** and submit your request.
4. Wait for TikTok to notify you when the ZIP file is ready.
5. Download it to your device.

👉 [Open TikTok Login Page](https://www.tiktok.com/login)

---

### ⬆️ Step 2: Upload the TikTok ZIP File

Once your ZIP file is ready, upload it below:
""")

uploaded_zip = st.file_uploader("Upload your TikTok data (.zip)", type="zip")

def load_user_data(file_path):
    """
    Parse TikTok follower/following file with two-line format:
    Date: YYYY-MM-DD HH:MM:SS UTC
    Username: username_here
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # skip empty lines

    for i in range(0, len(lines), 2):
        if i+1 >= len(lines):
            break  # no username line for last date line
        
        date_line = lines[i]
        user_line = lines[i+1]

        date_match = re.match(r"Date:\s*(.*) UTC", date_line)
        username_match = re.match(r"Username:\s*(.*)", user_line)

        if date_match and username_match:
            date_str = date_match.group(1)
            username = username_match.group(1)
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                date = None

            data.append({"username": username, "date": date})

    return pd.DataFrame(data)

if uploaded_zip:
    st.success("ZIP file uploaded successfully!")

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "tiktok_data.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getvalue())

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        extracted_files = os.listdir(tmp_dir)
        st.write("Extracted files:", extracted_files)

        followers_df = pd.DataFrame()
        following_df = pd.DataFrame()

        for file in extracted_files:
            file_lower = file.lower()
            file_path = os.path.join(tmp_dir, file)
            if "follower" in file_lower:
                followers_df = load_user_data(file_path)
            elif "following" in file_lower:
                following_df = load_user_data(file_path)

        if followers_df.empty or following_df.empty:
            st.error("Couldn't find or parse Follower.txt and Following.txt files properly.")
        else:
            st.subheader("👥 Summary")
            st.write(f"Total Followers: {len(followers_df)}")
            st.write(f"Total Following: {len(following_df)}")

            followers_set = set(followers_df['username'])
            following_set = set(following_df['username'])

            # People you follow who don't follow you back
            non_followbacks = following_set - followers_set

            # People who follow you but you don't follow back
            fans_only = followers_set - following_set

            # Estimate unfollowers:
            # Those who are in following list but not in followers list
            unfollowers = following_set - followers_set

            # Gather unfollower details with dates from following_df
            unfollowers_data = []
            for user in unfollowers:
                user_rows = following_df[following_df['username'] == user]
                if not user_rows.empty:
                    followed_on = user_rows.iloc[0]['date']
                else:
                    followed_on = None
                unfollowers_data.append({
                    "username": user,
                    "followed_on": followed_on,
                    "unfollowed_on": "Unknown"
                })
            unfollowers_df = pd.DataFrame(unfollowers_data)

            # Display non-followbacks with clickable links
            st.subheader("➡️ People You Follow Who Don't Follow You Back")
            for user in sorted(non_followbacks):
                url = f"https://www.tiktok.com/search?q={user}"
                st.markdown(f"[{user}]({url})", unsafe_allow_html=True)

            # Display fans only with clickable links
            st.subheader("🫂 People Who Follow You But You Don't Follow Back")
            for user in sorted(fans_only):
                url = f"https://www.tiktok.com/search?q={user}"
                st.markdown(f"[{user}]({url})", unsafe_allow_html=True)

            # Display estimated unfollowers
            st.subheader("❌ People Who Unfollowed You After Following")
            if not unfollowers_df.empty:
                for _, row in unfollowers_df.iterrows():
                    url = f"https://www.tiktok.com/search?q={row['username']}"
                    followed_str = row['followed_on'].strftime("%Y-%m-%d %H:%M") if pd.notnull(row['followed_on']) else "Unknown"
                    st.markdown(f"- [{row['username']}]({url}) — Followed: {followed_str}, Unfollowed: {row['unfollowed_on']}")
            else:
                st.write("No unfollowers detected.")

            # Plot overview chart
            counts = {
                "Followers": len(followers_set),
                "Following": len(following_set),
                "Non-Followbacks": len(non_followbacks),
                "Fans Only": len(fans_only),
                "Unfollowers (estimated)": len(unfollowers)
            }

            fig, ax = plt.subplots()
            ax.bar(counts.keys(), counts.values(), color=['green', 'blue', 'red', 'orange', 'purple'])
            ax.set_ylabel("Count")
            ax.set_title("TikTok Followers/Following Overview")
            st.pyplot(fig)

            # Prepare CSV export with categories
            combined_users = list(followers_set.union(following_set))
            categories = []
            for u in combined_users:
                if u in followers_set and u in following_set:
                    categories.append("Mutual")
                elif u in followers_set:
                    categories.append("Follower Only")
                else:
                    categories.append("Following Only")

            csv_df = pd.DataFrame({
                "Username": combined_users,
                "Category": categories
            })

            st.subheader("⬇️ Download your analysis data")
            st.download_button(
                "Download User List CSV",
                csv_df.to_csv(index=False).encode('utf-8'),
                "tiktok_users.csv",
                "text/csv"
            )
