"""Formatting utilities for Discord responses."""

from src.models.case import CaseRecord


def format_case_embed_text(case: CaseRecord) -> str:
	"""Format case details in compact multiline text."""

	forms = " + ".join(case.forms) if case.forms else "N/A"
	return (
		f"📋 Case {case.case_id}\n"
		f"Status: {case.status}\n"
		f"Barangay: {case.barangay or 'unknown'}\n"
		f"Municipality: {case.municipality or 'unknown'}\n"
		f"Province: {case.province or 'unknown'}\n"
		f"Team: {case.team or 'unassigned'}\n"
		f"Forms: {forms}"
	)


def format_progress_text(values: dict[str, float], label: str) -> str:
	"""Format progress metric map for Discord replies."""

	return (
		f"{label}\n"
		f"Completed: {values.get('completed', 0):.1f}\n"
		f"Target: {values.get('target', 0):.1f}\n"
		f"Rate: {values.get('rate', 0):.1f}%"
	)


def format_escalation_text(escalation_id: int) -> str:
	"""Format escalation confirmation text."""

	return f"Escalation created successfully. ID: {escalation_id}"
