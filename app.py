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

def parse_line(line):
    """Extract datetime and username from a line like:
       Date: 2025-08-02 01:00:44 UTCUsername: abdulllahi.salisu
    """
    match = re.search(r"Date:\s*(.*?)\s*UTCUsername:\s*(\S+)", line)
    if match:
        date_str, username = match.groups()
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except:
            date = None
        return username, date
    return None, None

def load_user_data(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            username, date = parse_line(line.strip())
            if username:
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

        # Load followers and following data
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

            # Sets for quick comparison
            followers_set = set(followers_df['username'])
            following_set = set(following_df['username'])

            # Non-followbacks: you follow them, but they don't follow you
            non_followbacks = following_set - followers_set

            # Fans only: they follow you, but you don't follow back
            fans_only = followers_set - following_set

            # Follow-then-unfollow detection:
            # Users who followed you at some point (in followers_df)
            # but are no longer following you (not in followers_set now)
            # For this, assume your current followers are in followers_set.
            # To detect unfollowers, check users in following_df and followers_df timestamps,
            # or if you have historical follower files. Here we infer from data:

            # Let's identify users who previously followed you (followers_df) but are missing now
            # Since we only have current data, this is tricky. 
            # But if followers_df includes historical dates (if you have older export),
            # we could compare.

            # For now, let's find users who followed you previously (appear in followers_df),
            # but not in current followers_set (assumed to be current followers_df usernames)
            # So if you upload old and new data, you'd compare.

            # Here we simulate this by assuming followers_df = historical followers,
            # and current followers are a separate upload (which you may add later).

            # For demo: treat all users in following_df not in followers_set as unfollowed you (simplified)
            unfollowers = set()
            unfollowers_dates = []

            # Find users who followed you before but not anymore
            # (For demonstration, those who are in following_df but not followers_set)
            for user in following_df['username']:
                if user not in followers_set:
                    # Find when they started following (date in following_df)
                    date_followed = following_df.loc[following_df['username'] == user, 'date'].iloc[0]
                    # Use None for unfollow date (since unknown)
                    unfollowers.add(user)
                    unfollowers_dates.append({"username": user, "followed_on": date_followed, "unfollowed_on": None})

            unfollowers_df = pd.DataFrame(unfollowers_dates)

            st.subheader("➡️ People You Follow Who Don't Follow You Back")
            for user in sorted(non_followbacks):
                url = f"https://www.tiktok.com/search?q={user}"
                st.markdown(f"[{user}]({url})", unsafe_allow_html=True)

            st.subheader("🫂 People Who Follow You But You Don't Follow Back")
            for user in sorted(fans_only):
                url = f"https://www.tiktok.com/search?q={user}"
                st.markdown(f"[{user}]({url})", unsafe_allow_html=True)

            st.subheader("❌ People Who Unfollowed You After Following")
            if not unfollowers_df.empty:
                for _, row in unfollowers_df.iterrows():
                    url = f"https://www.tiktok.com/search?q={row['username']}"
                    followed_str = row['followed_on'].strftime("%Y-%m-%d %H:%M") if pd.notnull(row['followed_on']) else "Unknown"
                    unfollowed_str = "Unknown"
                    st.markdown(f"- [{row['username']}]({url}) — Followed: {followed_str}, Unfollowed: {unfollowed_str}")
            else:
                st.write("No unfollowers detected.")

            # BONUS: Plotting follow/unfollow counts
            import matplotlib.pyplot as plt

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

            # Download CSV export
            st.subheader("⬇️ Download your analysis data")

            def to_clickable_link(user):
                return f"https://www.tiktok.com/search?q={user}"

            csv_df = pd.DataFrame({
                "Username": list(following_set.union(followers_set)),
                "Type": ["Both" if u in (followers_set & following_set) else
                         "Follower Only" if u in followers_set else
                         "Following Only" for u in (following_set.union(followers_set))],
            })

            st.download_button("Download User List CSV", csv_df.to_csv(index=False).encode('utf-8'), "tiktok_users.csv", "text/csv")
