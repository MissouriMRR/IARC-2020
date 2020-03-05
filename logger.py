"""Logging configuration and functions"""
import logging

from datetime import datetime
from logging import Formatter, FileHandler, StreamHandler
from logging.handlers import QueueHandler, QueueListener
from colorlog import ColoredFormatter

LOG_FILE: str = f"logs/{datetime.now()}.log"
LOG_FORMAT: str = "%(log_color)s%(levelname)s | %(asctime)s @  %(processName)s:%(funcName)s > %(message)s%(reset)s"
LOG_LEVEL = logging.DEBUG


def init_logger(queue):
    """
    Creates a QueueListener that will process all log messages throughout
    the application
    """
    formatter: Formatter = ColoredFormatter(LOG_FORMAT)

    file: FileHandler = logging.FileHandler(LOG_FILE, "a")
    file.setFormatter(formatter)

    console: StreamHandler = logging.StreamHandler()
    console.setFormatter(formatter)

    return QueueListener(queue, file, console)


def worker_configurer(queue):
    """
    When this is run, it configures the logger of this process to submit
    logs to the logging process (QueueListener)
    """
    queue_handler: QueueHandler = QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(queue_handler)
    root.setLevel(LOG_LEVEL)
