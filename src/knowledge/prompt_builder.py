"""Prompt assembly logic for RAG responses."""


def build_prompt(
	system_prompt: str,
	context: str,
	question: str,
	history: list[str] | None = None,
) -> str:
	"""Build a compact prompt from system prompt, context, and question."""

	history_text = "\n".join(history or [])
	return (
		f"System:\n{system_prompt}\n\n"
		f"History:\n{history_text}\n\n"
		f"Context:\n{context}\n\n"
		f"User Question:\n{question}\n\n"
		"Answer using only the context."
	)
