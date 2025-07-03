import logging
import sys


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s][%(name)s].%(funcName)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

def get_logger(name:str) -> logging.Logger:
    return logging.getLogger(name)