"""Password hashing, session management, and auth helpers."""

from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, Response
import bcrypt
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.datetime_util import now_cn_naive
from app.models import User, UserSession

SESSION_COOKIE = "session_id"
SESSION_DAYS = 14
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")

PASSWORD_COMPLEXITY_MSG = (
    "密码须至少 8 位，且包含大写字母、小写字母、数字和特殊字符（非字母数字）"
)


def validate_password_complexity(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail=PASSWORD_COMPLEXITY_MSG)
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail=PASSWORD_COMPLEXITY_MSG)
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail=PASSWORD_COMPLEXITY_MSG)
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail=PASSWORD_COMPLEXITY_MSG)
    if not re.search(r"[^A-Za-z0-9]", password):
        raise HTTPException(status_code=400, detail=PASSWORD_COMPLEXITY_MSG)


def validate_username(username: str) -> str:
    name = (username or "").strip()
    if not USERNAME_RE.match(name):
        raise HTTPException(
            status_code=400,
            detail="用户名须为 3–32 位字母、数字或下划线",
        )
    return name


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def active_user_clause():
    return (User.deleted_at.is_(None)) & (User.is_active.is_(True))


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.scalar(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    from sqlalchemy import func

    return db.scalar(
        select(User).where(
            func.lower(User.username) == username.strip().lower(),
            User.deleted_at.is_(None),
        )
    )


def create_session(db: Session, user_id: int) -> UserSession:
    session = UserSession(
        id=secrets.token_urlsafe(32),
        user_id=user_id,
        expires_at=now_cn_naive() + timedelta(days=SESSION_DAYS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: str) -> None:
    db.execute(delete(UserSession).where(UserSession.id == session_id))
    db.commit()


def revoke_all_sessions_for_user(db: Session, user_id: int) -> None:
    db.execute(delete(UserSession).where(UserSession.user_id == user_id))
    db.commit()


def get_session(db: Session, session_id: str) -> Optional[UserSession]:
    if not session_id:
        return None
    row = db.scalar(select(UserSession).where(UserSession.id == session_id))
    if not row:
        return None
    if row.expires_at < now_cn_naive():
        delete_session(db, row.id)
        return None
    return row


def resolve_user_from_session(db: Session, session_id: Optional[str]) -> Optional[User]:
    row = get_session(db, session_id)
    if not row:
        return None
    user = get_user_by_id(db, row.user_id)
    if not user or not user.is_active:
        return None
    return user


def read_session_id(request: Request) -> Optional[str]:
    return request.cookies.get(SESSION_COOKIE)


def set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=SESSION_DAYS * 86400,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE, path="/")


def display_name(user: User) -> str:
    nick = (user.nickname or "").strip()
    return nick if nick else user.username


def is_super_admin(user: User) -> bool:
    from app.config import get_settings

    settings = get_settings()
    return user.username.lower() == settings.admin_username.lower()


def seed_admin_user(db: Session) -> User:
    """Create seed admin when no users exist; return an admin user for migrations."""
    from sqlalchemy import func

    from app.config import get_settings

    settings = get_settings()
    existing = db.scalar(select(func.count(User.id)).where(User.deleted_at.is_(None))) or 0
    if existing:
        seed_admin = get_user_by_username(db, settings.admin_username)
        if seed_admin and not seed_admin.is_active:
            seed_admin.is_active = True
            seed_admin.updated_at = now_cn_naive()
            db.commit()
            db.refresh(seed_admin)
        admin = db.scalar(
            select(User)
            .where(User.role == "admin", User.deleted_at.is_(None))
            .order_by(User.id.asc())
        )
        if admin:
            return admin
        return db.scalars(select(User).where(User.deleted_at.is_(None)).order_by(User.id.asc())).first()

    username = validate_username(settings.admin_username)
    validate_password_complexity(settings.admin_password)
    user = User(
        username=username,
        password_hash=hash_password(settings.admin_password),
        nickname="管理员",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def count_active_admins(db: Session, exclude_user_id: Optional[int] = None) -> int:
    from sqlalchemy import func

    q = select(func.count(User.id)).where(
        User.role == "admin",
        User.deleted_at.is_(None),
        User.is_active.is_(True),
    )
    if exclude_user_id is not None:
        q = q.where(User.id != exclude_user_id)
    return db.scalar(q) or 0
