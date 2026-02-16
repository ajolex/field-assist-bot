Field-Assist-Bot — Implementation Plan
Executive Summary
Build an AI-powered Discord bot for IPA Philippines field research operations that automates case management, answers protocol questions, provides real-time progress updates, and reduces the Senior Research Associate's manual workload by ~70%. The bot integrates Discord, Google Sheets, SurveyCTO, and an LLM-backed knowledge base.

Architecture
Code
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DISCORD (User Interface)                           │
│                                                                                 │
│  #general    #scto    #mop-up    #team-a    #team-b    ...    #bot-admin        │
│                                                                                 │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          DISCORD GATEWAY LAYER                                  │
│                                                                                 │
│  discord.py 2.x  ·  Slash commands  ·  Message listener  ·  Event handlers     │
│  Rate limiter  ·  Permission checks  ·  Channel router                          │
│                                                                                 │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            COMMAND ROUTER                                        │
│                                                                                 │
│  Classifies incoming messages/commands into:                                    │
│                                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Slash Cmds   │  │  @bot Mention│  │  Scheduled   │  │  Admin Cmds  │        │
│  │  /check_case  │  │  Natural lang│  │  Cron jobs   │  │  /reload_kb  │        │
│  │  /progress    │  │  protocol Q&A│  │  daily posts │  │  /set_version│        │
│  │  /team_status │  │  fuzzy match │  │  alerts      │  │  /escalate   │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                 │                  │                 │                 │
└─────────┼─────────────────┼──────────────────┼─────────────────┼────────────────┘
          │                 │                  │                 │
          ▼                 ▼                  ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CORE SERVICE LAYER                                     │
│                                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌────────────────────────┐  │
│  │  CaseService         │  │  ProtocolService     │  │  SchedulerService      │  │
│  │                      │  │                      │  │                        │  │
│  │  - lookup_case()     │  │  - answer_question() │  │  - morning_briefing()  │  │
│  │  - check_status()    │  │  - search_kb()       │  │  - evening_summary()   │  │
│  │  - list_team_cases() │  │  - get_confidence()  │  │  - version_monitor()   │  │
│  │  - get_assignments() │  │  - escalate()        │  │  - productivity_post() │  │
│  │  - request_reopen()  │  │  - log_interaction() │  │  - schedule_job()      │  │
│  └──��───────┬───────────┘  └──────────┬───────────┘  └───────────┬────────────┘  │
│             │                         │                          │               │
│  ┌──────────┴───────────┐  ┌──────────┴───────────┐  ┌──────────┴────────────┐  │
│  │  ProgressService     │  │  AnnouncementService  │  │  EscalationService    │  │
│  │                      │  │                       │  │                       │  │
│  │  - team_progress()   │  │  - form_update()      │  │  - evaluate_conf()    │  │
│  │  - fo_productivity() │  │  - case_upload()      │  │  - route_to_human()   │  │
│  │  - daily_summary()   │  │  - safety_alert()     │  │  - log_escalation()   │  │
│  │  - completion_rate() │  │  - from_template()    │  │  - track_resolution() │  │
│  └──────────┬───────────┘  └───────────┬───────────┘  └───────────┬───────────┘  │
│             │                          │                          │              │
└─────────────┼──────────────────────────┼──────────────────────────┼──────────────┘
              │                          │                          │
              ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA ACCESS LAYER                                        │
