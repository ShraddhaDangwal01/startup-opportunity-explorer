"""
Multi‑platform scraper for opportunity discovery project

Sources:
- Hacker News (API)
- Product Hunt (unofficial GraphQL endpoint – requires token)
- IndieHackers (basic HTML scraping)
- YouTube comments (via YouTube Data API)

Output:
combined_dataset.csv
"""

import requests
import pandas as pd
import time
from datetime import datetime
print("SCRIPT STARTED", flush=True)

# ===============================
# CONFIG
# ===============================

HN_POST_LIMIT = 5000
PH_POST_LIMIT = 5000
IH_POST_LIMIT = 5000
YT_VIDEO_LIMIT = 100
YT_COMMENT_LIMIT = 50

# OPTIONAL TOKENS (add if available)
PRODUCTHUNT_TOKEN = ""
YOUTUBE_API_KEY = ""

combined_data = []

# ===============================
# HACKER NEWS SCRAPER
# ===============================

def scrape_hackernews():

    print("Scraping Hacker News...")

    base_url = "https://hacker-news.firebaseio.com/v0"
    print("Fetching HackerNews story IDs...", flush=True)

    top_ids = requests.get(f"{base_url}/topstories.json", timeout=10).json()
    new_ids = requests.get(f"{base_url}/newstories.json", timeout=10).json()
    best_ids = requests.get(f"{base_url}/beststories.json", timeout=10).json()

    ids = list(dict.fromkeys(top_ids + new_ids + best_ids))
    collected = 0

    for story_id in ids:
        if collected >= HN_POST_LIMIT:
            break

        try:

            item = requests.get(f"{base_url}/item/{story_id}.json", timeout=10).json()

            if item and "title" in item:

                combined_data.append({
                    "source":"hackernews",
                    "title": item.get("title",""),
                    "text": item.get("text",""),
                    "score": item.get("score",0),
                    "comments": item.get("descendants",0),
                    "created_utc": item.get("time",0),
                    "url": item.get("url","")
                })

                collected += 1
                if collected % 100 == 0:
                    print("HN posts collected:", collected)

            time.sleep(0.15)

        except:
            pass


# ===============================
# PRODUCT HUNT SCRAPER
# ===============================

def scrape_producthunt():

    if PRODUCTHUNT_TOKEN == "":
        print("Skipping Product Hunt (token missing)")
        return

    print("Scraping Product Hunt...")

    headers = {
        "Authorization": f"Bearer {PRODUCTHUNT_TOKEN}",
        "Content-Type": "application/json"
    }

    query = """
    {
      posts(first:50){
        edges{
          node{
            name
            tagline
            votesCount
            commentsCount
            createdAt
            url
          }
        }
      }
    }
    """

    for _ in range(int(PH_POST_LIMIT/50)):

        try:

            r = requests.post(
                "https://api.producthunt.com/v2/api/graphql",
                json={"query":query},
                headers=headers
            )

            posts = r.json()["data"]["posts"]["edges"]

            for p in posts:

                node = p["node"]

                combined_data.append({
                    "source":"producthunt",
                    "title": node["name"],
                    "text": node["tagline"],
                    "score": node["votesCount"],
                    "comments": node["commentsCount"],
                    "created_utc": datetime.fromisoformat(node["createdAt"]).timestamp(),
                    "url": node["url"]
                })

            time.sleep(1)

        except:
            pass


# ===============================
# INDIEHACKERS SCRAPER
# ===============================

def scrape_indiehackers():

    print("Scraping IndieHackers...")

    page = 1
    collected = 0

    while collected < IH_POST_LIMIT:

        try:

            print(f"Fetching IndieHackers page {page}...", flush=True)
            url = f"https://www.indiehackers.com/posts?page={page}"

            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                break

            html = r.text

            titles = html.split('class="post-title"')

            for t in titles[1:]:

                title = t.split(">")[1].split("<")[0]

                combined_data.append({
                    "source":"indiehackers",
                    "title": title,
                    "text":"",
                    "score":0,
                    "comments":0,
                    "created_utc":0,
                    "url":"https://www.indiehackers.com"
                })

                collected += 1
                if collected % 100 == 0:
                    print("IH posts collected:", collected)

            if collected >= IH_POST_LIMIT:
                break

            page += 1
            time.sleep(1)

            if page > 200:
                break

        except:
            break


# ===============================
# YOUTUBE COMMENT SCRAPER
# ===============================

def scrape_youtube():

    if YOUTUBE_API_KEY == "":
        print("Skipping YouTube (API key missing)")
        return

    print("Scraping YouTube comments...")

    search_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part":"snippet",
        "q":"startup tools",
        "type":"video",
        "maxResults":YT_VIDEO_LIMIT,
        "key":YOUTUBE_API_KEY
    }

    r = requests.get(search_url,params=params).json()

    videos = [v["id"]["videoId"] for v in r["items"]]

    for vid in videos:

        comment_url = "https://www.googleapis.com/youtube/v3/commentThreads"

        params = {
            "part":"snippet",
            "videoId":vid,
            "maxResults":YT_COMMENT_LIMIT,
            "key":YOUTUBE_API_KEY
        }

        try:

            r = requests.get(comment_url,params=params).json()

            for c in r["items"]:

                text = c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

                combined_data.append({
                    "source":"youtube",
                    "title":"",
                    "text":text,
                    "score":0,
                    "comments":0,
                    "created_utc":0,
                    "url":f"https://youtube.com/watch?v={vid}"
                })

        except:
            pass


# ===============================
# RUN SCRAPERS
# ===============================

if __name__ == "__main__":

    scrape_hackernews()
    scrape_producthunt()
    scrape_indiehackers()
    scrape_youtube()

    print("Total records collected:", len(combined_data))
    df = pd.DataFrame(combined_data)

    df.to_csv("combined_dataset.csv",index=False)

    print("Saved dataset:",len(df),"rows")


import pandas as pd

df = pd.read_csv("startup_opportunity_dataset.csv")

print(len(df))
print(df.columns)
