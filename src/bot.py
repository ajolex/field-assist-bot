"""Discord bot application entry point."""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

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
from src.knowledge.collector import KnowledgeCollector
from src.knowledge.indexer import KnowledgeIndexer
from src.knowledge.retriever import KnowledgeRetriever
from src.services.announcement_service import AnnouncementService
from src.services.assignment_service import AssignmentService
from src.services.case_service import CaseService
from src.services.escalation_service import EscalationService
from src.services.intent_classifier import Intent, IntentClassifier
from src.services.progress_service import ProgressService
from src.services.progress_exceptions_service import ProgressExceptionsService
from src.services.protocol_service import ProtocolService, _escalation_mention
from src.services.remote_automation_service import RemoteAutomationService
from src.services.scheduler_service import SchedulerService
from src.services.issue_triage_service import IssueTriageService
from src.services.surveycto_issue_service import SurveyCTOIssueService
from src.utils.logger import configure_logging, get_logger


COGS = [
	"src.cogs.admin",
	"src.cogs.cases",
	"src.cogs.protocol",
	"src.cogs.progress",
	"src.cogs.assignments",
	"src.cogs.forms",
	"src.cogs.announcements",
	"src.cogs.triage",
	"src.cogs.automation",
	"src.cogs.remote_control",
]


