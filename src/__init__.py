import logging

LOGGER_NAME = "GRAPHML-BUILDER"
FORMATSTRING = "%(levelname)7s | %(message)s"
# FORMATSTRING = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=FORMATSTRING
)
logger = logging.getLogger(name=LOGGER_NAME)
