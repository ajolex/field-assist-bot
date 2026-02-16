"""Announcement generation and logging logic."""

from src.db.repositories.announcement_repo import AnnouncementRepository
from src.models.announcement import AnnouncementRecord


class AnnouncementService:
	"""Creates and tracks announcements."""

	def __init__(self, repository: AnnouncementRepository) -> None:
		self.repository = repository
		self.templates: dict[str, str] = {
			"morning_briefing": "Good morning team. Today's target is {target} completions.",
			"evening_summary": "Evening summary: {summary}",
			"form_update": "Form update: {form} is now on version {version}",
		}

	def from_template(self, template_name: str, **kwargs: str) -> str:
		"""Render announcement content from template."""

		template = self.templates.get(template_name)
		if template is None:
			raise ValueError(f"Unknown template: {template_name}")
		return template.format(**kwargs)

	async def log_announcement(self, type_name: str, channel: str, content: str) -> None:
		"""Persist sent announcement event."""

		await self.repository.create(
			AnnouncementRecord(type=type_name, channel=channel, content=content)
		)
