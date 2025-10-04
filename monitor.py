# monitor.py
import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
import time

DB_FILE = "videos.db"
REFRESH_INTERVAL = 2  # seconds

st.set_page_config(page_title="YT Traffic Monitor", layout="wide")
st.title("📊 Live YouTube Traffic Monitor (SQLite)")

# ensure DB and tables exist
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS video_stats (
    video_id INTEGER PRIMARY KEY,
    views INTEGER DEFAULT 0
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS video_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER,
    user_id TEXT,
    region TEXT,
    device TEXT,
    timestamp TEXT
)
""")
conn.commit()

st.sidebar.markdown("**Controls**")
refresh = st.sidebar.slider("Refresh interval (seconds)", min_value=1, max_value=10, value=REFRESH_INTERVAL)

# layout: left = stats, right = recent details
left, right = st.columns([2, 3])

with left:
    st.subheader("Aggregated Views (video_stats)")
    df_stats = pd.read_sql_query("SELECT video_id, views FROM video_stats ORDER BY views DESC", conn)
    if df_stats.empty:
        st.info("No aggregated data yet. Start the client + consumer.")
    else:
        st.dataframe(df_stats, use_container_width=True)
        bar = alt.Chart(df_stats).mark_bar().encode(
            x=alt.X('video_id:N', title="Video ID"),
            y=alt.Y('views:Q', title="Views"),
            tooltip=['video_id', 'views']
        ).properties(height=300)
        st.altair_chart(bar, use_container_width=True)

    # line chart: snapshot of video_stats over time is not stored; use details table to make a time series
    st.subheader("Views Over Time (last 10 minutes, per minute)")
    df_time = pd.read_sql_query("""
        SELECT video_id, timestamp FROM video_details
        WHERE timestamp IS NOT NULL AND timestamp != ''
        ORDER BY id DESC
        LIMIT 10000
    """, conn)

    if not df_time.empty:
        df_time['timestamp'] = pd.to_datetime(df_time['timestamp'], errors='coerce')
        df_time = df_time.dropna(subset=['timestamp'])
        # bucket to minute
        df_time['minute'] = df_time['timestamp'].dt.floor('1min')
        series = df_time.groupby(['minute', 'video_id']).size().reset_index(name='count')
        line = alt.Chart(series).mark_line(point=True).encode(
            x=alt.X('minute:T', title='Minute'),
            y=alt.Y('count:Q', title='Views'),
            color='video_id:N',
            tooltip=['minute', 'video_id', 'count']
        ).properties(height=300)
        st.altair_chart(line, use_container_width=True)
    else:
        st.info("No time-series data yet (video_details empty).")

with right:
    st.subheader("Recent Events (video_details)")
    df_recent = pd.read_sql_query("SELECT id, video_id, user_id, region, device, timestamp FROM video_details ORDER BY id DESC LIMIT 200", conn)
    if df_recent.empty:
        st.info("No events yet.")
    else:
        st.dataframe(df_recent, use_container_width=True)

# auto-refresh
st.sidebar.write("Auto-refresh every few seconds")
time.sleep(refresh)
st.rerun()
