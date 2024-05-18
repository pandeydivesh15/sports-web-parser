import logging
import multiprocessing
import typing
from collections.abc import Callable


def get_logger(
    name: str,
    level=logging.INFO,
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
):
    logging.basicConfig(format=format)
    logger = logging.getLogger(name=name)
    logger.setLevel(level)
    return logger