"""Application configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Runtime settings for all app modules."""

	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	discord_bot_token: str = Field(default="", alias="DISCORD_BOT_TOKEN")
	discord_guild_id: int | None = Field(default=None, alias="DISCORD_GUILD_ID")

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

	bot_admin_channel_id: int = Field(default=0, alias="BOT_ADMIN_CHANNEL_ID")
	general_channel_id: int = Field(default=0, alias="GENERAL_CHANNEL_ID")
	scto_channel_id: int = Field(default=0, alias="SCTO_CHANNEL_ID")
	sra_discord_user_id: int = Field(default=0, alias="SRA_DISCORD_USER_ID")


settings = Settings()
