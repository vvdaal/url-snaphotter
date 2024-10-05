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
                    If False, sets the log level to INFO for file handler and CRITICAL for console.
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

    # Retrieve console and file handlers
    console_handler = logging.getLogger().handlers[0]
    file_handler = logging.getLogger().handlers[1]

    if debug:
        # If debug is enabled, log everything to both console and file
        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
    else:
        # If debug is disabled:
        # Log only CRITICAL messages to console
        console_handler.setLevel(logging.CRITICAL)
        # Log everything from INFO and above to file
        file_handler.setLevel(logging.INFO)

    # Set formatter for console and file handlers
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
