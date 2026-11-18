# -*- coding: utf-8 -*-
import logging
import time
import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.messages import MSG_INTERNAL_ERROR
from app.client.odoo_client import odoo_client
from app.api.v1.endpoints import auth, officer_absence, reply_templates, reports, tickets

_logger = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    """Resolve client IP for rate limiting, trusting X-Forwarded-For only behind a trusted proxy."""
    if settings.TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            last_hop = forwarded.split(",")[-1].strip()
            if last_hop:
                return last_hop
    return request.client.host if request.client and request.client.host else "unknown"


class SlidingWindowRateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter.
    
    Protects login endpoint against brute-force (15 req/min)
    and general API endpoints against excessive calls (180 req/min).
    """
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = _client_ip(request)
        path = request.url.path
        now = time.time()
        window = 60.0  # 1 minute sliding window

        # Determine limits based on target endpoint
        is_login = path.endswith("/auth/login")
        max_requests = 15 if is_login else 180
        key = f"{client_ip}:{path}" if is_login else f"{client_ip}:api"

        timestamps = [t for t in self.requests[key] if now - t < window]
        if not timestamps and key in self.requests:
            del self.requests[key]

        if len(timestamps) >= max_requests:
            oldest = timestamps[0]
            retry_after = max(1, int(window - (now - oldest)))
            msg = f"요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요. (제한: 분당 {max_requests}회)"
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"{msg} ({retry_after}초 후 재시도 가능)",
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": msg,
                        "retry_after_seconds": retry_after
                    }
                },
                headers={"Retry-After": str(retry_after)}
            )

        timestamps.append(now)
        self.requests[key] = timestamps

        if len(self.requests) > 1000:
            stale_keys = [k for k, v in self.requests.items() if not v or (now - v[-1] >= window)]
            for k in stale_keys:
                self.requests.pop(k, None)

        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan: Manage persistent HTTP connection pool."""
    # Startup
    await odoo_client.start()
    yield
    # Shutdown
    await odoo_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate Limiting Middleware
app.add_middleware(SlidingWindowRateLimitMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # 브라우저 JS가 CSV 내보내기 응답 헤더를 읽을 수 있도록 노출
    expose_headers=["Content-Disposition", "X-Export-Truncated", "Retry-After"],
)

# Mount API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix=f"{settings.API_V1_PREFIX}/tickets", tags=["Tickets"])
app.include_router(reply_templates.router, prefix=f"{settings.API_V1_PREFIX}/reply-templates", tags=["Reply Templates"])
app.include_router(officer_absence.router, prefix=f"{settings.API_V1_PREFIX}/officers", tags=["Officer Absence"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "ok", "version": settings.VERSION}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Normalize unhandled exceptions into clean JSON response without exposing internals."""
    _logger.exception("Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": MSG_INTERNAL_ERROR,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": MSG_INTERNAL_ERROR,
                "path": request.url.path,
            },
        },
    )
