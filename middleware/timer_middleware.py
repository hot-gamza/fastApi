from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TimerMiddleware:
    async def __call__(self, scope, receive, send):
        #scope는 HTTP 또는 WEBSOCKET 시에 특별한 처리 시, 사용
        start_time = datetime.now()        
        await send(await receive())
        elapsed_time = datetime.now() - start_time        
        logger.info(f"Elapsed time for request: {elapsed_time}")
