import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# load dataset
df = pd.read_csv("reddit_posts.csv")

# extract keywords
vectorizer = CountVectorizer(
    stop_words="english",
    max_features=20
)

X = vectorizer.fit_transform(df["title"])

keywords = vectorizer.get_feature_names_out()

print("Top trending keywords:")
print(keywords)
