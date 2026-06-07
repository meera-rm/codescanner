import time
from typing import Dict
from collections import defaultdict


class RateLimiter:
    def __init__(self):
        self.limits: Dict[str, int] = defaultdict(lambda: 100)
        self.tokens: Dict[str, float] = defaultdict(lambda: 100.0)
        self.last_refill: Dict[str, float] = defaultdict(time.time)

    def set_limit(self, key_id: str, limit: int):
        self.limits[key_id] = limit
        self.tokens[key_id] = float(limit)
        self.last_refill[key_id] = time.time()

    def is_allowed(self, key_id: str) -> bool:
        limit = self.limits[key_id]
        now = time.time()
        elapsed = now - self.last_refill[key_id]
        refill_rate = limit / 60.0

        self.tokens[key_id] = min(
            limit, self.tokens[key_id] + elapsed * refill_rate
        )
        self.last_refill[key_id] = now

        if self.tokens[key_id] >= 1.0:
            self.tokens[key_id] -= 1.0
            return True
        return False

    def get_remaining(self, key_id: str) -> int:
        return max(0, int(self.tokens[key_id]))

    def get_limit(self, key_id: str) -> int:
        return self.limits[key_id]

    def get_reset_time(self, key_id: str) -> int:
        now = time.time()
        last_refill = self.last_refill[key_id]
        return int(last_refill + 60)
