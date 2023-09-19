from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TimerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        start_time = datetime.now()
        await self.app(scope, receive, send)
        elapsed_time = datetime.now() - start_time
        logger.info(f"Elapsed time for request: {elapsed_time}")
