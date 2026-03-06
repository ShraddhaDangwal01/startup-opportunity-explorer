import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)"
}

subreddits = [
    "startups",
    "Entrepreneur",
    "productivity",
    "sidehustle",
    "SaaS"
]

posts = []

for sub in subreddits:

    url = f"https://old.reddit.com/r/{sub}/"

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    for post in soup.find_all("p", class_="title"):
        title = post.get_text(strip=True)

        posts.append({
            "subreddit": sub,
            "title": title
        })

df = pd.DataFrame(posts)

print(df.head())
print("Total posts scraped:", len(df))

df.to_csv("reddit_posts.csv", index=False)