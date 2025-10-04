# gateway.py
from fastapi import FastAPI
from kafka import KafkaProducer
import json
from datetime import datetime
import random

app = FastAPI(title="YT View Gateway")

BOOTSTRAP = "localhost:9092"
TOPIC = "views"

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    linger_ms=5  # small linger to allow micro-batching client-side
)

@app.get("/view/{video_id}")
def add_view(video_id: int):
    # enrich event with typical fields
    event = {
        "video_id": int(video_id),
        "user_id": f"user_{random.randint(1000,9999)}",
        "region": random.choice(["IN","US","EU","JP","BR"]),
        "device": random.choice(["mobile","desktop","tv"]),
        "timestamp": datetime.utcnow().isoformat()
    }
    # send asynchronously
    producer.send(TOPIC, value=event)
    # note: not calling flush() for performance — KafkaProducer will batch/flush
    return {"status": "queued", "event": event}