│                                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐              │
│  │  GoogleSheetsAPI  │  │  SurveyCTOAPI    │  │  KnowledgeBase   │              │
│  │                   │  │                  │  │                  │              │
│  │  - read_tracker() │  │  - get_cases()   │  │  - vector_store  │              │
│  │  - read_assign()  │  │  - get_forms()   │  │  - search()      │              │
│  │  - read_progress()│  │  - get_versions()│  │  - reindex()     │              │
│  │  - write_log()    │  │  - get_submits() │  │  - get_context() │              │
│  │                   │  │                  │  │                  │              │
│  │  gspread +        │  │  REST API +      │  │  ChromaDB/FAISS +│              │
│  │  google-auth      │  │  httpx/aiohttp   │  │  OpenAI Embeds   │              │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘              │
│           │                     │                      │                        │
│           ▼                     ▼                      ▼                        │
│  ┌──────────────────────────────────────────────────────────────────┐           │
│  │                      CACHE LAYER (Redis / In-Memory)             │           │
│  │                                                                  │           │
│  │  TTL-based caching for:                                         │           │
│  │  - Case lookups (5 min TTL)                                     │           │
│  │  - Team assignments (30 min TTL)                                │           │
│  │  - Form versions (10 min TTL)                                   │           │
│  │  - Productivity data (15 min TTL)                               │           │
│  └──────────────────────────────────────────────────────────────────┘           │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────┐           │
│  │                      DATABASE (SQLite → PostgreSQL)               │           │
│  │                                                                  │           │
│  │  Tables:                                                        │           │
│  │  - interactions (question, answer, confidence, escalated, ts)   │           │
│  │  - escalations (case_id, requester, reason, status, resolver)   │           │
│  │  - announcements (type, channel, content, sent_at)              │           │
│  │  - form_versions (form_id, version, detected_at, announced)     │           │
│  │  - reopen_requests (case_id, requester, reason, status)         │           │
│  └───────────────────���──────────────────────────────────────────────┘           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           LLM LAYER                                             │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────┐              │
│  │  RAG Pipeline (Retrieval-Augmented Generation)                │              │
│  │                                                               │              │
│  │  1. Incoming question                                         │              │
│  │  2. Embed question → vector search knowledge base             │              │
│  │  3. Retrieve top-k relevant chunks from:                      │              │
│  │     - protocol.md                                             │              │
│  │     - psps_questionnaire_guide.md                             │              │
│  │     - faq_field_scenarios.md                                  │              │
│  │     - case_status_rules.md                                    │              │
│  │     - case_pipeline.md                                        │              │
│  │     - known_issues_and_fixes.md                               │              │
│  │     - data_quality_rules.md                                   │              │
│  │     - bot_escalation_rules.md                                 │              │
│  │     - announcement_templates.md                               │              │
│  │     - deployment_schedule.md                                  │              │
│  │  4. Construct prompt: system prompt + retrieved context + Q   │              │
│  │  5. LLM generates answer + confidence score                   │              │
│  │  6. Apply escalation rules based on confidence                │              │
│  │                                                               │              │
│  │  Model: OpenAI GPT-4o (primary) / GPT-4o-mini (fallback)     │              │
│  │  Embeddings: text-embedding-3-small                           │              │
│  └───────────────────────────────────────────────────────────────┘              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
Repository Structure
Code
field-assist-bot/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint, test, type-check on PR
│       ├── deploy.yml                # Auto-deploy on merge to main
│       └── kb-index.yml              # Re-index knowledge base on docs change
│
├── docs/
│   └── knowledge_base/
│       ├── protocol.md
│       ├── psps_questionnaire_guide.md
│       ├── case_status_rules.md
│       ├── case_pipeline.md
│       ├── deployment_schedule.md
│       ├── known_issues_and_fixes.md
│       ├── data_quality_rules.md
│       ├── faq_field_scenarios.md
│       ├── bot_escalation_rules.md
│       └── announcement_templates.md
│
├── src/
│   ├── __init__.py
│   ├── bot.py                        # Bot entry point, event loop, cog loading
│   ├── config.py                     # Settings via pydantic-settings + .env
│   │
│   ├── cogs/                         # Discord command groups (modular)
│   │   ├── __init__.py
│   │   ├── cases.py                  # /check_case, /reopen_request, /case_status
│   │   ├── protocol.py              # /protocol, @bot natural language Q&A
│   │   ├── progress.py              # /progress, /team_status, /fo_productivity
│   │   ├── assignments.py           # /assignments, /where_is, /team_for
│   │   ├── forms.py                 # /form_version, /form_changelog
│   │   ├── announcements.py         # /announce, /morning_briefing (manual triggers)
│   │   └── admin.py                 # /reload_kb, /set_version, /bot_stats, /escalation_log
│   │
│   ├── services/                     # Business logic (no Discord dependency)
│   │   ├── __init__.py
│   │   ├── case_service.py
│   │   ├── protocol_service.py
│   │   ├── progress_service.py
│   │   ├── assignment_service.py
│   │   ├── announcement_service.py
│   │   ├── escalation_service.py
│   │   └── scheduler_service.py
│   │
│   ├── integrations/                 # External API clients
│   │   ├── __init__.py
│   │   ├── google_sheets.py          # gspread async wrapper
│   │   ├── surveycto.py              # SurveyCTO REST API client
│   │   └── openai_client.py          # LLM + embedding calls
│   │
│   ├── knowledge/                    # RAG pipeline
│   │   ├── __init__.py
│   │   ├── indexer.py                # Chunk + embed + store documents
│   │   ├── retriever.py             # Vector search + re-ranking
│   │   ├── prompt_builder.py        # System prompt + context assembly
│   │   └── confidence.py            # Confidence scoring + escalation logic
│   │
│   ├── models/                       # Data models (Pydantic + SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── case.py
│   │   ├── interaction.py
│   │   ├── escalation.py
│   │   ├── announcement.py
│   │   └── form_version.py
│   │
│   ├── db/                           # Database
│   │   ├── __init__.py
│   │   ├── engine.py                 # Async SQLAlchemy engine
│   │   ├── migrations/               # Alembic migrations
│   │   └── repositories/             # Data access layer
│   │       ├── interaction_repo.py
│   │       ├── escalation_repo.py
│   │       └── announcement_repo.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py             # Discord embed builders, table formatters
│       ├── permissions.py            # Role-based access (SRA, FC, FO)
│       ├── rate_limiter.py           # Per-user rate limiting
│       └── logger.py                 # Structured logging
│
├── tests/
│   ├── unit/
│   │   ├── test_case_service.py
│   │   ├── test_protocol_service.py
│   │   ├── test_progress_service.py
│   │   ├── test_confidence.py
│   │   └── test_prompt_builder.py
│   ├── integration/
│   │   ├── test_google_sheets.py
│   │   ├── test_surveycto.py
│   │   └── test_rag_pipeline.py
│   └── e2e/
│       └── test_discord_commands.py
│
├── scripts/
│   ├── index_knowledge_base.py       # CLI to re-index docs
│   ├── seed_db.py                    # Seed database with initial data
│   └── export_brgy_lookup.py         # Generate brgy_prefix → name mapping
│
├── .env.example                      # Environment variable template
├── docker-compose.yml                # Local dev: bot + redis + postgres
├── Dockerfile
├── pyproject.toml                    # Dependencies, linting, tool config
├── alembic.ini
└── README.md
Implementation Phases
Phase 0: Foundation & Infrastructure (Week 1)
Goal: Skeleton bot running on Discord with CI/CD pipeline.

