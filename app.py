import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob

st.set_page_config(page_title="KRI Dashboard", layout="wide")
st.title("🛡️ Key Risk Indicator (KRI) Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("data/sample_kri_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    def get_sentiment(text):
        analysis = TextBlob(text)
        return round(analysis.sentiment.polarity, 2)
    df['Sentiment_Score'] = df['Risk_Log_Description'].apply(get_sentiment)
    return df

df = load_data()

st.sidebar.header("Filter Options")
categories = st.sidebar.multiselect("Select KRI Category:", options=df["KRI_Category"].unique(), default=df["KRI_Category"].unique())
filtered_df = df[df["KRI_Category"].isin(categories)]

def determine_status(row):
    if row['Risk_Metric_Value'] >= row['Threshold_Red']:
        return "Critical (Red)"
    elif row['Risk_Metric_Value'] >= row['Threshold_Amber']:
        return "Warning (Amber)"
    else:
        return "Safe (Green)"

filtered_df['Risk_Status'] = filtered_df.apply(determine_status, axis=1)

total_risks = len(filtered_df)
critical_breaches = len(filtered_df[filtered_df['Risk_Status'] == "Critical (Red)"])
avg_sentiment = filtered_df['Sentiment_Score'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Monitored Indicators", total_risks)
col2.metric("Critical Red Breaches", critical_breaches, delta_color="inverse")
col3.metric("Average Log Sentiment", f"{avg_sentiment:.2f}")

st.markdown("---")
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📊 KRI Metric vs Threshold Limits")
    fig_bar = px.bar(
        filtered_df, x='Date', y='Risk_Metric_Value', color='Risk_Status',
        color_discrete_map={"Safe (Green)": "green", "Warning (Amber)": "orange", "Critical (Red)": "red"},
        hover_data=['KRI_Category', 'Risk_Log_Description']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with right_col:
    st.subheader("🧠 Sentiment Analysis of Risk Logs")
    fig_scatter = px.scatter(
        filtered_df, x='Sentiment_Score', y='Risk_Metric_Value', color='KRI_Category',
        size='Risk_Metric_Value', hover_name='Risk_Log_Description'
    )
    fig_scatter.add_vline(x=0.0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("📋 Detailed Risk Logs")
st.dataframe(filtered_df[['Date', 'KRI_Category', 'Risk_Metric_Value', 'Risk_Status', 'Sentiment_Score', 'Risk_Log_Description']].sort_values(by='Date', ascending=False), use_container_width=True)