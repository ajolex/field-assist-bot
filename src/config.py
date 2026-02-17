"""Application configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Runtime settings for all app modules."""

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	discord_bot_token: str = Field(default="", alias="DISCORD_BOT_TOKEN")
	discord_guild_id: int | None = Field(default=None, alias="DISCORD_GUILD_ID")
	discord_guild_ids_raw: str = Field(default="", alias="DISCORD_GUILD_IDS")

	# Escalation — ALL escalations go to this single Discord user
	escalation_discord_user_id: int | None = Field(
		default=None, alias="ESCALATION_DISCORD_USER_ID"
	)
	escalation_discord_username: str = Field(
		default="ajolex0306", alias="ESCALATION_DISCORD_USERNAME"
	)
	escalation_display_name: str = Field(
		default="Aubrey", alias="ESCALATION_DISPLAY_NAME"
	)

	openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
	openai_model_primary: str = Field(default="gpt-4o", alias="OPENAI_MODEL_PRIMARY")
	openai_model_fallback: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL_FALLBACK")
	openai_embedding_model: str = Field(
		default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
	)

	google_service_account_json: str = Field(default="", alias="GOOGLE_SERVICE_ACCOUNT_JSON")
	google_assignments_sheet_id: str = Field(default="", alias="GOOGLE_ASSIGNMENTS_SHEET_ID")
	google_productivity_sheet_id: str = Field(default="", alias="GOOGLE_PRODUCTIVITY_SHEET_ID")

	surveycto_server_name: str = Field(default="", alias="SURVEYCTO_SERVER_NAME")
	surveycto_username: str = Field(default="", alias="SURVEYCTO_USERNAME")
	surveycto_password: str = Field(default="", alias="SURVEYCTO_PASSWORD")

	database_url: str = Field(default="sqlite+aiosqlite:///./field_assist.db", alias="DATABASE_URL")

	environment: str = Field(default="development", alias="ENVIRONMENT")
	log_level: str = Field(default="INFO", alias="LOG_LEVEL")
	timezone: str = Field(default="Asia/Manila", alias="TIMEZONE")

	# Discord channel IDs
	bot_admin_channel_id: int = Field(default=0, alias="BOT_ADMIN_CHANNEL_ID")
	general_channel_id: int = Field(default=0, alias="GENERAL_CHANNEL_ID")
	scto_channel_id: int = Field(default=0, alias="SCTO_CHANNEL_ID")
	sra_discord_user_id: int = Field(default=0, alias="SRA_DISCORD_USER_ID")

	# Knowledge index settings
	knowledge_base_path: str = Field(default="docs/knowledge_base", alias="KNOWLEDGE_BASE_PATH")
	knowledge_index_cache_path: str = Field(
		default=".cache/knowledge_index.pkl", alias="KNOWLEDGE_INDEX_CACHE_PATH"
	)
	auto_reindex_on_new_docs: bool = Field(default=True, alias="AUTO_REINDEX_ON_NEW_DOCS")
	knowledge_scan_interval_minutes: int = Field(
		default=30, alias="KNOWLEDGE_SCAN_INTERVAL_MINUTES"
	)
	passive_learning_enabled: bool = Field(default=True, alias="PASSIVE_LEARNING_ENABLED")
	knowledge_candidates_path: str = Field(
		default=".cache/knowledge_candidates.jsonl", alias="KNOWLEDGE_CANDIDATES_PATH"
	)
	passive_learning_reaction: str = Field(default="❤️", alias="PASSIVE_LEARNING_REACTION")
	knowledge_promotion_doc: str = Field(
		default="learned_from_chat.md", alias="KNOWLEDGE_PROMOTION_DOC"
	)
	morning_greeting_message: str = Field(
		default=(
			"Good Morning @everyone, I am Aubrey's Assistant (AI). I am here to help to you "
			"when my boss is still sleeping or busy. Just tag me and ask any question, "
			"I will respond to the best of my knowledge. And I will also escalate to Aubrey "
			"those that I cannot answer. Good luck! and Halong!"
		),
		alias="MORNING_GREETING_MESSAGE",
	)
	morning_greeting_test_delay_minutes: int = Field(
		default=0, alias="MORNING_GREETING_TEST_DELAY_MINUTES"
	)
	evening_greeting_message: str = Field(
		default=(
			"Good evening @everyone, good job today!. Just a friendly reminder, "
			"please make sure you submit all your completed forms, so that @Aubrey can "
			"check your productivity and the data. Good night wishes from Manila!"
		),
		alias="EVENING_GREETING_MESSAGE",
	)

	@property
	def discord_guild_ids(self) -> list[int]:
		"""Parse optional comma-separated guild IDs, with single-ID fallback."""

		ids: list[int] = []
		if self.discord_guild_ids_raw.strip():
			for value in self.discord_guild_ids_raw.split(","):
				cleaned = value.strip()
				if cleaned:
					try:
						ids.append(int(cleaned))
					except ValueError:
						continue
		if ids:
			return ids
		return [self.discord_guild_id] if self.discord_guild_id else []


settings = Settings()