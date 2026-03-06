import requests
import pandas as pd
import time
import random

# -----------------------------
# SUBREDDIT LIST
# -----------------------------

subreddits = [
"AskReddit","NoStupidQuestions","TooAfraidToAsk","Advice","self","LifeProTips","explainlikeimfive","CasualConversation",
"AskMen","AskWomen","AskWomenOver30","AskMenOver30","Men","Women",
"Fitness","bodyweightfitness","LoseIt","nutrition","running","bodybuilding","yoga","biohacking",
"productivity","getdisciplined","selfimprovement","meditation","DecidingToBeBetter",
"personalfinance","financialindependence","FIRE","fatFIRE","investing","sidehustle","povertyfinance",
"jobs","careeradvice","careerguidance","antiwork","remotework","freelance","digitalnomad",
"startups","Entrepreneur","smallbusiness","SaaS","startuplife","bootstrapping","Founders","buildinpublic",
"marketing","digital_marketing","SEO","PPC","Emailmarketing","growth_marketing","advertising",
"programming","webdev","learnprogramming","devops","coding","software","technology","Futurology",
"MachineLearning","ArtificialIntelligence","ChatGPT","LocalLLaMA","OpenAI","singularity","datascience",
"youtubers","ContentCreators","podcasting","streaming","Twitch","NewTubers",
"ecommerce","dropship","AmazonFBA","EtsySellers",
"photography","cooking","coffee","woodworking","gardening","cars","motorcycles",
"Parenting","NewParents","Mommit","Daddit",
"college","gradschool","GetStudying","learnpython",
"internetisbeautiful","dataisbeautiful","mildlyinteresting","todayilearned"
]

# -----------------------------
# CONFIG
# -----------------------------

TARGET_POSTS = 20000

headers = {
"User-Agent": "startup-opportunity-research"
}

# -----------------------------
# LOAD EXISTING DATA (for deduplication)
# -----------------------------
import os

existing_urls = set()

if os.path.exists("reddit_startup_ideas_dataset.csv"):
    existing_df = pd.read_csv("reddit_startup_ideas_dataset.csv")
    if "url" in existing_df.columns and "title" in existing_df.columns:
        existing_urls = set(
            (existing_df["url"].fillna("") + existing_df["title"].fillna("")).tolist()
        )
    print("Existing posts loaded:", len(existing_urls))
else:
    existing_df = pd.DataFrame()

all_posts = []

# -----------------------------
# SCRAPER FUNCTION
# -----------------------------

def scrape_subreddit(subreddit):

    after = None
    count = 0

    print(f"\nScraping: {subreddit}")

    while count < 1000:

        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"

        if after:
            url += f"&after={after}"

        try:
            response = requests.get(url, headers=headers, timeout=20)

            if response.status_code != 200:
                print("Blocked. Waiting...")
                time.sleep(15)
                continue

            data = response.json()["data"]["children"]

            if not data:
                break

            for post in data:

                p = post["data"]

                post_url = p.get("url")
                post_title = p.get("title")

                # Skip posts with missing URL or title
                if not post_url or not post_title:
                    continue

                # Create a unique identifier using URL + title
                unique_id = post_url + post_title

                if unique_id in existing_urls:
                    continue

                existing_urls.add(unique_id)

                all_posts.append({
                    "subreddit": subreddit,
                    "title": p.get("title"),
                    "score": p.get("score"),
                    "comments": p.get("num_comments"),
                    "created_utc": p.get("created_utc"),
                    "url": post_url,
                    "text": p.get("selftext")
                })

                count += 1

            after = data[-1]["data"]["name"]

            print("Posts collected:", len(all_posts))

            time.sleep(random.uniform(2,5))

            if len(all_posts) >= TARGET_POSTS:
                return

        except Exception as e:

            print("Error:", e)
            time.sleep(10)

# -----------------------------
# MAIN LOOP
# -----------------------------

for sub in subreddits:

    if len(all_posts) >= TARGET_POSTS:
        break

    scrape_subreddit(sub)

# -----------------------------
# SAVE DATASET
# -----------------------------

new_df = pd.DataFrame(all_posts)

if not existing_df.empty:
    df = pd.concat([existing_df, new_df], ignore_index=True)
else:
    df = new_df

df = df.drop_duplicates(subset=["url","title"])

df.to_csv("reddit_startup_ideas_dataset.csv", index=False)

print("\nScraping finished")
print("Total posts:", len(df))
