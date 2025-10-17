from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        # Basic access log
        print(f"{request.method} {request.url.path} -> {response.status_code} in {duration_ms}ms")
        return response


