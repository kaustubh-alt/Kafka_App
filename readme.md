
# 🧠 YouTube View Count Simulation using Kafka

This project simulates how **YouTube handles millions of view counts per second** efficiently using **Apache Kafka** as a message broker.  
It demonstrates real-time event streaming, aggregation, and visualization — showing how large-scale systems manage heavy traffic without overloading databases.

---

## 🚀 Project Overview

When users watch videos, each view is recorded as an **event**.  
Directly writing every event to a database creates bottlenecks and performance issues.  
To solve this, systems like YouTube use **Kafka** to collect, store, and process events asynchronously.

This project recreates that workflow on a smaller scale:

| Component | Description |
|------------|-------------|
| **Client Script** | Simulates user traffic by generating random video view events. |
| **FastAPI Gateway** | Acts as the entry point for requests; pushes events to Kafka. |
| **Kafka Broker** | Buffers and streams all view events in real-time. |
| **Kafka Consumer** | Reads events, aggregates view counts, and writes to SQLite. |
| **SQLite DB** | Stores both aggregated views and detailed event logs. |
| **Streamlit Dashboard** | Displays real-time view counts and traffic analytics. |

---

## 🧩 System Architecture

[Client Script / Users] ↓ [FastAPI Gateway] ↓ [Kafka Topic: 'views'] ↓ [Kafka Consumer] ↙          ↘ [video_stats]  [video_details] (Aggregated)   (Detailed) ↓ [Streamlit Dashboard]

---

## ⚙️ Tech Stack

- **Python**
- **FastAPI**
- **Kafka (kafka-python / confluent-kafka)**
- **SQLite**
- **Streamlit**
- **Pandas / Matplotlib**

---

## 📂 Project Structure

📦 YTview/ │ ├── server.py           # FastAPI app (Kafka producer) ├── consumer.py          # Kafka consumer + DB aggregator ├── client.py  # Simulates random video views ├── monitor.py         # Streamlit dashboard ├── requirements.txt     # Python dependencies └── README.md

---

## 🧠 How It Works

1. **Client Simulation**  
   Generates thousands of fake "view" events (video_id, user_id, region, device, timestamp).

2. **FastAPI Gateway (Producer)**  
   Receives HTTP POST requests and pushes events to Kafka topic `views`.

3. **Kafka Broker**  
   Acts as a distributed queue for storing all view events reliably.

4. **Kafka Consumer**  
   Reads events in real-time:  
   - Aggregates total views per video.  
   - Buffers detailed data (user, region, timestamp) for batch insertion.  
   - Periodically flushes both to SQLite.

5. **Streamlit Dashboard**  
   Queries the database and visualizes:  
   - Total views per video (bar/line graph).  
   - Recent detailed view logs.  
   - Real-time updates every few seconds.

---

## 🔧 Installation & Setup

### 1️⃣ Prerequisites
- Python 3.9+  
- Kafka & Zookeeper running locally

To start Kafka locally:
```bash
zookeeper-server-start.sh config/zookeeper.properties
kafka-server-start.sh config/server.properties

2️⃣ Clone this Repository

git clone https://github.com/yourusername/yt-view-simulation.git
cd yt-view-simulation

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Create Kafka Topic

kafka-topics.sh --create --topic views --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1


---

▶️ Run the Simulation

Step 1: Start the FastAPI Gateway

uvicorn server:app --reload --port 8000

Step 2: Start the Kafka Consumer

python consumer.py

Step 3: Start the Client Traffic Simulator

python client.py

Step 4: Start the Streamlit Dashboard

streamlit run monitor.py


---

📊 Dashboard Features

Real-time total view count per video

Live table of incoming events

Auto-refreshing visualizations

Aggregated vs detailed view comparison



---

🧠 What This Simulates

This project demonstrates how YouTube’s backend might handle:

Billions of views efficiently using event streaming.

Aggregating data to minimize database writes.

Separating hot (aggregated) and cold (detailed) data for analytics.

Real-time monitoring dashboards for live traffic.



---

📈 Future Enhancements

Switch SQLite to PostgreSQL for better concurrency.

Add user session tracking & geo-distribution maps.

Implement multi-partition Kafka topics for scaling.

Integrate Spark Streaming or Flink for real-time analytics.



---

🏁 Conclusion

This simulation shows how large-scale systems like YouTube avoid direct DB writes per view, using Kafka for buffering and aggregation.
It’s a great starting point for understanding real-time event-driven architectures in production-grade systems.


---

🧩 Author

Kaustubh Gadhave
Backend & AI Engineer | Tech Innovator
✨ Building scalable and intelligent 