import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)

logger = logging.getLogger("codalyra")
