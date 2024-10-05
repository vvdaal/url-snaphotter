# url_snapshotter/logging_config.py

# This module configures the logging settings for the application using structlog (https://www.structlog.org/).

import structlog
import logging
import sys


def configure_structlog(debug: bool = False):
    """
    Configures Structlog for logging.

    Args:
      debug (bool): If True, sets the log level to DEBUG for all handlers.
                    If False, sets the log level to INFO for file handler and ERROR for console.
    """

    # Define processors for formatting log messages
    processors = [
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
    ]

    # Add a renderer depending on debug flag
    if debug:
        # Use plain console renderer for easier debugging
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Use key-value pairs for structured logging in production
        processors.append(structlog.processors.KeyValueRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set up standard logging for compatibility
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console handler
            logging.FileHandler("app.log", mode="a", encoding="utf-8"),  # File handler
        ],
    )

    # Adjust the log level for console and file handlers individually
    console_handler = logging.getLogger().handlers[0]
    console_handler.setLevel(logging.DEBUG if debug else logging.ERROR)

    file_handler = logging.getLogger().handlers[1]
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
