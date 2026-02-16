"""Simple in-memory rate limiting utilities."""

import time


class RateLimiter:
	"""Per-key fixed-window rate limiter."""

	def __init__(self, limit: int, window_seconds: int) -> None:
		self.limit = limit
		self.window_seconds = window_seconds
		self._hits: dict[str, list[float]] = {}

	def allow(self, key: str) -> bool:
		"""Return True when request is within configured limits."""

		now = time.monotonic()
		window_start = now - self.window_seconds
		values = [stamp for stamp in self._hits.get(key, []) if stamp >= window_start]
		if len(values) >= self.limit:
			self._hits[key] = values
			return False
		values.append(now)
		self._hits[key] = values
		return True
