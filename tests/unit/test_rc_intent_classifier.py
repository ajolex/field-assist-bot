"""Tests for remote-control intent classification fast-paths and param extractor."""

import pytest

from src.services.intent_classifier import Intent, IntentClassifier


# ---------------------------------------------------------------------------
# Fast-path regex tests — no LLM needed
# ---------------------------------------------------------------------------

class FakeOpenAI:
    """Stub that should NOT be called for fast-path classifications."""
    has_api_key = False

    async def chat_with_system_prompt(self, **kwargs):
        raise AssertionError("LLM should not be called for fast-path intents")


@pytest.fixture
def classifier() -> IntentClassifier:
    return IntentClassifier(FakeOpenAI())  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_screenshot_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("take a screenshot")
    assert intent == Intent.RC_SCREENSHOT

    intent, _ = await classifier.classify("show me my screen")
    assert intent == Intent.RC_SCREENSHOT

    intent, _ = await classifier.classify("screenshot please")
    assert intent == Intent.RC_SCREENSHOT

    intent, _ = await classifier.classify("screen capture")
    assert intent == Intent.RC_SCREENSHOT

    # Window-specific screenshot passes raw text as param
    intent, param = await classifier.classify("screenshot of Teams")
    assert intent == Intent.RC_SCREENSHOT
    assert param is not None and "Teams" in param


@pytest.mark.asyncio
async def test_sys_status_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("what's my CPU usage?")
    assert intent == Intent.RC_SYS_STATUS

    intent, _ = await classifier.classify("how is my RAM?")
    assert intent == Intent.RC_SYS_STATUS

    intent, _ = await classifier.classify("check disk space")
    assert intent == Intent.RC_SYS_STATUS

    intent, _ = await classifier.classify("system status")
    assert intent == Intent.RC_SYS_STATUS

    intent, _ = await classifier.classify("how's my computer doing?")
    assert intent == Intent.RC_SYS_STATUS

    intent, _ = await classifier.classify("what's the uptime?")
    assert intent == Intent.RC_SYS_STATUS


@pytest.mark.asyncio
async def test_processes_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("show me running processes")
    assert intent == Intent.RC_PROCESSES

    intent, _ = await classifier.classify("what's running on my pc?")
    assert intent == Intent.RC_PROCESSES

    intent, _ = await classifier.classify("open task manager")
    assert intent == Intent.RC_PROCESSES

    intent, _ = await classifier.classify("top processes")
    assert intent == Intent.RC_PROCESSES


@pytest.mark.asyncio
async def test_git_fast_path(classifier: IntentClassifier) -> None:
    intent, param = await classifier.classify("git pull this repo")
    assert intent == Intent.RC_GIT_PULL
    assert param is not None

    intent, param = await classifier.classify("git status")
    assert intent == Intent.RC_GIT_STATUS

    intent, param = await classifier.classify("run git st on my project")
    assert intent == Intent.RC_GIT_STATUS


@pytest.mark.asyncio
async def test_greeting_still_works(classifier: IntentClassifier) -> None:
    """Greetings should NOT trigger remote control."""
    intent, _ = await classifier.classify("hello")
    assert intent == Intent.GREETING

    intent, _ = await classifier.classify("Hey good morning")
    assert intent == Intent.GREETING


@pytest.mark.asyncio
async def test_surveycto_still_works(classifier: IntentClassifier) -> None:
    """SurveyCTO issues should NOT trigger remote control."""
    intent, _ = await classifier.classify("skip logic is not working on the form")
    assert intent == Intent.SURVEYCTO_ISSUE


# ---------------------------------------------------------------------------
# Automation job fast-path tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_dms_fast_path(classifier: IntentClassifier) -> None:
    """Full DMS pipeline phrases."""
    intent, _ = await classifier.classify("run the dms")
    assert intent == Intent.RC_RUN_DMS

    intent, _ = await classifier.classify("run the full pipeline")
    assert intent == Intent.RC_RUN_DMS

    intent, _ = await classifier.classify("run the daily automation")
    assert intent == Intent.RC_RUN_DMS

    intent, _ = await classifier.classify("run scto_dms_daily")
    assert intent == Intent.RC_RUN_DMS


@pytest.mark.asyncio
async def test_download_hh_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("download the household survey data")
    assert intent == Intent.RC_DOWNLOAD_HH

    intent, _ = await classifier.classify("pull the HH csv")
    assert intent == Intent.RC_DOWNLOAD_HH

    intent, _ = await classifier.classify("fetch household form data")
    assert intent == Intent.RC_DOWNLOAD_HH


@pytest.mark.asyncio
async def test_download_biz_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("download the business data csv")
    assert intent == Intent.RC_DOWNLOAD_BIZ

    intent, _ = await classifier.classify("get the ICM business data from SurveyCTO")
    assert intent == Intent.RC_DOWNLOAD_BIZ

    intent, _ = await classifier.classify("pull biz survey data")
    assert intent == Intent.RC_DOWNLOAD_BIZ


@pytest.mark.asyncio
async def test_download_phase_a_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("download the Phase A revisit data")
    assert intent == Intent.RC_DOWNLOAD_PHASE_A

    intent, _ = await classifier.classify("fetch the revisit form data")
    assert intent == Intent.RC_DOWNLOAD_PHASE_A

    intent, _ = await classifier.classify("get phase a csv")
    assert intent == Intent.RC_DOWNLOAD_PHASE_A


@pytest.mark.asyncio
async def test_run_hh_dms_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("run the household dms")
    assert intent == Intent.RC_RUN_HH_DMS

    intent, _ = await classifier.classify("execute the HH Stata do file")
    assert intent == Intent.RC_RUN_HH_DMS


@pytest.mark.asyncio
async def test_run_biz_dms_fast_path(classifier: IntentClassifier) -> None:
    intent, _ = await classifier.classify("run the business dms")
    assert intent == Intent.RC_RUN_BIZ_DMS

    intent, _ = await classifier.classify("execute biz Stata master")
    assert intent == Intent.RC_RUN_BIZ_DMS


# ---------------------------------------------------------------------------
# Intent enum coverage
# ---------------------------------------------------------------------------

def test_all_rc_intents_exist() -> None:
    """Verify all expected RC intents are defined."""
    expected = [
        "rc_sys_status", "rc_processes", "rc_kill",
        "rc_file_find", "rc_file_send", "rc_file_save",
        "rc_file_size", "rc_file_zip", "rc_screenshot",
        "rc_app_open", "rc_app_close", "rc_app_run",
        "rc_web_download", "rc_web_ping",
        "rc_git_status", "rc_git_pull",
        "rc_download_hh", "rc_download_biz", "rc_download_phase_a",
        "rc_run_hh_dms", "rc_run_biz_dms", "rc_run_dms",
    ]
    for name in expected:
        assert Intent(name), f"Missing intent: {name}"
