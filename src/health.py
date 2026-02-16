"""FastAPI health endpoint for uptime monitoring."""

from fastapi import FastAPI

app = FastAPI(title="Field Assist Bot Health")


@app.get("/health")
async def health() -> dict[str, str]:
    """Return application health status."""
    return {"status": "ok"}
