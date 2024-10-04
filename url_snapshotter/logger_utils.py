# url_snapshotter/logger_utils.py

import logging


def setup_logger(debug: bool = False) -> logging.Logger:
    """
    Set up a logger for the application.

    Args:
        debug (bool): If True, sets the logging level to DEBUG and logs to 'debug.log'.
                      Otherwise, sets it to INFO and logs only to the console.

    Returns:
        logging.Logger: Configured logger instance for the application.
    """
    logger = logging.getLogger("url_snapshotter")

    # Clear any existing handlers to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set the logger's level to DEBUG to capture all levels
    logger.setLevel(logging.DEBUG)

    # Create a console handler with the appropriate level
    ch = logging.StreamHandler()
    ch_level = logging.DEBUG if debug else logging.INFO
    ch.setLevel(ch_level)
    ch_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(ch_formatter)

    # Add the console handler to the logger
    logger.addHandler(ch)

    if debug:
        # Create a file handler which logs debug messages if debugging is enabled
        fh = logging.FileHandler("debug.log", mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(fh_formatter)

        # Add the file handler to the logger
        logger.addHandler(fh)

    return logger