class FieldAssistBot(commands.Bot):
	"""Main Discord bot instance."""

	def __init__(self) -> None:
		intents = discord.Intents.default()
		intents.guild_messages = True
		intents.dm_messages = True
		intents.message_content = True
		super().__init__(command_prefix="!", intents=intents)
		self.log = get_logger("field_assist_bot")
		self.sheets_client = GoogleSheetsClient()
		self.survey_client = SurveyCTOClient()
		self.openai_client = OpenAIClient()

		# Retriever is built async in setup_hook
		self.retriever: KnowledgeRetriever | None = None

		self.interaction_repository = InteractionRepository()
		self.escalation_repository = EscalationRepository()
		self.announcement_repository = AnnouncementRepository()

		self.escalation_service = EscalationService(self.escalation_repository)
		self.case_service = CaseService(self.survey_client, self.escalation_service)
		self.assignment_service = AssignmentService(self.sheets_client)
		self.progress_service = ProgressService(self.sheets_client)
		self.progress_exceptions_service = ProgressExceptionsService(self.sheets_client)
		self.announcement_service = AnnouncementService(self.announcement_repository)
		self.issue_triage_service = IssueTriageService(self.openai_client)
		self.remote_automation_service = RemoteAutomationService(self.survey_client)
		# protocol_service is finalized in setup_hook after async index build
		self.protocol_service: ProtocolService | None = None
		self.scheduler_service = SchedulerService(settings.timezone)
		self.intent_classifier: IntentClassifier | None = None
		self.surveycto_issue_service = SurveyCTOIssueService(self.sheets_client, self.openai_client)
		self._knowledge_docs_seen: set[str] = set()
		self.knowledge_collector = KnowledgeCollector(Path(settings.knowledge_candidates_path))

	async def setup_hook(self) -> None:
		"""Load initial cogs and sync application commands."""

		await init_db()

		# Build/load persistent knowledge index with incremental re-embedding
		indexer = KnowledgeIndexer(
			Path(settings.knowledge_base_path),
			self.openai_client,
			cache_path=Path(settings.knowledge_index_cache_path),
		)
		chunks, index_stats = await indexer.build_index()
		self.retriever = KnowledgeRetriever(chunks, self.openai_client)
		kb_base = Path(settings.knowledge_base_path)
		self._knowledge_docs_seen = {
			path.relative_to(kb_base).as_posix() for path in kb_base.rglob("*.md")
		}
		self.log.info(
			"knowledge.indexed",
			chunk_count=index_stats.chunk_count,
			total_docs=index_stats.total_docs,
			reused_chunks=index_stats.reused_chunks,
			embedded_chunks=index_stats.embedded_chunks,
			changed_docs=index_stats.changed_docs,
			cache_hit=index_stats.cache_hit,
		)

		self.protocol_service = ProtocolService(
			self.retriever,
			self.openai_client,
			self.interaction_repository,
			self.escalation_service,
		)
		self.intent_classifier = IntentClassifier(self.openai_client)
		for cog in COGS:
			await self.load_extension(cog)
		self.scheduler_service.schedule_cron(
			self.run_morning_briefing,
			hour=6,
			minute=30,
			job_id="morning_briefing",
		)
		if settings.morning_greeting_test_delay_minutes > 0:
			test_run_at = datetime.now(ZoneInfo(settings.timezone)) + timedelta(
				minutes=settings.morning_greeting_test_delay_minutes
			)
			self.scheduler_service.schedule_once(
				self.run_morning_briefing,
				run_date=test_run_at,
				job_id="morning_briefing_test_once",
			)
			self.log.info(
				"scheduler.morning_briefing_test_scheduled",
				run_at=test_run_at.isoformat(),
				minutes=settings.morning_greeting_test_delay_minutes,
			)
		self.scheduler_service.schedule_cron(
			self.run_evening_summary,
			hour=19,
			minute=0,
			job_id="evening_summary",
		)
		self.scheduler_service.schedule_cron(
			self.run_progress_exceptions,
			hour=settings.progress_exceptions_hour,
			minute=settings.progress_exceptions_minute,
			job_id="progress_exceptions",
		)
		self.scheduler_service.schedule_cron(
			self.monitor_form_versions,
			hour=0,
			minute=30,
			job_id="form_version_monitor",
		)
		if settings.auto_reindex_on_new_docs:
			self.scheduler_service.schedule_interval(
				self.check_knowledge_base_updates,
				minutes=max(settings.knowledge_scan_interval_minutes, 10),
				job_id="knowledge_new_doc_scan",
			)
		guild_ids = settings.discord_guild_ids
		if guild_ids:
			for guild_id in guild_ids:
				guild = discord.Object(id=guild_id)
				self.tree.copy_global_to(guild=guild)
				try:
					await self.tree.sync(guild=guild)
					self.log.info("commands.synced", scope="guild", guild_id=guild_id)
				except discord.Forbidden:
					self.log.warning(
						"commands.guild_sync_failed",
						guild_id=guild_id,
						message="Skipping guild sync — ensure bot has applications.commands scope in this guild",
					)
			await self.tree.sync()
			self.log.info("commands.synced", scope="global_backup")
		else:
			await self.tree.sync()
			self.log.info("commands.synced", scope="global")

	async def on_ready(self) -> None:
		"""Log readiness after gateway connection."""

		self.log.info("bot.ready", user=str(self.user), user_id=getattr(self.user, "id", None))
		self.scheduler_service.start()

	async def on_message(self, message: discord.Message) -> None:
		"""Handle @mentions with intelligent intent routing."""
		self.log.info(
			"message.received",
			author_id=str(message.author.id),
			is_bot=message.author.bot,
			channel_id=str(getattr(message.channel, "id", "")),
			raw_mentions=getattr(message, "raw_mentions", []),
			raw_role_mentions=getattr(message, "raw_role_mentions", []),
			preview=message.content[:120],
		)

		if message.author.bot or self.user is None:
			return
		await self._maybe_collect_knowledge_candidate(message)
		content_lower = message.content.lower()
		bot_name = (self.user.display_name or self.user.name).lower()
		mention_by_entity = self.user.id in message.raw_mentions
		mention_by_token = (
			f"<@{self.user.id}>" in message.content
			or f"<@!{self.user.id}>" in message.content
		)
		mention_by_name = f"@{bot_name}" in content_lower
		mention_by_role = any(
			bot_name in role.name.lower() for role in getattr(message, "role_mentions", [])
		)

		if not (mention_by_entity or mention_by_token or mention_by_name or mention_by_role):
			return
		if message.mention_everyone:
			return

		question = message.content
		question = question.replace(f"<@{self.user.id}>", "")
		question = question.replace(f"<@!{self.user.id}>", "")
		question = question.strip()
		if message.attachments:
			attachment_lines = [
				f"- {attachment.filename}: {attachment.url}" for attachment in message.attachments
			]
			question = f"{question}\n\nAttachments:\n" + "\n".join(attachment_lines)

			image_urls = [
				attachment.url
				for attachment in message.attachments
				if (attachment.content_type or "").startswith("image/")
				or attachment.filename.lower().endswith(
					(".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")
				)
			]
			if image_urls:
				image_instruction = (
					"Extract useful troubleshooting context from these screenshots: "
					"visible error messages, variable/question names, labels, "
					"skip/relevance hints, and any values shown. Keep concise."
				)
				image_context = await self.openai_client.extract_image_context(
					image_urls=image_urls,
					instruction=image_instruction,
				)
				if image_context:
					question += f"\n\nScreenshot context:\n{image_context}"
		if not question:
			await message.reply(
				"\U0001f44b Hi! You can ask me anything \u2014 protocol questions, case lookups, "
				"progress updates, assignments, and more. Just tag me and ask!"
			)
			return

		user_id = str(message.author.id)
		channel = f"#{message.channel.name}" if hasattr(message.channel, "name") else "#dm"
		mention = _escalation_mention()
		footer = f"\n\n---\n\U0001f4ac *Not satisfied with this answer? Feel free to reach out to my boss {mention} directly.*"

		self.log.info("mention.received", user=user_id, question=question[:80])

		try:
			async with message.channel.typing():
				response = await self._handle_mention(question, user_id, channel)
			await self._send_reply(message, response + footer)
		except Exception as e:
			self.log.error("mention.error", error=str(e))
			await message.reply("\u26a0\ufe0f Something went wrong. Try a slash command or rephrase your question.")

	async def on_error(self, event_method: str, *args, **kwargs) -> None:
		"""Log unhandled event errors for faster troubleshooting."""

		self.log.exception("discord.event_error", event_method=event_method)

	async def _handle_mention(
		self, question: str, user_id: str, channel: str
	) -> str:
		"""Classify intent and route to the right service."""

		intent, param = await self.intent_classifier.classify(question)
		self.log.info("mention.classified", intent=intent.value, param=param)

		if intent == Intent.GREETING:
			return (
				"👋 Hey! I'm Field Assist Bot — Aubrey's assistant. Ask me about:\n"
				"• **Protocol** — survey procedures, field scenarios\n"
				"• **SurveyCTO Issues** — skip logic/relevance/constraint troubleshooting\n"
				"• **Cases** — look up a case by ID\n"
				"• **Assignments** — who is assigned where\n"
				"• **Progress** — team productivity\n"
				"• **Forms** — current form versions\n\n"
				"Just tag me with your question! Halong! 🙌"
			)

		if intent == Intent.CASE_LOOKUP and param:
			from src.utils.formatters import format_case_embed_text
			case = await self.case_service.lookup_case(param)
			redacted = self.case_service.redact_pii(case)
			return format_case_embed_text(redacted)

		if intent == Intent.CASE_STATUS and param:
			return await self.case_service.case_status(
				param,
				requester=user_id,
				channel=channel,
				request_text=question,
			)

		if intent == Intent.PROGRESS:
			from src.utils.formatters import format_progress_text
			values = await self.progress_service.overall_progress()
			return format_progress_text(values, "\U0001f4ca Overall Progress")

		if intent == Intent.FORM_VERSION:
			versions = await self.get_form_versions()
			if not versions:
				return "No form version data available right now."
			lines = [f"**{name}**: {version}" for name, version in versions.items()]
			return "\U0001f4cb Current Form Versions:\n" + "\n".join(lines)

		if intent == Intent.SURVEYCTO_ISSUE:
			diagnosis = await self.surveycto_issue_service.diagnose(question)
			escalation_details = diagnosis.escalation_payload(
				reporter=user_id,
				user_description=question,
			)
			escalation_id = await self.escalation_service.create_escalation(
				requester=user_id,
				reason=(
					f"SurveyCTO issue ({diagnosis.issue_type}) "
					f"variable={diagnosis.variable_name} form={diagnosis.form_name}"
				),
				channel=channel,
				question=escalation_details,
			)
			mention = _escalation_mention()
			return (
				f"{diagnosis.fo_response()}\n\n"
				f"\U0001f514 I've escalated this to {mention} for a form fix review "
				f"(Escalation ID: **{escalation_id}**)."
			)

		if intent == Intent.ESCALATION:
			escalation_id = await self.escalation_service.create_escalation(
				requester=user_id,
				reason=f"User-requested escalation: {question}",
				channel=channel,
				question=question,
			)
			mention = _escalation_mention()
			return (
				f"\U0001f514 I've escalated this to {mention} for review.\n"
				f"Escalation ID: **{escalation_id}**"
			)

		# Default: protocol pipeline (covers PROTOCOL, ASSIGNMENTS, UNKNOWN, etc.)
		answer, confidence = await self.protocol_service.answer_question(
			question, user_id=user_id, channel=channel
		)
		return f"{answer}\n\n*Confidence: {confidence.value}*"

	async def _send_reply(self, message: discord.Message, text: str) -> None:
		"""Reply, splitting if over Discord's 2000-char limit."""

		if len(text) <= 2000:
			await message.reply(text)
			return
		chunks: list[str] = []
		current = ""
		for line in text.split("\n"):
			if len(current) + len(line) + 1 > 1990:
				chunks.append(current)
				current = line
			else:
				current = f"{current}\n{line}" if current else line
		if current:
			chunks.append(current)
		for i, chunk in enumerate(chunks):
			if i == 0:
				await message.reply(chunk)
			else:
				await message.channel.send(chunk)

	async def _maybe_collect_knowledge_candidate(self, message: discord.Message) -> None:
		"""Capture potentially reusable knowledge from normal chat messages."""

		if not settings.passive_learning_enabled:
			return
		if not message.content.strip():
			return
		if not self.knowledge_collector.should_capture(message.content):
			return

		candidate = self.knowledge_collector.build_candidate(
			message_id=message.id,
			author_id=message.author.id,
			channel_id=message.channel.id,
			content=message.content,
		)
		await self.knowledge_collector.persist(candidate)
		self.log.info(
			"knowledge.candidate.captured",
			candidate_id=candidate.candidate_id,
			message_id=message.id,
		)
		try:
			await message.add_reaction(settings.passive_learning_reaction)
		except (discord.Forbidden, discord.HTTPException):
			self.log.warning("knowledge.candidate.reaction_failed", message_id=message.id)

	async def close(self) -> None:
		"""Close bot and shutdown scheduler."""

		self.scheduler_service.shutdown()
		await super().close()

	async def run_morning_briefing(self) -> None:
		"""Scheduled morning briefing hook."""

		content = settings.morning_greeting_message
		await self.announcement_service.log_announcement("morning_briefing", "#general", content)

		# Send to Discord channel if configured
		if settings.general_channel_id:
			channel = self.get_channel(settings.general_channel_id)
			if channel and hasattr(channel, "send"):
				await channel.send(
					content,
					allowed_mentions=discord.AllowedMentions(everyone=True),
				)
				self.log.info("scheduler.morning_briefing.sent", channel_id=settings.general_channel_id)
				return

		self.log.info("scheduler.morning_briefing", content=content)

	async def check_knowledge_base_updates(self) -> None:
		"""Reindex only when new markdown files are added to KB directory."""

		kb_path = Path(settings.knowledge_base_path)
		current_docs = {path.relative_to(kb_path).as_posix() for path in kb_path.rglob("*.md")}
		new_docs = current_docs - self._knowledge_docs_seen
		if not new_docs:
			self.log.info("knowledge.scan.no_new_docs", scanned_docs=len(current_docs))
			return

		self.log.info("knowledge.scan.new_docs_found", count=len(new_docs), docs=sorted(new_docs))
		indexer = KnowledgeIndexer(
			kb_path,
			self.openai_client,
			cache_path=Path(settings.knowledge_index_cache_path),
		)
		chunks, stats = await indexer.build_index()
		self.retriever = KnowledgeRetriever(chunks, self.openai_client)
		if self.protocol_service is not None:
			self.protocol_service.retriever = self.retriever
		self._knowledge_docs_seen = current_docs
		self.log.info(
			"knowledge.reindexed_on_new_docs",
			chunk_count=stats.chunk_count,
			reused_chunks=stats.reused_chunks,
			embedded_chunks=stats.embedded_chunks,
			changed_docs=stats.changed_docs,
		)

	async def get_form_versions(self) -> dict[str, str]:
		"""Get form versions from SurveyCTO Google Sheet Settings tabs."""

		versions = await self.sheets_client.read_form_versions_from_settings()
		if versions:
			return versions

		self.log.warning("form_versions.settings_tab_empty_or_unavailable")
		return {}

	async def run_evening_summary(self) -> None:
		"""Scheduled evening summary hook."""

		content = settings.evening_greeting_message
		await self.announcement_service.log_announcement("evening_summary", "#general", content)

		# Send to Discord channel if configured
		if settings.general_channel_id:
			channel = self.get_channel(settings.general_channel_id)
			if channel and hasattr(channel, "send"):
				await channel.send(
					content,
					allowed_mentions=discord.AllowedMentions(everyone=True, users=True),
				)
				self.log.info("scheduler.evening_summary.sent", channel_id=settings.general_channel_id)
		else:
			self.log.info("scheduler.evening_summary", content=content)

	async def monitor_form_versions(self) -> None:
		"""Scheduled form version monitor hook."""

		versions = await self.get_form_versions()
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

	async def run_progress_exceptions(self) -> None:
		"""Post nightly productivity anomalies only (no dashboard dump)."""

		report = await self.progress_exceptions_service.build_nightly_report()
		if not report.has_anomalies:
			self.log.info("scheduler.progress_exceptions.none")
			return

		channel_id = settings.progress_exceptions_channel_id or settings.general_channel_id
		if channel_id:
			channel = self.get_channel(channel_id)
			if channel and hasattr(channel, "send"):
				await channel.send(
					report.text,
					allowed_mentions=discord.AllowedMentions(everyone=True, roles=True, users=True),
				)
				self.log.info("scheduler.progress_exceptions.sent", channel_id=channel_id)
				return

		self.log.info("scheduler.progress_exceptions.fallback", preview=report.text[:400])


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
