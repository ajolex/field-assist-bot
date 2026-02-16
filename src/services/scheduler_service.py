"""Async scheduling service."""

from collections.abc import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerService:
	"""Wrapper around APScheduler for app jobs."""

	def __init__(self, timezone: str) -> None:
		self.scheduler = AsyncIOScheduler(timezone=timezone)

	def start(self) -> None:
		"""Start scheduler if not running."""

		if not self.scheduler.running:
			self.scheduler.start()

	def shutdown(self) -> None:
		"""Stop scheduler without waiting."""

		if self.scheduler.running:
			self.scheduler.shutdown(wait=False)

	def schedule_cron(
		self,
		func: Callable[[], Awaitable[None]],
		*,
		hour: int,
		minute: int,
		job_id: str,
	) -> None:
		"""Register async cron job."""

		self.scheduler.add_job(func, "cron", hour=hour, minute=minute, id=job_id, replace_existing=True)
