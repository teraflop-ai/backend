import logfire
from loguru import logger


def setup_logger():
    logfire.configure()
    logger.configure(handlers=[logfire.loguru_handler()])