Tasks:

#	Task	Details	Acceptance Criteria
0.1	Repository setup	Create ajolex/field-assist-bot, branch protection, PR templates	Repo exists with README, .gitignore, LICENSE
0.2	Project scaffolding	pyproject.toml with dependencies, src/ structure, Dockerfile, docker-compose.yml	docker-compose up starts the bot
0.3	Config management	pydantic-settings loading from .env — all secrets via env vars	Config loads cleanly; .env.example documents all vars
0.4	Discord bot skeleton	discord.py 2.x, connect to gateway, register 1 test slash command (/ping)	Bot comes online, /ping returns "pong"
0.5	CI pipeline	GitHub Actions: ruff lint, mypy type-check, pytest on every PR	PR blocked if checks fail
0.6	Logging	Structured JSON logging with structlog — log level configurable via env	All services log with context (user, channel, command)
0.7	Database setup	SQLAlchemy async + Alembic migrations for SQLite (dev) / PostgreSQL (prod)	Tables created via migration; can read/write
0.8	Deploy pipeline	GitHub Actions → deploy to Railway/Render on merge to main	Bot auto-deploys on merge
Dependencies: Python 3.11+, discord.py 2.x, pydantic-settings, SQLAlchemy 2.x, alembic, structlog, ruff, mypy, pytest, Docker

Phase 1: Data Integrations (Week 2)
Goal: Bot can read from Google Sheets and SurveyCTO.

