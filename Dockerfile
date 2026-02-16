FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY docs ./docs
COPY scripts ./scripts

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

CMD ["python", "-m", "src.bot"]
