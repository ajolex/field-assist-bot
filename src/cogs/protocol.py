"""Protocol Q&A command handlers."""

import discord
from discord import app_commands
from discord.ext import commands

from src.bot import FieldAssistBot


class ProtocolCog(commands.Cog):
	"""Handles protocol slash command and mention-based Q&A."""

	def __init__(self, bot: FieldAssistBot) -> None:
		self.bot = bot

	@app_commands.command(name="protocol", description="Ask a protocol question")
	async def protocol(self, interaction: discord.Interaction, question: str) -> None:
		"""Answer protocol question with confidence tag."""

		answer, confidence = await self.bot.protocol_service.answer_question(question)
		await interaction.response.send_message(f"{answer}\n\nConfidence: {confidence.value}")

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message) -> None:
		"""Answer natural language questions when bot is mentioned."""

		if message.author.bot:
			return
		if self.bot.user is None:
			return
		if self.bot.user.mentioned_in(message):
			question = message.content.replace(self.bot.user.mention, "").strip()
			if not question:
				return
			answer, confidence = await self.bot.protocol_service.answer_question(question)
			await message.reply(f"{answer}\nConfidence: {confidence.value}")


async def setup(bot: FieldAssistBot) -> None:
	"""Load cog into bot instance."""

	await bot.add_cog(ProtocolCog(bot))