#	Task	Details	Acceptance Criteria
1.1	Google Sheets client	Async wrapper around gspread with service account auth. Read: assignment sheet, productivity tracker	GoogleSheetsClient.read_assignments() returns structured data
1.2	SurveyCTO client	Async HTTP client for SurveyCTO REST API. Read: cases, form versions, submission counts	SurveyCTOClient.get_case("H019412021") returns case status
1.3	Cache layer	In-memory TTL cache (or Redis if needed). Configurable TTL per data source	Repeated calls within TTL don't hit external API
1.4	Brgy prefix lookup	Generate and load brgy_prefix → (barangay, municipality, province) mapping from exported data	lookup_brgy("H030832") → ("Guinacas", "Pototan", "Iloilo")
1.5	Error handling	Graceful degradation if external API is down — bot responds with "data temporarily unavailable" instead of crashing	Bot stays online even if Sheets/SCTO API fails
1.6	Integration tests	Tests with mocked API responses for both Sheets and SCTO	Tests pass in CI without real credentials
Secrets needed (stored in .env, never committed):

DISCORD_BOT_TOKEN
GOOGLE_SERVICE_ACCOUNT_JSON (base64 encoded)
SURVEYCTO_SERVER_NAME, SURVEYCTO_USERNAME, SURVEYCTO_PASSWORD
OPENAI_API_KEY
Google Sheets to connect:

Productivity Tracker
Assignment Sheet
Phase 2: Case Management Commands (Week 3)
Goal: Field teams can look up cases and request actions via Discord.

#	Task	Details	Acceptance Criteria
2.1	CaseService	Business logic for case lookups, status checks, team case lists	Unit tests pass for all status scenarios
2.2	/check_case <case_id>	Look up case status, team assignment, barangay, forms assigned. Redacts PII.	Returns formatted embed with case info
2.3	/case_status <case_id>	Detailed status: Open/Closed/Refused + explanation of why	Correctly interprets users field values
2.4	/team_cases <team_name>	List all open cases for a team with counts	Returns case count + list grouped by barangay
2.5	/request_reopen <case_id> <reason>	Logs a reopen request, notifies SRA via escalation	Request logged in DB; @Aubrey pinged in #bot-admin
2.6	PII protection	All case responses strip respondent names, phone numbers, addresses. Only show: case ID, status, team, barangay	No PII ever appears in Discord messages
2.7	Permission model	FOs can query cases. Only SRA/FC roles can request reopens. Admin commands restricted to SRA.	Unauthorized users get "insufficient permissions"
Discord embed format for /check_case:

Code
📋 Case H019412021
━━━━━━━━━━━━━━━━━━
Status:      🟢 Open (assigned to team_e)
Barangay:    Mambusao, Brgy. Bula
Municipality: Mambusao
Province:    Capiz
Forms:       HH Survey + ICM Business
Treatment:   Yes (T2)
━━━━━━━━━━━━━━━━━━
💡 This case requires both HH and ICM Business module completion before it will auto-close.
Phase 3: Knowledge Base & RAG Pipeline (Week 3–4)
Goal: Bot answers protocol and questionnaire questions using AI + knowledge base.

#	Task	Details	Acceptance Criteria
3.1	Document chunker	Split all 10 knowledge base docs into overlapping chunks (512 tokens, 64 token overlap). Preserve section headers as metadata.	Each chunk has: text, source_doc, section_path, chunk_id
3.2	Embedding pipeline	Embed all chunks using text-embedding-3-small. Store in ChromaDB (local) or Pinecone (prod).	Vector store populated; similarity search returns relevant chunks
3.3	Retriever	Given a question: embed → search top-8 chunks → re-rank by relevance → return top-4 with metadata	Retriever returns relevant protocol sections for test questions
3.4	System prompt	Carefully crafted system prompt that defines bot personality, role, constraints (no PII, escalation rules, neutrality)	System prompt reviewed and approved
3.5	Prompt builder	Assemble: system prompt + retrieved context + conversation history (last 3 messages) + user question	Prompt stays within token limit; context is relevant
3.6	Confidence scorer	LLM rates its own confidence (High/Medium/Low) based on how well the retrieved context answers the question	Confidence correctly identifies novel vs. known questions
3.7	Escalation logic	High → answer directly. Medium → answer + tag SRA for confirmation. Low → don't answer, escalate with context.	Escalation follows rules from bot_escalation_rules.md
3.8	/protocol <question>	Slash command for explicit protocol questions	Returns answer with source reference and confidence
3.9	@bot mention handler	Natural language question detection when bot is mentioned or in #scto channel	Bot responds to natural questions like the Discord screenshots
3.10	/reload_kb (admin)	Re-index all knowledge base documents without restarting bot	New/updated docs are searchable within 30 seconds
3.11	Interaction logging	Log every Q&A to database: question, answer, confidence, source docs, escalated?, channel, user	Can audit all bot interactions
System Prompt (core):

