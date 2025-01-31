import logging
import structlog


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get structured logger instance
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            (
                structlog.dev.ConsoleRenderer()
                if os.getenv("ENV") == "development"
                else structlog.processors.JSONRenderer()
            ),
        ],
        wrapper_class=structlog.BoundLogger,
        logger_factory=structlog.WriteLoggerFactory(
            logger=logging.getLogger(name or __name__)
        ),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()
