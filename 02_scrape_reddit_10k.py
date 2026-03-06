import requests
import pandas as pd
import time
import random

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

subreddit = "startups"
posts = []
after = None

while len(posts) < 10000:

    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"

    if after:
        url += f"&after={after}"

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            print("Blocked or error:", response.status_code)
            time.sleep(10)
            continue

        data = response.json()["data"]["children"]

        if not data:
            break

        for post in data:
            posts.append(post["data"]["title"])

        after = data[-1]["data"]["name"]

        print("Posts collected:", len(posts))

        # random delay so Reddit doesn't block us
        time.sleep(random.uniform(3,6))

    except Exception as e:
        print("Retrying after error:", e)
        time.sleep(10)

df = pd.DataFrame(posts, columns=["title"])
df.to_csv("reddit_10k_posts.csv", index=False)

print("Finished:", len(df))
