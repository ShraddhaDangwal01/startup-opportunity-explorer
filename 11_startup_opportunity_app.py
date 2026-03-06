import streamlit as st
import pandas as pd
import hashlib
import logging
import os

# ------------------------------------------------
# SECURITY CONFIG
# ------------------------------------------------

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)

SAFE_ERROR = "Something went wrong. Please refresh the application."

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.set_page_config(
    page_title="Startup Opportunity Explorer",
    layout="wide"
)

# ------------------------------------------------
# MODERN UI STYLE
# ------------------------------------------------

st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
background: linear-gradient(180deg,#0f172a,#020617);
color:white;
}

[data-testid="stSidebar"] {
background:#020617;
border-right:1px solid #1e293b;
}

h1,h2,h3,h4{
font-weight:600;
color:#e2e8f0;
}

p{
color:#cbd5f5;
}

.hero-title{
font-size:42px;
font-weight:700;
margin-bottom:10px;
}

.hero-sub{
font-size:18px;
opacity:0.8;
margin-bottom:30px;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DATASET PATH
# ------------------------------------------------

DATASET_PATH = "startup_opportunity_dataset.csv"

# ------------------------------------------------
# LOAD DATA SAFELY
# ------------------------------------------------

@st.cache_data
def load_dataset():

    if not os.path.exists(DATASET_PATH):
        raise Exception("Dataset missing")

    df = pd.read_csv(DATASET_PATH)

    required = [
        "subreddit",
        "title",
        "score",
        "comments",
        "created_utc",
        "content_clean"
    ]

    for col in required:
        if col not in df.columns:
            raise Exception("Dataset structure invalid")

    return df


try:
    df = load_dataset()

except Exception as e:
    logging.error(str(e))
    st.error("Data source unavailable.")
    st.stop()

# ------------------------------------------------
# DATE PROCESSING
# ------------------------------------------------

try:

    df["created_utc"] = pd.to_datetime(
        df["created_utc"],
        unit="s",
        errors="coerce"
    )

    df["year"] = df["created_utc"].dt.year

except Exception as e:

    logging.error(str(e))
    st.error(SAFE_ERROR)
    st.stop()

# ------------------------------------------------
# TOPICS
# ------------------------------------------------

topics = {

"Freelancing":[
"freelance","client","contract","gig"
],

"Marketing":[
"marketing","growth","advertising","promotion"
],

"Automation":[
"automate","automation","workflow"
],

"Productivity":[
"productivity","focus","efficiency"
],

"Learning & Skills":[
"learn","skill","career"
],

"Payments":[
"payment","invoice","transaction"
],

"Remote Work":[
"remote","work from home","distributed"
]

}

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------

with st.sidebar:

    st.title("Startup Opportunity Explorer")

    page = st.radio(
        "Navigation",
        [
            "Landing",
            "Market Analysis",
            "Opportunity Insights",
            "Dataset Overview",
            "Methodology"
        ]
    )

# ------------------------------------------------
# LANDING PAGE
# ------------------------------------------------

if page == "Landing":

    try:

        st.markdown(
            '<div class="hero-title">Startup Opportunity Explorer</div>',
            unsafe_allow_html=True
        )

        st.markdown(
        '<div class="hero-sub">Discover emerging startup opportunities by analyzing large scale online discussions.</div>',
        unsafe_allow_html=True)

        st.markdown("### Market Intelligence Snapshot")

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Discussions Analyzed",len(df))
        col2.metric("Communities",df["subreddit"].nunique())
        col3.metric("Avg Score",round(df["score"].mean(),1))
        col4.metric("Avg Comments",round(df["comments"].mean(),1))

        st.markdown("---")

        st.markdown("### Emerging Market Signals")

        market_counts={}

        for topic,keywords in topics.items():

            mask = pd.Series(False, index=df.index)

            for word in keywords:

                mask = mask | df["content_clean"].str.contains(
                    word,
                    case=False,
                    na=False
                )

            market_counts[topic]=len(df[mask])

        st.bar_chart(pd.Series(market_counts))

        st.markdown("---")

        st.markdown("### Communities Driving Innovation")

        subs = df["subreddit"].value_counts().head(10)

        if len(subs) > 0:

            st.bar_chart(subs)
            st.write(subs)

        else:

            st.info("No communities detected.")

        st.markdown("---")

        st.markdown("### Problem Signals Detected")

        problem_words = [
            "problem","issue","struggle",
            "difficult","frustrating","challenge"
        ]

        mask = df["content_clean"].str.contains(
            "|".join(problem_words),
            case=False,
            na=False
        )

        st.write(
            "Detected frustration-related discussions:",
            len(df[mask])
        )

    except Exception as e:

        logging.error(str(e))
        st.error(SAFE_ERROR)

# ------------------------------------------------
# MARKET ANALYSIS
# ------------------------------------------------

elif page == "Market Analysis":

    try:

        st.title("Market Opportunity Analysis")

        selected_topic = st.selectbox(
            "Select Market Area",
            ["Select a market to analyze"] + list(topics.keys())
        )

        if selected_topic == "Select a market to analyze":

            st.info("Choose a market to begin analysis.")
            st.stop()

        keywords = topics[selected_topic]

        mask = pd.Series(False, index=df.index)

        for word in keywords:

            mask = mask | df["content_clean"].str.contains(
                word,
                case=False,
                na=False
            )

        filtered=df[mask]

        if len(filtered)==0:

            st.warning("No discussions found for this topic.")
            st.stop()

        volume=len(filtered)

        avg_comments = filtered["comments"].mean()
        avg_score = filtered["score"].mean()

        opportunity_score=(volume*avg_comments*avg_score)/10000

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Discussion Volume",volume)
        col2.metric("Avg Comments",round(avg_comments,1))
        col3.metric("Avg Score",round(avg_score,1))
        col4.metric("Opportunity Score",round(opportunity_score,1))

        st.markdown("---")

        st.subheader("Trend Over Time")

        trend = filtered.groupby("year").size().reset_index(name="discussions")

        trend["year"] = trend["year"].astype(int)

        trend = trend.sort_values("year")

        st.line_chart(trend.set_index("year"))

        st.markdown("---")

        st.subheader("Top Communities Discussing This Topic")

        comm = filtered["subreddit"].value_counts().head(10)

        st.bar_chart(comm)

        st.write(comm)

    except Exception as e:

        logging.error(str(e))
        st.error(SAFE_ERROR)

# ------------------------------------------------
# OPPORTUNITY INSIGHTS
# ------------------------------------------------

elif page == "Opportunity Insights":

    try:

        st.title("Community Engagement Insights")

        subs = df["subreddit"].value_counts().head(15)

        st.bar_chart(subs)

        st.write(subs)

        st.markdown("---")

        col1,col2,col3 = st.columns(3)

        col1.metric("Average Score",round(df["score"].mean(),1))
        col2.metric("Average Comments",round(df["comments"].mean(),1))
        col3.metric("Total Discussions",len(df))

    except Exception as e:

        logging.error(str(e))
        st.error(SAFE_ERROR)

# ------------------------------------------------
# DATASET OVERVIEW
# ------------------------------------------------

elif page == "Dataset Overview":

    try:

        st.title("Dataset Overview")

        st.write("Total posts analyzed:",len(df))

        st.write("Total communities:",df["subreddit"].nunique())

        st.write(
            df["subreddit"].value_counts().head(20)
        )

    except Exception as e:

        logging.error(str(e))
        st.error(SAFE_ERROR)

# ------------------------------------------------
# METHODOLOGY
# ------------------------------------------------

elif page == "Methodology":

    st.title("Methodology")

    st.write("""

This platform analyzes large-scale online discussions to detect
emerging startup opportunities.

Signals used:

• discussion frequency  
• engagement metrics  
• problem signal detection  

These indicators help identify product gaps in growing markets.

""")

st.markdown("---")

st.caption("Startup Opportunity Explorer • Market Intelligence Dashboard")
