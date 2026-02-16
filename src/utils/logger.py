"""Structured logging utilities."""

import logging
import sys

import structlog


def configure_logging(level: str) -> None:
	"""Configure structlog and stdlib logging."""

	logging.basicConfig(format="%(message)s", stream=sys.stdout, level=getattr(logging, level, logging.INFO))

	structlog.configure(
		processors=[
			structlog.contextvars.merge_contextvars,
			structlog.processors.TimeStamper(fmt="iso"),
			structlog.stdlib.add_log_level,
			structlog.processors.JSONRenderer(),
		],
		logger_factory=structlog.stdlib.LoggerFactory(),
		wrapper_class=structlog.stdlib.BoundLogger,
		cache_logger_on_first_use=True,
	)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
	"""Return a named structured logger."""

	return structlog.get_logger(name)
