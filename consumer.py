# consumer_dual_rows.py
import json
import sqlite3
import time
from collections import defaultdict
from kafka import KafkaConsumer
import signal
import sys

BOOTSTRAP = "localhost:9092"
TOPIC = "views"
GROUP_ID = "view_counters"
DB_FILE = "videos.db"

# Batching parameters
FLUSH_INTERVAL = 5        # seconds
DETAILS_BATCH_SIZE = 500  # bulk insert threshold

# Setup DB
conn = sqlite3.connect(DB_FILE, check_same_thread=False, timeout=30)
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

# Kafka consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=GROUP_ID,
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=1000  # allows loop to continue if no messages briefly
)

# In-memory buffers
agg_counts = defaultdict(int)   # video_id -> count
event_buffer = []               # list of tuples for executemany

last_flush = time.time()

def flush_to_db():
    global agg_counts, event_buffer, conn, cur
    if not agg_counts and not event_buffer:
        return

    # 1) Upsert aggregated counters (one statement per video_id)
    try:
        for vid, count in agg_counts.items():
            cur.execute("""
            INSERT INTO video_stats (video_id, views)
            VALUES (?, ?)
            ON CONFLICT(video_id) DO UPDATE SET views = video_stats.views + excluded.views
            """, (vid, count))

        # 2) Bulk insert details rows
        if event_buffer:
            cur.executemany("""
            INSERT INTO video_details (video_id, user_id, region, device, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """, event_buffer)

        conn.commit()
        print(f"Flushed -> counters: {len(agg_counts)} videos, details rows: {len(event_buffer)}")
    except Exception as e:
        print("Error flushing to DB:", e)
        conn.rollback()
    finally:
        agg_counts.clear()
        event_buffer.clear()

def graceful_shutdown(signum, frame):
    print("SIGTERM received. Flushing remaining data...")
    flush_to_db()
    consumer.close()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

print("🚀 Aggregating consumer started. Listening to topic:", TOPIC)

try:
    while True:
        # Poll for messages
        for message in consumer:
            event = message.value
            vid = int(event.get("video_id"))
            agg_counts[vid] += 1

            event_buffer.append((
                vid,
                event.get("user_id", ""),
                event.get("region", ""),
                event.get("device", ""),
                event.get("timestamp", "")
            ))

            now = time.time()
            # flush conditions
            if (now - last_flush) >= FLUSH_INTERVAL or len(event_buffer) >= DETAILS_BATCH_SIZE:
                flush_to_db()
                last_flush = time.time()

        # If poll timed out (no messages), still check flush interval
        if (time.time() - last_flush) >= FLUSH_INTERVAL and (agg_counts or event_buffer):
            flush_to_db()
            last_flush = time.time()

except Exception as e:
    print("Unexpected error:", e)
    flush_to_db()
    consumer.close()
    conn.close()
