# url_snapshotter/logger_utils.py

import logging


def setup_logger(debug: bool = False) -> logging.Logger:
    """Set up a logger for the application."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("url_snapshotter")
