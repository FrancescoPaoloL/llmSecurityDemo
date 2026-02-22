import time
import threading
from dataclasses import dataclass, field
from typing import List, Optional

TTL_SECONDS = 600

@dataclass
class QueryRecord:
    text: str
    timestamp: float
    embedding_requested: bool = False
    logprobs_requested: bool = False

@dataclass
class IPSession:
    queries: List[QueryRecord] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)

    def add_query(self, text: str, embedding_requested: bool = False, logprobs_requested: bool = False):
        self.queries.append(QueryRecord(text=text, timestamp=time.time(),
            embedding_requested=embedding_requested, logprobs_requested=logprobs_requested))
        self.last_seen = time.time()

    def recent_queries(self, window_seconds: float = 60.0) -> List[QueryRecord]:
        cutoff = time.time() - window_seconds
        return [q for q in self.queries if q.timestamp >= cutoff]

    def is_expired(self) -> bool:
        return (time.time() - self.last_seen) > TTL_SECONDS

class LLM10SessionStore:
    def __init__(self):
        self._store: dict = {}
        self._lock = threading.Lock()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()

    def get_or_create(self, ip: str) -> IPSession:
        with self._lock:
            if ip not in self._store or self._store[ip].is_expired():
                self._store[ip] = IPSession()
            return self._store[ip]

    def record_query(self, ip: str, text: str, embedding_requested: bool = False,
                     logprobs_requested: bool = False) -> IPSession:
        session = self.get_or_create(ip)
        with self._lock:
            session.add_query(text, embedding_requested, logprobs_requested)
        return session

    def get_session(self, ip: str) -> Optional[IPSession]:
        with self._lock:
            s = self._store.get(ip)
            if s and not s.is_expired():
                return s
            return None

    def _cleanup_loop(self):
        while True:
            time.sleep(TTL_SECONDS // 2)
            with self._lock:
                expired = [ip for ip, s in self._store.items() if s.is_expired()]
                for ip in expired:
                    del self._store[ip]

session_store = LLM10SessionStore()

