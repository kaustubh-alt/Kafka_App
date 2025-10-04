# client.py
import threading
import time
import random
import requests

API_BASE = "http://127.0.0.1:8000/view"  # gateway endpoint
VIDEO_IDS = [1, 2, 3, 4, 5]
THREADS = 5               # number of concurrent threads generating traffic
VIEWS_PER_THREAD = 1000  # if you want finite runs; set high or loop forever
MIN_DELAY = 0.1      # min seconds between requests
MAX_DELAY = 0.5          # max seconds between requests

def worker(thread_id):
    i = 0
    while True:
        vid = random.choice(VIDEO_IDS)
        try:
            resp = requests.get(f"{API_BASE}/{vid}", timeout=2)
            # optional: check resp.status_code
        except Exception as e:
            print(f"[client {thread_id}] request error:", e)
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        i += 1
        # if i >= VIEWS_PER_THREAD: break

threads = []
for t in range(THREADS):
    th = threading.Thread(target=worker, args=(t,), daemon=True)
    th.start()
    threads.append(th)

print("Load generator started. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping load generator.")
