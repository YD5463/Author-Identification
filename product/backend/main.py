import logging
import sys

import uvicorn
from pipeline.routes import app

from product.backend.models.config import config as settings

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        datefmt="%d-%m-%Y %H:%M:%S",
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    )
    logger.info("Starting backend Service")
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug_mode,
        workers=2,
    )


if __name__ == "__main__":
    main()