Code
You are Field Assist Bot, the AI assistant for IPA Philippines' ICM Follow-Up
Survey field operations. You support Field Officers (FOs), Field Coordinators
(FCs), and the Senior Research Associate (SRA) via Discord.

YOUR ROLE:
- Answer protocol questions about the ICM Follow-Up Survey and PSPS
- Help with SurveyCTO troubleshooting
- Provide case status information (never reveal PII)
- Give survey module guidance
- Post progress updates and announcements

YOUR RULES:
1. NEVER reveal respondent names, addresses, or phone numbers
2. NEVER reveal treatment arm assignments to field officers
3. NEVER make up protocol rules — only answer from the knowledge base
4. If unsure, say so and escalate to @Aubrey
5. Be concise, friendly, and professional
6. Respond in English (field teams communicate in English on Discord)
7. When answering protocol questions, cite the source section
8. For case lookups, only show: case ID, status, team, barangay, forms

CONTEXT: You have access to the study protocol, questionnaire guide, case
management rules, and field scenario FAQs. Use ONLY this context to answer.
If the question is not covered, escalate.
RAG Quality Benchmarks (test with real questions from Discord screenshots):

Test Question	Expected Source	Expected Answer Summary
"Can I interview the 2nd knowledgeable respondent?"	protocol.md §4.1, faq_field_scenarios.md §1	Only if original unavailable + last day in brgy
"Respondent moved to new house, can we interview there?"	protocol.md §6.1, faq_field_scenarios.md §1	Yes if return date unknown
"Cases H019412021 not showing on tablet"	case_status_rules.md, faq_field_scenarios.md §2	Try Get Blank Form; check assignment; escalate to SRA
"What version should I be using?"	known_issues_and_fixes.md	Pull current versions from data source
"Is a tricycle driver a business or employment?"	psps_questionnaire_guide.md §12	Depends on ownership — see classification rules
Phase 4: Progress & Productivity (Week 4)
Goal: Automated progress tracking and reporting.

#	Task	Details	Acceptance Criteria
4.1	ProgressService	Read productivity Google Sheet; calculate completion rates by team, FO, province, barangay	Unit tests with mock sheet data
4.2	/progress	Overall progress summary: total completed, remaining, % by province	Formatted embed/table posted
4.3	/team_status <team>	Team-specific: cases completed today, weekly total, target %, remaining	Shows each FO's numbers
4.4	/fo_productivity <fo_name>	Individual FO stats: daily average, weekly total, vs. 3.5/day target	Shows trend (on track / behind)
4.5	Progress formatters	Clean Discord embeds with tables, progress bars, color-coded status	Visually clear and scannable
Phase 5: Scheduling & Automation (Week 5)
Goal: Bot proactively posts updates without manual triggers.

#	Task	Details	Acceptance Criteria
5.1	Scheduler setup	APScheduler with async support, timezone-aware (Asia/Manila)	Jobs run at configured times
5.2	Morning briefing	Daily 6:00 AM: post assignments, form versions, reminders to #general	Posts automatically; correct data
5.3	Evening summary	Daily 6:00 PM: post productivity summary to #general	Posts automatically; accurate numbers
5.4	Form version monitor	Every 30 min: check SurveyCTO for form version changes. If changed → announce in #general + #scto	Detects and announces within 30 min of change
5.5	Weekly progress report	Every Friday 5:00 PM: comprehensive weekly report by province + team	Posted to #general
5.6	AnnouncementService	Use templates from announcement_templates.md; fill with live data	All templates render correctly
5.7	Announcement logging	Every auto-post logged to DB with type, channel, content, timestamp	Auditable announcement history
Phase 6: Escalation System (Week 5–6)
Goal: Robust escalation workflow for questions the bot can't answer.

