"""Unified mention handler — routes @bot messages to the right service."""

import discord
from discord.ext import commands

from src.bot import FieldAssistBot
from src.services.intent_classifier import Intent, IntentClassifier
from src.services.protocol_service import _escalation_mention
from src.utils.formatters import format_case_embed_text, format_progress_text
from src.utils.logger import get_logger

log = get_logger("mention_handler")


def _reply_footer() -> str:
    """Standard footer appended to every bot reply."""
    mention = _escalation_mention()
    return f"\n\n---\n💬 *Not satisfied with this answer? Feel free to reach out to my boss {mention} directly.*"


class MentionCog(commands.Cog):
    """Listens for @bot mentions and intelligently routes to services."""

    def __init__(self, bot: FieldAssistBot) -> None:
        self.bot = bot
        self.classifier = IntentClassifier(bot.openai_client)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Handle all @bot mentions with intent classification."""

        if message.author.bot:
            return
        if self.bot.user is None:
            return
        if not self.bot.user.mentioned_in(message):
            return
        # Ignore @everyone/@here
        if message.mention_everyone:
            return

        question = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
        if not question:
            await message.reply(
                "👋 Hi! You can ask me anything — protocol questions, case lookups, "
                "progress updates, assignments, and more. Just tag me and ask!"
            )
            return

        user_id = str(message.author.id)
        channel = f"#{message.channel.name}" if hasattr(message.channel, "name") else "#dm"

        # Show typing indicator while processing
        async with message.channel.typing():
            intent, param = await self.classifier.classify(question)
            log.info("mention.classified", intent=intent.value, user=user_id, param=param)

            try:
                response = await self._route(intent, question, param, user_id, channel)
            except Exception as e:
                log.error("mention.handler_error", error=str(e), intent=intent.value)
                response = (
                    "⚠️ Something went wrong processing your request. "
                    "Try using a slash command instead, or rephrase your question."
                )

        try:
            await self._send_reply(message, response + _reply_footer())
        except Exception as e:
            log.error("mention.reply_failed", error=str(e), response_length=len(response))

    async def _send_reply(self, message: discord.Message, text: str) -> None:
        """Reply to a message, splitting if it exceeds Discord's 2000-char limit."""

        if len(text) <= 2000:
            await message.reply(text)
            return

        # Split into chunks at newline boundaries
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

    async def _route(
        self,
        intent: Intent,
        question: str,
        param: str | None,
        user_id: str,
        channel: str,
    ) -> str:
        """Route classified intent to the appropriate service."""

        if intent == Intent.GREETING:
            return (
                "👋 Hey! I'm Field Assist Bot. Ask me about:\n"
                "• **Protocol** — survey procedures, field scenarios, questionnaire guidance\n"
                "• **Cases** — look up a case by ID, check status\n"
                "• **Assignments** — who is assigned where\n"
                "• **Progress** — team productivity, completion rates\n"
                "• **Forms** — current form versions\n\n"
                "Just tag me with your question!"
            )

        if intent == Intent.PROTOCOL:
            answer, confidence = await self.bot.protocol_service.answer_question(
                question, user_id=user_id, channel=channel
            )
            return f"{answer}\n\n*Confidence: {confidence.value}*"

        if intent == Intent.CASE_LOOKUP:
            if not param:
                return (
                    "I'd be happy to look up a case! Please include the case ID.\n"
                    "Example: `@Field Assist Bot check case ABC-123`"
                )
            case = await self.bot.case_service.lookup_case(param)
            redacted = self.bot.case_service.redact_pii(case)
            return format_case_embed_text(redacted)

        if intent == Intent.CASE_STATUS:
            if param:
                status = await self.bot.case_service.case_status(param)
                return status
            return (
                "Could you specify a case ID or team name?\n"
                "Example: `@Field Assist Bot status of case ABC-123` "
                "or use `/team_cases <team>`"
            )

        if intent == Intent.ASSIGNMENTS:
            # Try to extract a team name or FO name from the question
            # Fall back to general guidance
            return (
                "For assignments, please use one of these commands:\n"
                "• `/assignments <team_name>` — list assignments for a team\n"
                "• `/where_is <case_id>` — find which team has a case\n"
                "• `/team_for <fo_name>` — find which team an FO belongs to\n\n"
                "Or rephrase your question with a specific team or case ID and tag me again!"
            )

        if intent == Intent.PROGRESS:
            try:
                values = await self.bot.progress_service.overall_progress()
                return format_progress_text(values, "📊 Overall Progress")
            except Exception:
                return (
                    "I couldn't fetch progress data right now. Try:\n"
                    "• `/progress` — overall progress\n"
                    "• `/team_status <team>` — team-specific\n"
                    "• `/fo_productivity <name>` — individual FO"
                )

        if intent == Intent.FORM_VERSION:
            try:
                versions = await self.bot.survey_client.get_form_versions()
                if not versions:
                    return "No form version data available right now."
                lines = [f"**{name}**: {version}" for name, version in versions.items()]
                return "📋 Current Form Versions:\n" + "\n".join(lines)
            except Exception:
                return "I couldn't fetch form versions right now. Try `/form_version`."

        if intent == Intent.ESCALATION:
            escalation_id = await self.bot.escalation_service.create_escalation(
                requester=user_id,
                reason=f"User-requested escalation: {question}",
                channel=channel,
                question=question,
            )
            from src.services.protocol_service import _escalation_mention

            mention = _escalation_mention()
            return (
                f"🔔 I've escalated this to {mention} for review.\n"
                f"Escalation ID: **{escalation_id}**\n\n"
                f"They'll get back to you as soon as possible."
            )

        # UNKNOWN — default to protocol pipeline as a catch-all
        answer, confidence = await self.bot.protocol_service.answer_question(
            question, user_id=user_id, channel=channel
        )
        return f"{answer}\n\n*Confidence: {confidence.value}*"


async def setup(bot: FieldAssistBot) -> None:
    """Load cog into bot instance."""

    await bot.add_cog(MentionCog(bot))
