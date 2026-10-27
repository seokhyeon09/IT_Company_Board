# -*- coding: utf-8 -*-
import time
import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.client.odoo_client import odoo_client
from app.api.v1.endpoints import auth, tickets


class SlidingWindowRateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory sliding window rate limiter.
    
    Protects login endpoint against brute-force (15 req/min)
    and general API endpoints against excessive calls (180 req/min).
    """
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        now = time.time()
        window = 60.0  # 1 minute sliding window

        # Determine limits based on target endpoint
        is_login = path.endswith("/auth/login")
        max_requests = 15 if is_login else 180
        key = f"{client_ip}:{path}" if is_login else f"{client_ip}:api"

        async with self.lock:
            timestamps = self.requests[key]
            # Prune timestamps older than window
            self.requests[key] = [t for t in timestamps if now - t < window]

            if len(self.requests[key]) >= max_requests:
                oldest = self.requests[key][0]
                retry_after = max(1, int(window - (now - oldest)))
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요. (제한: 분당 {max_requests}회)",
                            "retry_after_seconds": retry_after
                        }
                    },
                    headers={"Retry-After": str(retry_after)}
                )

            self.requests[key].append(now)

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
)

# Mount API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix=f"{settings.API_V1_PREFIX}/tickets", tags=["Tickets"])

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "ok", "version": settings.VERSION}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Normalize unhandled exceptions into clean JSON response."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "path": request.url.path,
            }
        }
    )
