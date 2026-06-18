import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start
        logging.info(f"{request.method} {request.url.path} [{response.status_code}] - {elapsed:.3f}s")
        return response
