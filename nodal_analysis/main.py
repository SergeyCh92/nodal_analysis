import asyncio
import logging

from nodal_analysis.schemas import NodeAnalysisRequest
from nodal_analysis.service import NodalAnalysisService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - PID:%(process)d - threadName:%(thread)d - %(message)s",
)
logging.getLogger("pika").setLevel(logging.WARNING)


async def main():
    logging.info("program started")
    service = NodalAnalysisService()
    await service.async_start(service.settings.nodal_analysis_queue, NodeAnalysisRequest)


if __name__ == "__main__":
    asyncio.run(main())
