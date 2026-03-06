import requests
import pandas as pd
import time
import random

# -------------------------
# SETTINGS
# -------------------------

TARGET_POSTS = 5000
OUTPUT_FILE = "reddit_dataset_progress.csv"

headers = {
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)"
}

# -------------------------
# NEW SUBREDDITS ONLY
# -------------------------

subreddits = [

# 20 highly active global communities (tech / AI / startups / marketing)
"Entrepreneurship",
"Founders",
"bootstrapping",
"passive_income",
"freelance",
"digitalnomad",
"remotework",
"onlinebusiness",
"technology",
"Futurology",
"innovation",
"bigdata",
"analytics",
"DataScienceJobs",
"deeplearning",
"MLQuestions",
"computervision",
"computerscience",
"softwareengineering",
"cloudcomputing",

# 10 India‑focused tech / startup communities not previously scraped
"developersIndia",
"StartUpIndia",
"IndiaInvestments",
"IndianStockMarket",
"indiasocial",
"IndiaBusiness",
"IndiaDiscussion",
"IndiaInvestors",
"IndiaStartups",
"IndiaTechCommunity"
]

# -------------------------
# LOAD EXISTING DATA
# -------------------------

try:
    existing_df = pd.read_csv(OUTPUT_FILE)
    print("Existing posts:", len(existing_df))
    if "subreddit" in existing_df.columns:
        scraped_subreddits = set(existing_df["subreddit"].dropna().unique())
    else:
        scraped_subreddits = set()
except:
    existing_df = pd.DataFrame()
    print("No previous dataset found")
    scraped_subreddits = set()

posts = []

# -------------------------
# SCRAPER
# -------------------------

def scrape_subreddit(subreddit):

    print(f"\nScraping: {subreddit}")

    after = None

    while True:

        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"

        if after:
            url += f"&after={after}"

        try:

            response = requests.get(url, headers=headers, timeout=20)

            if response.status_code == 404:
                print("Subreddit not found. Skipping...")
                break
            if response.status_code == 429:
                print("Rate limited. Sleeping 30 seconds...")
                time.sleep(30)
                continue
            if response.status_code != 200:
                print("Blocked or unexpected response. Waiting...")
                time.sleep(15)
                continue

            data = response.json()

            children = data["data"]["children"]

            if not children:
                break

            for post in children:

                p = post["data"]

                posts.append({
                    "subreddit": subreddit,
                    "title": p.get("title"),
                    "score": p.get("score"),
                    "comments": p.get("num_comments"),
                    "created_utc": p.get("created_utc"),
                    "url": p.get("url"),
                    "text": p.get("selftext")
                })

                total = len(posts)

                if total % 100 == 0:
                    print("Posts collected:", total)

                if total >= TARGET_POSTS:
                    return

            after = data["data"]["after"]

            if after is None:
                break

            time.sleep(random.uniform(3,6))

        except Exception as e:

            print("Error reading response. Retrying...")
            time.sleep(10)


# -------------------------
# MAIN LOOP
# -------------------------

for subreddit in subreddits:

    if subreddit in scraped_subreddits:
        print(f"Skipping already scraped subreddit: {subreddit}")
        continue

    if len(posts) >= TARGET_POSTS:
        break

    scrape_subreddit(subreddit)

    temp_df = pd.DataFrame(posts)

    if not existing_df.empty:
        temp_df = pd.concat([existing_df, temp_df], ignore_index=True)

    temp_df.drop_duplicates(inplace=True)

    temp_df.to_csv(OUTPUT_FILE, index=False)

    print("Saved progress:", len(temp_df))
    scraped_subreddits.add(subreddit)

# -------------------------
# FINAL SAVE
# -------------------------

final_df = pd.DataFrame(posts)

if not existing_df.empty:
    final_df = pd.concat([existing_df, final_df], ignore_index=True)

final_df.drop_duplicates(inplace=True)

final_df.to_csv("reddit_dataset_final.csv", index=False)

print("\nScraping finished")
print("Total rows:", len(final_df))
