# ===============================
# MERGE ALL REDDIT DATASETS
# REMOVE DUPLICATES
# CREATE MASTER DATASET
# ===============================

import pandas as pd
import glob

# --------------------------------
# 1. FIND ALL CSV FILES
# --------------------------------

csv_files = glob.glob("*.csv")

print("CSV files found:")
for f in csv_files:
    print(f)

# --------------------------------
# 2. LOAD ALL DATASETS
# --------------------------------

dfs = []

for file in csv_files:
    try:
        df = pd.read_csv(file)
        print(f"Loaded {file} : {len(df)} rows")
        dfs.append(df)
    except Exception as e:
        print(f"Error loading {file}: {e}")

# --------------------------------
# 3. COMBINE ALL DATAFRAMES
# --------------------------------

combined_df = pd.concat(dfs, ignore_index=True)

print("\nTotal rows before cleaning:", len(combined_df))

# --------------------------------
# 4. REMOVE DUPLICATES
# --------------------------------

# Remove duplicates based on title
combined_df = combined_df.drop_duplicates(subset=["title"])

print("Rows after removing duplicate titles:", len(combined_df))

# --------------------------------
# 5. REMOVE EMPTY TITLES
# --------------------------------

combined_df = combined_df.dropna(subset=["title"])

print("Rows after removing empty titles:", len(combined_df))

# --------------------------------
# 6. RESET INDEX
# --------------------------------

combined_df = combined_df.reset_index(drop=True)

# --------------------------------
# 7. SAVE MASTER DATASET
# --------------------------------

combined_df.to_csv("reddit_master_dataset.csv", index=False)

print("\nMaster dataset saved as: reddit_master_dataset.csv")
print("Total rows in master dataset:", len(combined_df))
print("Final dataset size:", len(combined_df))

# --------------------------------
# 8. BASIC DATASET SUMMARY
# --------------------------------

print("\nDataset Summary")
print("----------------")
print("Unique Subreddits:", combined_df["subreddit"].nunique())
print("Average Score:", combined_df["score"].mean())
print("Average Comments:", combined_df["comments"].mean())

print("\nTop Subreddits:")
print(combined_df["subreddit"].value_counts().head(10))
