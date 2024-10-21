import sys
from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.levels import LogLevel
from fastapi import FastAPI

async def setup_logger():
    global logger
    logger = Logger(
        name="fastapi_logger",
        level=LogLevel.DEBUG,
    )

    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    stream_handler = AsyncStreamHandler(
        stream=sys.stderr,
        formatter=formatter,
        level=LogLevel.DEBUG,
    )

    logger.add_handler(stream_handler)
    
    return logger

logger = None

async def get_logger():
    global logger
    if logger is None:
        logger = await setup_logger()
    return logger