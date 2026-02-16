"""Prompt assembly logic for RAG responses."""

from src.knowledge.indexer import KnowledgeChunk


SYSTEM_PROMPT = """You are Field Assist Bot, the AI assistant for IPA Philippines' ICM Follow-Up Survey field operations. You support Field Officers (FOs), Field Coordinators (FCs), and the Senior Research Associate (SRA) via Discord.

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
4. If unsure, say so and escalate to the Senior Research Associate
5. Be concise, friendly, and professional
6. Respond in English (field teams communicate in English on Discord)
7. When answering protocol questions, cite the source section
8. For case lookups, only show: case ID, status, team, barangay, forms

CONTEXT: You have access to the study protocol, questionnaire guide, case management rules, and field scenario FAQs. Use ONLY this context to answer. If the question is not covered, escalate."""


def build_prompt(question: str, context_chunks: list[KnowledgeChunk]) -> list[dict[str, str]]:
	"""Build OpenAI chat messages from system prompt, context chunks, and question.

	Returns a list of message dicts ready for OpenAI chat completions API.
	"""

	# Assemble context with source citations
	context_parts = []
	for chunk in context_chunks:
		citation = f"[{chunk.source_doc}"
		if chunk.section_path and chunk.section_path != "root":
			citation += f" > {chunk.section_path}"
		citation += "]"
		context_parts.append(f"{citation}\n{chunk.text}")

	context = "\n\n".join(context_parts)

	messages = [
		{"role": "system", "content": SYSTEM_PROMPT},
		{
			"role": "system",
			"content": f"Context from knowledge base:\n\n{context}",
		},
		{"role": "user", "content": question},
	]

	return messages
