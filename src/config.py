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
	google_form_hh_survey_sheet_id: str = Field(default="", alias="GOOGLE_FORM_HH_SURVEY_SHEET_ID")
	google_form_icm_business_sheet_id: str = Field(
		default="", alias="GOOGLE_FORM_ICM_BUSINESS_SHEET_ID"
	)
	google_form_phase_a_revisit_sheet_id: str = Field(
		default="", alias="GOOGLE_FORM_PHASE_A_REVISIT_SHEET_ID"
	)

	surveycto_server_name: str = Field(default="", alias="SURVEYCTO_SERVER_NAME")
	surveycto_username: str = Field(default="", alias="SURVEYCTO_USERNAME")
	surveycto_password: str = Field(default="", alias="SURVEYCTO_PASSWORD")
	surveycto_cases_data_id: str = Field(default="", alias="SURVEYCTO_CASES_DATA_ID")
	surveycto_cases_form_id: str = Field(default="cases_icm", alias="SURVEYCTO_CASES_FORM_ID")
	surveycto_cases_csv_path: str = Field(
		default=".cache/cases_icm.csv",
		alias="SURVEYCTO_CASES_CSV_PATH",
	)

	database_url: str = Field(default="sqlite+aiosqlite:///./field_assist.db", alias="DATABASE_URL")

	environment: str = Field(default="development", alias="ENVIRONMENT")
	log_level: str = Field(default="INFO", alias="LOG_LEVEL")
	timezone: str = Field(default="Asia/Manila", alias="TIMEZONE")

	# Discord channel IDs
	bot_admin_channel_id: int = Field(default=0, alias="BOT_ADMIN_CHANNEL_ID")
	general_channel_id: int = Field(default=0, alias="GENERAL_CHANNEL_ID")
	scto_channel_id: int = Field(default=0, alias="SCTO_CHANNEL_ID")
	sra_discord_user_id: int = Field(default=0, alias="SRA_DISCORD_USER_ID")
	fm_role_id: int = Field(default=0, alias="FM_ROLE_ID")
	fc_role_id: int = Field(default=0, alias="FC_ROLE_ID")
	progress_exceptions_channel_id: int = Field(default=0, alias="PROGRESS_EXCEPTIONS_CHANNEL_ID")
	progress_exceptions_hour: int = Field(default=19, alias="PROGRESS_EXCEPTIONS_HOUR")
	progress_exceptions_minute: int = Field(default=30, alias="PROGRESS_EXCEPTIONS_MINUTE")
	progress_exception_min_target: float = Field(default=2.0, alias="PROGRESS_EXCEPTION_MIN_TARGET")
	progress_exception_drop_threshold: float = Field(
		default=1.0,
		alias="PROGRESS_EXCEPTION_DROP_THRESHOLD",
	)
	progress_snapshots_path: str = Field(
		default=".cache/progress_snapshots.jsonl",
		alias="PROGRESS_SNAPSHOTS_PATH",
	)

	issue_records_path: str = Field(default=".cache/field_issues.json", alias="ISSUE_RECORDS_PATH")
	issue_status_log_path: str = Field(
		default=".cache/issue_status_log.jsonl",
		alias="ISSUE_STATUS_LOG_PATH",
	)
	default_issue_owner: str = Field(default="FC", alias="DEFAULT_ISSUE_OWNER")

	# Remote control — private automation channel
	automation_channel_id: int = Field(default=0, alias="AUTOMATION_CHANNEL_ID")
	remote_screenshot_quality: int = Field(default=70, alias="REMOTE_SCREENSHOT_QUALITY")
	remote_file_max_mb: int = Field(default=25, alias="REMOTE_FILE_MAX_MB")
	remote_cmd_timeout: int = Field(default=60, alias="REMOTE_CMD_TIMEOUT")

	stata_executable: str = Field(default="stata-mp", alias="STATA_EXECUTABLE")
	stata_run_timeout_seconds: int = Field(default=1800, alias="STATA_RUN_TIMEOUT_SECONDS")
	surveycto_sctoapi_date: int = Field(default=0, alias="SURVEYCTO_SCTOAPI_DATE")
	remote_jobs_log_path: str = Field(default=".cache/remote_jobs_log.jsonl", alias="REMOTE_JOBS_LOG_PATH")
	surveycto_form_household_id: str = Field(
		default="ICM_follow_up_launch_integrated",
		alias="SURVEYCTO_FORM_HOUSEHOLD_ID",
	)
	surveycto_form_business_id: str = Field(
		default="ICM_Business_linked_launch",
		alias="SURVEYCTO_FORM_BUSINESS_ID",
	)
	surveycto_household_csv_path: str = Field(
		default=(
			"F:/10_Livelihood/PSPS ICM Livelihoods Study/10_ICM Follow up survey/"
			"Data Management System/ICM Household survey/4_data/2_survey/"
			"ICM_follow_up_launch_integrated_WIDE.csv"
		),
		alias="SURVEYCTO_HOUSEHOLD_CSV_PATH",
	)
	surveycto_business_csv_path: str = Field(
		default=(
			"F:/10_Livelihood/PSPS ICM Livelihoods Study/10_ICM Follow up survey/"
			"Data Management System/ICM Business module/4_data/2_survey/"
			"ICM_Business_linked_launch_WIDE.csv"
		),
		alias="SURVEYCTO_BUSINESS_CSV_PATH",
	)
	stata_household_master_do_path: str = Field(
		default=(
			"C:/Users/AJolex/Box/"
			"16566_psps_international_care_ministries_livelihoods/"
			"06_Data_Management_System/ICM_Household_survey/0_master.do"
		),
		alias="STATA_HOUSEHOLD_MASTER_DO_PATH",
	)
	stata_business_master_do_path: str = Field(
		default=(
			"C:/Users/AJolex/Box/"
			"16566_psps_international_care_ministries_livelihoods/"
			"06_Data_Management_System/ICM_Business_module/0_master.do"
		),
		alias="STATA_BUSINESS_MASTER_DO_PATH",
	)
	surveycto_form_phase_a_id: str = Field(
		default="phase_a_revisit",
		alias="SURVEYCTO_FORM_PHASE_A_ID",
	)
	surveycto_phase_a_csv_path: str = Field(
		default=(
			"F:/10_Livelihood/PSPS ICM Livelihoods Study/10_ICM Follow up survey/"
			"Data Management System/Phase A revisit/4_data/2_survey/"
			"phase_a_revisit_WIDE.csv"
		),
		alias="SURVEYCTO_PHASE_A_CSV_PATH",
	)

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

	@property
	def surveycto_form_sheet_ids(self) -> dict[str, str]:
		"""Configured SurveyCTO form sheet IDs keyed by form name."""

		forms = {
			"hh_survey": self.google_form_hh_survey_sheet_id,
			"icm_business": self.google_form_icm_business_sheet_id,
			"phase_a_revisit": self.google_form_phase_a_revisit_sheet_id,
		}
		return {name: sheet_id for name, sheet_id in forms.items() if sheet_id.strip()}

	@property
	def field_manager_role_id(self) -> int:
		"""Preferred role ID for productivity exception tagging."""

		return self.fm_role_id or self.fc_role_id

	@property
	def surveycto_cases_source_id(self) -> str:
		"""Primary cases source ID, preferring dataset variable name."""

		return self.surveycto_cases_data_id.strip() or self.surveycto_cases_form_id.strip()


settings = Settings()