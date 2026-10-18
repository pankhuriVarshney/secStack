"""Model routing: tiers, fallback chain, per-lead call budget, circuit breaker."""

import time
from app.config import LLM_MODEL

class ModelRouter:
    def __init__(self, budget_limit: int = 50):
        self.budget_limit = budget_limit
        self.call_count = 0
        self.circuit_open = False
        self.cooldown_until = 0.0

    def check_budget(self):
        if self.circuit_open:
            if time.time() > self.cooldown_until:
                self.circuit_open = False
                self.call_count = 0
            else:
                raise RuntimeError("Circuit breaker open due to error rate or budget exhaustion.")
        if self.call_count >= self.budget_limit:
            self.circuit_open = True
            self.cooldown_until = time.time() + 60.0
            raise RuntimeError("Per-session call budget exhausted. Circuit breaker triggered.")

    def record_call(self):
        self.call_count += 1

    def trip_breaker(self):
        self.circuit_open = True
        self.cooldown_until = time.time() + 30.0

router = ModelRouter()