#	Task	Details	Acceptance Criteria
6.1	EscalationService	Create, track, resolve escalations. Assign to SRA.	Full lifecycle tracked in DB
6.2	Escalation embeds	Formatted escalation message posted to #bot-admin with full context	SRA gets: who asked, what, where, bot's assessment, reason
6.3	Resolution tracking	SRA can /resolve <escalation_id> <answer> — bot learns from resolution	Resolution logged; optionally added to FAQ
6.4	Escalation dashboard	/escalation_stats — open count, avg resolution time, common categories	SRA can monitor bot gaps
6.5	Auto-FAQ builder	When SRA resolves an escalation, bot suggests adding Q&A to faq_field_scenarios.md	Continuous knowledge base improvement
Phase 7: Admin & Observability (Week 6)
Goal: SRA has full control and visibility into bot operations.

#	Task	Details	Acceptance Criteria
7.1	/bot_stats	Total interactions, questions answered, escalations, uptime	Quick health check
7.2	/set_version <form> <version>	Manually set current form version (override for announcements)	Version updated; next check uses new value
7.3	/reload_kb	Re-index knowledge base from docs/knowledge_base/	Updated docs searchable immediately
7.4	/announce <template> [overrides]	Manually trigger an announcement from template	Announcement posted to configured channel
7.5	Error alerting	Bot posts to #bot-admin if: API down, LLM error, unhandled exception	SRA knows immediately if something breaks
7.6	Health endpoint	HTTP /health for uptime monitoring	External monitor can ping
7.7	Audit log	All admin actions logged with who/what/when	Full audit trail
Phase 8: Testing, Hardening & Launch (Week 7–8)
#	Task	Details	Acceptance Criteria
8.1	Unit test coverage	≥80% coverage for all services	Coverage report in CI
8.2	Integration tests	Test real API calls (Sheets, SCTO) with test data	Tests pass with test credentials
8.3	RAG evaluation	Test 50+ real questions from Discord history against expected answers	≥85% accuracy on known questions
8.4	Load testing	Simulate 20 concurrent users sending commands	No crashes, <2s response time
8.5	Security audit	No secrets in code, no PII leaks, rate limiting works, permissions enforced	Passes security checklist
8.6	Documentation	README with setup guide, architecture diagram, contributing guide	New developer can set up in <30 min
8.7	Soft launch	Deploy to a test Discord server with FC team for 1 week	FCs provide feedback; bugs logged
8.8	Production launch	Deploy to production Discord server	Bot operational for all field teams
Technology Stack
Layer	Technology	Rationale
Language	Python 3.11+	Aligns with Stata workflow; best Discord bot ecosystem; strong async support
Discord	discord.py 2.x	Most mature, best documented, native slash commands + message content intent
Web framework	FastAPI (health/webhook endpoints only)	Lightweight; async; for health checks and potential future webhooks
LLM	OpenAI GPT-4o (primary), GPT-4o-mini (fallback/high-volume)	Best reasoning for protocol questions; mini for simple lookups to save cost
Embeddings	OpenAI text-embedding-3-small	Good quality/cost ratio; 1536 dimensions
Vector store	ChromaDB (dev/small scale) → Pinecone (if scaling needed)	ChromaDB is simple, local, no infra needed; Pinecone if >10k chunks
Database	SQLite (dev) → PostgreSQL (prod)	SQLite for zero-setup dev; Postgres for production reliability
Cache	In-memory dict with TTL (dev) → Redis (prod if needed)	Start simple; add Redis only if memory/performance requires it
ORM	SQLAlchemy 2.x (async) + Alembic	Industry standard; async support; migration management
Scheduler	APScheduler	Mature, async-compatible, cron-like syntax, timezone support
Google Sheets	gspread + google-auth	Most popular Python Sheets library; service account auth
HTTP client	httpx (async)	Modern async HTTP for SurveyCTO API calls
Config	pydantic-settings	Type-safe config from .env; validation; secrets management
Logging	structlog	Structured JSON logs; context binding; great for debugging
Linting	ruff	Fast, replaces flake8+isort+pyupgrade; single tool
Type checking	mypy (strict)	Catch bugs early; enforce type safety
Testing	pytest + pytest-asyncio + pytest-cov	Async test support; coverage reporting
Containerization	Docker + docker-compose	Reproducible dev/prod environments
Hosting	Railway or Render	Simple deployment from GitHub; auto-deploy on merge; affordable
CI/CD	GitHub Actions	Native to repo; free for public repos
Cost Estimates
Service	Usage Estimate	Monthly Cost
OpenAI GPT-4o	~50 protocol questions/day × 30 days × ~2K tokens each	~$15–25
OpenAI GPT-4o-mini	~100 simple lookups/day × 30 days × ~500 tokens	~$3–5
OpenAI Embeddings	Initial indexing + re-index weekly	<$1
Railway/Render hosting	1 always-on service (512MB–1GB RAM)	$5–10
PostgreSQL (Railway)	Small instance	$5
Redis (if needed)	Small instance	$0–5
Domain (optional)	For health endpoint	$0–12/year
Total		~$30–50/month
Agent Assignment
Agent A: Core Infrastructure + Data Integrations + Case Management
Owns: Phases 0, 1, 2, 4, and 7

