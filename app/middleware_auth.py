"""HTTP middleware: session auth for all non-public routes."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth import read_session_id, resolve_user_from_session
from app.database import SessionLocal


def is_public_path(path: str, method: str) -> bool:
    if path.startswith("/static"):
        return True
    if path == "/health":
        return True
    if path == "/login" and method == "GET":
        return True
    if path == "/auth/login" and method == "POST":
        return True
    if path == "/auth/logout" and method == "POST":
        return True
    if path in ("/", "/admin") and method == "GET":
        return True
    if path == "/api/__debug/client-log" and method == "POST":
        return True
    return False


def requires_admin(path: str) -> bool:
    return path.startswith("/admin/")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        if is_public_path(path, method):
            return await call_next(request)

        db = SessionLocal()
        try:
            user = resolve_user_from_session(db, read_session_id(request))
            if not user:
                return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
            if requires_admin(path) and user.role != "admin":
                return JSONResponse(status_code=403, content={"detail": "Admin required"})
            request.state.user = user
        finally:
            db.close()

        return await call_next(request)
