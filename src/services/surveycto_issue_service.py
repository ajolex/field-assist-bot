"""SurveyCTO issue troubleshooting service."""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from src.integrations.google_sheets import GoogleSheetsClient
	from src.integrations.openai_client import OpenAIClient


_VARIABLE_PATTERN = re.compile(r"\b[a-zA-Z][a-zA-Z0-9_]{2,}\b")


@dataclass
class SurveyCTODiagnosis:
	"""Structured diagnosis for SurveyCTO issue reports."""

	issue_type: str
	variable_name: str
	form_name: str
	diagnosis_text: str
	suggested_fix: str
	workaround: str

	def fo_response(self) -> str:
		"""Render end-user facing diagnosis response."""
		lines = [
			f"This looks like a **{self.issue_type}** issue"
			+ (f" for `{self.variable_name}`." if self.variable_name != "unknown" else "."),
			self.diagnosis_text,
			f"Temporary workaround: {self.workaround}",
		]
		return "\n".join(lines)

	def escalation_payload(self, reporter: str, user_description: str) -> str:
		"""Render escalation payload block for Aubrey."""
		return (
			"SurveyCTO Form Issue Escalation\n"
			f"Reported by: {reporter}\n"
			f"Form: {self.form_name}\n"
			f"Variable: {self.variable_name}\n"
			f"Issue type: {self.issue_type}\n"
			f"Description: {user_description}\n"
			f"Bot diagnosis: {self.diagnosis_text}\n"
			f"Suggested fix: {self.suggested_fix}"
		)


class SurveyCTOIssueService:
	"""Generates suggestions/explanations for SurveyCTO form issues."""

	def __init__(self, sheets_client: "GoogleSheetsClient", openai_client: "OpenAIClient") -> None:
		"""Initialize dependencies."""
		self.sheets_client = sheets_client
		self.openai_client = openai_client

	def extract_variable_hints(self, issue_text: str) -> list[str]:
		"""Extract candidate variable names from issue text."""
		hints = []
		for token in _VARIABLE_PATTERN.findall(issue_text):
			lowered = token.lower()
			if lowered in {"the", "and", "then", "with", "from", "that", "this", "when", "profit"}:
				continue
			if "_" in token or lowered.startswith(("q", "s", "hh", "icm")):
				hints.append(token)
		return list(dict.fromkeys(hints))[:12]

	def detect_issue_type(self, issue_text: str) -> str:
		"""Classify likely issue type from FO symptom wording."""
		text = issue_text.lower()
		if any(phrase in text for phrase in ["error", "invalid", "constraint", "must be"]):
			return "Constraint"
		if any(phrase in text for phrase in ["wrong name", "wrong value", "pulled", "shows wrong"]):
			return "Calculation/Pull data"
		if any(phrase in text for phrase in ["shows twice", "appears twice", "repeat"]):
			return "Repeat group"
		if any(
			phrase in text
			for phrase in ["didn't appear", "did not appear", "still asks", "appeared when", "skip"]
		):
			return "Relevance/Skip logic"
		if any(phrase in text for phrase in ["crash", "freeze", "stuck", "lag"]):
			return "Technical/device"
		return "Relevance/Skip logic"

	def detect_form_name(self, issue_text: str) -> str:
		"""Infer likely form from issue text mentions."""
		text = issue_text.lower()
		if "icm" in text or "business" in text:
			return "ICM Business"
		if "phase a" in text or "revisit" in text:
			return "Phase A Revisit"
		if "hh" in text or "household" in text:
			return "HH Survey"
		return "Unknown"

	def workaround_for(self, issue_type: str) -> str:
		"""Map issue type to FO temporary workaround."""
		if issue_type == "Constraint":
			return (
				"If the value is correct, note the case ID and contact your FC "
				"while we verify the rule."
			)
		if issue_type == "Calculation/Pull data":
			return (
				"Continue with the correct respondent info and add a comment "
				"noting the mismatch."
			)
		if issue_type == "Repeat group":
			return "Continue the survey and add a comment that the question repeated unexpectedly."
		if issue_type == "Technical/device":
			return (
				"Restart SurveyCTO Collect and sync, then retry on stable internet "
				"before re-opening the form."
			)
		return (
			"Enter a neutral value if needed and add a comment that this is a "
			"skip logic issue so we can patch it."
		)

	async def diagnose(self, issue_text: str) -> SurveyCTODiagnosis:
		"""Return structured diagnosis aligned to SurveyCTO troubleshooting guide."""
		variable_hints = self.extract_variable_hints(issue_text)
		variable_name = variable_hints[0] if variable_hints else "unknown"
		issue_type = self.detect_issue_type(issue_text)
		form_name = self.detect_form_name(issue_text)
		workaround = self.workaround_for(issue_type)
		form_context = await self.sheets_client.surveycto_issue_context(issue_text, variable_hints)

		system_prompt = (
			"You are diagnosing SurveyCTO form issues for field users. "
			"Follow this method: identify variable, identify issue type, "
			"inspect relevance/constraint/calculation, "
			"then explain plain-English behavior. "
			"Return EXACTLY 2 lines:\n"
			"DIAGNOSIS: <short explanation>\n"
			"SUGGESTED_FIX: <what to change in xlsform logic>"
		)
		context = form_context or "No matching rows found in configured form sheets."
		answer = await self.openai_client.chat_with_system_prompt(
			system_prompt=system_prompt,
			user_message=issue_text,
			context=context,
		)
		lines = [line.strip() for line in answer.splitlines() if line.strip()]
		diagnosis_line = next(
			(line for line in lines if line.upper().startswith("DIAGNOSIS:")),
			(
				"DIAGNOSIS: This is likely a form logic mismatch and needs "
				"a quick check in the form sheet."
			),
		)
		fix_line = next(
			(line for line in lines if line.upper().startswith("SUGGESTED_FIX:")),
			(
				"SUGGESTED_FIX: Review relevance/constraint expressions "
				"for the reported question and upstream variable."
			),
		)
		diagnosis_text = diagnosis_line.split(":", 1)[1].strip()
		suggested_fix = fix_line.split(":", 1)[1].strip()

		return SurveyCTODiagnosis(
			issue_type=issue_type,
			variable_name=variable_name,
			form_name=form_name,
			diagnosis_text=diagnosis_text,
			suggested_fix=suggested_fix,
			workaround=workaround,
		)