Responsibilities:

Repository setup, CI/CD, Docker, deployment pipeline
Discord bot skeleton, cog system, permission model
Google Sheets integration (assignment sheet + productivity tracker)
SurveyCTO API integration (cases, forms, versions)
Cache layer
Database schema + migrations
All case management commands (/check_case, /case_status, /team_cases, /request_reopen)
All progress commands (/progress, /team_status, /fo_productivity)
Admin commands (/bot_stats, /set_version)
Discord embed formatters, PII protection
Health endpoint
Deliverables:

Working bot that connects to Discord and responds to slash commands
Live data from Google Sheets and SurveyCTO displayed in Discord
Case lookup with PII protection
Progress reporting with formatted embeds
Admin dashboard commands
Full test suite for all services
Agent B: Knowledge Base + RAG Pipeline + Scheduling + Escalation
Owns: Phases 3, 5, 6, and 8

Responsibilities:

Knowledge base document ingestion, chunking, embedding
Vector store setup (ChromaDB)
RAG retrieval pipeline (embed → search → re-rank → context assembly)
System prompt engineering and prompt builder
Confidence scoring and escalation logic
LLM integration (OpenAI client with fallback, retries, token management)
Protocol Q&A command (/protocol) and @bot natural language handler
Scheduled jobs (morning briefing, evening summary, form version monitor, weekly report)
Announcement service using templates
Escalation system (create, track, resolve, auto-FAQ)
/reload_kb, /escalation_stats, /resolve
RAG evaluation suite (50+ test questions)
Integration and e2e tests
Security audit and documentation
Deliverables:

Working RAG pipeline that answers protocol questions accurately
Confidence-based escalation that correctly identifies novel questions
Automated scheduled posts (morning, evening, weekly)
Form version change detection and auto-announcement
Full escalation lifecycle with resolution tracking
≥85% accuracy on protocol question test suite
Complete documentation
Shared Interface Contract
Both agents must agree on these interfaces before building independently:

src/models/case.py
"""Shared data models — both agents import from here."""
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


src/models/interaction.py
class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


src/models/escalation.py
class EscalationStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


src/config.py
"""Configuration — both agents use the same config structure."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Discord
Consensus Protocol for the Two Agents
After independent work:

Interface review: Both agents verify their implementations conform to the shared models in src/models/ and src/config.py
Integration test: Agent A's CaseService output must be consumable by Agent B's PromptBuilder for context-enriched answers
Merge protocol: Agent A merges first (infrastructure). Agent B rebases onto Agent A's work and merges second.
Joint testing: Run the full test suite (unit + integration + e2e + RAG evaluation) together
Disagreement resolution: If agents disagree on an approach, the criterion is: which approach is simpler to maintain long-term while meeting the acceptance criteria?
Quality Gates (Both Agents)
Gate	Requirement	Enforced By
Code style	ruff check passes with zero warnings	CI
Type safety	mypy --strict passes	CI
Test coverage	≥80% for all services	CI + pytest-cov
No secrets	No API keys, passwords, or PII in code	CI + pre-commit hook
PII protection	No respondent names/phones/addresses in any Discord output	Unit tests + code review
Documentation	Every public function has a docstring	ruff rule D100
PR review	Every PR requires 1 approval before merge	GitHub branch protection