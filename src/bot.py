"""Discord bot application entry point."""

import asyncio
from pathlib import Path

import discord
from discord.ext import commands

from src.config import settings
from src.db import init_db
from src.db.repositories.announcement_repo import AnnouncementRepository
from src.db.repositories.escalation_repo import EscalationRepository
from src.db.repositories.interaction_repo import InteractionRepository
from src.integrations.google_sheets import GoogleSheetsClient
from src.integrations.openai_client import OpenAIClient
from src.integrations.surveycto import SurveyCTOClient
from src.knowledge.indexer import KnowledgeIndexer
from src.knowledge.retriever import KnowledgeRetriever
from src.services.announcement_service import AnnouncementService
from src.services.assignment_service import AssignmentService
from src.services.case_service import CaseService
from src.services.escalation_service import EscalationService
from src.services.progress_service import ProgressService
from src.services.protocol_service import ProtocolService
from src.services.scheduler_service import SchedulerService
from src.utils.logger import configure_logging, get_logger


COGS = [
	"src.cogs.admin",
	"src.cogs.cases",
	"src.cogs.protocol",
	"src.cogs.progress",
	"src.cogs.assignments",
	"src.cogs.forms",
	"src.cogs.announcements",
]


class FieldAssistBot(commands.Bot):
	"""Main Discord bot instance."""

	def __init__(self) -> None:
		intents = discord.Intents.default()
		intents.message_content = True
		super().__init__(command_prefix="!", intents=intents)
		self.log = get_logger("field_assist_bot")
		self.sheets_client = GoogleSheetsClient()
		self.survey_client = SurveyCTOClient()
		self.openai_client = OpenAIClient()

		indexer = KnowledgeIndexer(Path("docs/knowledge_base"), self.openai_client)
		retriever = KnowledgeRetriever(indexer.build_index(), self.openai_client)

		self.interaction_repository = InteractionRepository()
		self.escalation_repository = EscalationRepository()
		self.announcement_repository = AnnouncementRepository()

		self.escalation_service = EscalationService(self.escalation_repository)
		self.case_service = CaseService(self.survey_client)
		self.assignment_service = AssignmentService(self.sheets_client)
		self.progress_service = ProgressService(self.sheets_client)
		self.announcement_service = AnnouncementService(self.announcement_repository)
		self.protocol_service = ProtocolService(
			retriever,
			self.openai_client,
			self.interaction_repository,
			self.escalation_service,
		)
		self.scheduler_service = SchedulerService(settings.timezone)

	async def setup_hook(self) -> None:
		"""Load initial cogs and sync application commands."""

		await init_db()
		for cog in COGS:
			await self.load_extension(cog)
		self.scheduler_service.schedule_cron(
			self.run_morning_briefing,
			hour=6,
			minute=0,
			job_id="morning_briefing",
		)
		self.scheduler_service.schedule_cron(
			self.run_evening_summary,
			hour=18,
			minute=0,
			job_id="evening_summary",
		)
		self.scheduler_service.schedule_cron(
			self.monitor_form_versions,
			hour=0,
			minute=30,
			job_id="form_version_monitor",
		)
		if settings.discord_guild_id:
			guild = discord.Object(id=settings.discord_guild_id)
			self.tree.copy_global_to(guild=guild)
			await self.tree.sync(guild=guild)
			self.log.info("commands.synced", scope="guild", guild_id=settings.discord_guild_id)
		else:
			await self.tree.sync()
			self.log.info("commands.synced", scope="global")

	async def on_ready(self) -> None:
		"""Log readiness after gateway connection."""

		self.log.info("bot.ready", user=str(self.user), user_id=getattr(self.user, "id", None))
		self.scheduler_service.start()

	async def close(self) -> None:
		"""Close bot and shutdown scheduler."""

		self.scheduler_service.shutdown()
		await super().close()

	async def run_morning_briefing(self) -> None:
		"""Scheduled morning briefing hook."""

		content = self.announcement_service.from_template("morning_briefing", target="3.5/day")
		await self.announcement_service.log_announcement("morning_briefing", "#general", content)

		# Send to Discord channel if configured
		if settings.general_channel_id:
			channel = self.get_channel(settings.general_channel_id)
			if channel and hasattr(channel, "send"):
				await channel.send(content)
				self.log.info("scheduler.morning_briefing.sent", channel_id=settings.general_channel_id)
		else:
			self.log.info("scheduler.morning_briefing", content=content)

	async def run_evening_summary(self) -> None:
		"""Scheduled evening summary hook."""

		progress = await self.progress_service.overall_progress()
		summary = f"completed={progress['completed']:.1f}, rate={progress['rate']:.1f}%"
		content = self.announcement_service.from_template("evening_summary", summary=summary)
		await self.announcement_service.log_announcement("evening_summary", "#general", content)

		# Send to Discord channel if configured
		if settings.general_channel_id:
			channel = self.get_channel(settings.general_channel_id)
			if channel and hasattr(channel, "send"):
				await channel.send(content)
				self.log.info("scheduler.evening_summary.sent", channel_id=settings.general_channel_id)
		else:
			self.log.info("scheduler.evening_summary", content=content)

	async def monitor_form_versions(self) -> None:
		"""Scheduled form version monitor hook."""

		versions = await self.survey_client.get_form_versions()
		for form, version in versions.items():
			content = self.announcement_service.from_template("form_update", form=form, version=version)
			await self.announcement_service.log_announcement("form_update", "#scto", content)

			# Send to Discord channel if configured
			if settings.scto_channel_id:
				channel = self.get_channel(settings.scto_channel_id)
				if channel and hasattr(channel, "send"):
					await channel.send(content)
					self.log.info("scheduler.form_version_monitor.sent", channel_id=settings.scto_channel_id)

		if not settings.scto_channel_id:
			self.log.info("scheduler.form_version_monitor", forms=len(versions))


async def start_bot() -> None:
	"""Start the Discord bot."""

	configure_logging(settings.log_level)
	if not settings.discord_bot_token:
		raise RuntimeError("DISCORD_BOT_TOKEN is required.")

	bot = FieldAssistBot()
	await bot.start(settings.discord_bot_token)


def main() -> None:
	"""CLI entry for bot startup."""

	asyncio.run(start_bot())


if __name__ == "__main__":
	main()
