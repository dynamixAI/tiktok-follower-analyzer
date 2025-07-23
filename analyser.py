import pandas as pd

def load_csv(file_path):
    """Loads a TikTok CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print("Error loading file:", e)
        return None

def compare_followers_and_following(followers_df, following_df):
    """Compares follower and following lists to find non-followers and non-followed."""
    followers = set(followers_df['Username'].str.lower())
    following = set(following_df['Username'].str.lower())

    not_following_back = following - followers
    not_followed_by_you = followers - following

    return not_following_back, not_followed_by_you

def main():
    print("👋 Welcome to the TikTok Follower Analyzer")
    print("📌 Please download your 'Followers' and 'Following' CSVs from TikTok > Settings > Download your data.")
    print("Once you have the files, enter the file paths below.")

    followers_path = input("Enter path to followers CSV file: ").strip()
    following_path = input("Enter path to following CSV file: ").strip()

    followers_df = load_csv(followers_path)
    following_df = load_csv(following_path)

    if followers_df is None or following_df is None:
        print("❌ Could not load one or both files.")
        return

    not_following_back, not_followed_by_you = compare_followers_and_following(followers_df, following_df)

    print("\n🚫 People you follow but they don't follow back:")
    for user in sorted(not_following_back):
        print("-", user)

    print("\n💡 People who follow you, but you're not following back:")
    for user in sorted(not_followed_by_you):
        print("-", user)

if __name__ == "__main__":
    main()
