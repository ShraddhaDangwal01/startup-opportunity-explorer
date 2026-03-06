import requests
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0"
}

subreddit = "startups"

url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"

posts = []
after = None

while len(posts) < 10000:

    if after:
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100&after={after}"

    response = requests.get(url, headers=headers)

    data = response.json()["data"]["children"]

    for post in data:
        posts.append(post["data"]["title"])

    after = data[-1]["data"]["name"]

    print("Posts collected:", len(posts))

    time.sleep(1)

df = pd.DataFrame(posts, columns=["title"])

df.to_csv("reddit_large_dataset.csv", index=False)

print("Finished:", len(df))