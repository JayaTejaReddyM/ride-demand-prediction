import threading
import queue
import random
import time
from collections import defaultdict, deque
from datetime import datetime

from .data_service import ZONE_COORDS

request_queue = queue.Queue()          # shared buffer between threads
_lock = threading.Lock()               # protects the shared data below
_live_counts = defaultdict(int)        # zone_id -> live request count
_recent = deque(maxlen=10)             # last 10 requests
_started = False

# busier zones receive more simulated requests
WEIGHTS = {0: 1.0, 1: 0.8, 2: 0.7, 3: 0.9, 4: 1.1,
           5: 0.5, 6: 0.4, 7: 0.3, 8: 0.6, 9: 0.3}


def _producer():
    """Simulates ride requests arriving in real time."""
    zones = list(WEIGHTS.keys())
    weights = list(WEIGHTS.values())
    while True:
        zone = random.choices(zones, weights)[0]
        request_queue.put({"zone_id": zone, "time": datetime.now()})
        time.sleep(0.5)

def _consumer():
    """Takes requests from the queue and updates the live counts."""
    while True:
        req = request_queue.get()      # waits until a request arrives
        with _lock:                    # only one thread updates at a time
            _live_counts[req["zone_id"]] += 1
            _recent.appendleft({
                "zone": ZONE_COORDS[req["zone_id"]][0],
                "time": req["time"].strftime("%H:%M:%S"),
            })
        request_queue.task_done()


def start_ingestion():
    """Start both threads once."""
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_producer, daemon=True, name="producer").start()
    threading.Thread(target=_consumer, daemon=True, name="consumer").start()


def get_snapshot():
    with _lock:
        counts = [{"zone_id": z, "zone_name": ZONE_COORDS[z][0],
                   "live_requests": _live_counts[z]} for z in ZONE_COORDS]
        return {"counts": counts, "recent": list(_recent),
                "queue_size": request_queue.qsize()}