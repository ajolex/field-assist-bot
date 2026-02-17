"""Protocol Q&A command handlers."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot
from src.services.protocol_service import _escalation_mention


class ProtocolCog(commands.Cog):
	"""Handles protocol slash command and mention-based Q&A."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="protocol", description="Ask a protocol question")
	async def protocol(self, interaction: discord.Interaction, question: str) -> None:
		"""Answer protocol question with confidence tag."""

		await interaction.response.defer()
		user_id = str(interaction.user.id)
		channel = f"#{interaction.channel.name}" if interaction.channel else "#unknown"
		answer, confidence = await self.bot.protocol_service.answer_question(
			question, user_id=user_id, channel=channel
		)
		await interaction.followup.send(
			f"{answer}\n\nConfidence: {confidence.value}"
			f"\n\n---\n💬 *Not satisfied with this answer? Feel free to reach out to my boss {_escalation_mention()} directly.*"
		)


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(ProtocolCog(bot))
