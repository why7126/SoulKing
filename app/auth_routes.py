"""Authentication and user management HTTP routes."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import (
    SESSION_COOKIE,
    clear_session_cookie,
    create_session,
    delete_session,
    display_name,
    get_user_by_id,
    get_user_by_username,
    hash_password,
    read_session_id,
    resolve_user_from_session,
    revoke_all_sessions_for_user,
    set_session_cookie,
    validate_password_complexity,
    validate_username,
    verify_password,
    count_active_admins,
    is_super_admin,
)
from app.config import get_settings
from app.database import get_db
from app.datetime_util import now_cn_naive
from app.models import User
from app.schemas import (
    AdminUserCreate,
    AdminUserOut,
    AdminUserResetPassword,
    AdminUserUpdate,
    AuthLoginIn,
    AuthMeOut,
    UserPasswordChangeIn,
    UserProfileUpdateIn,
)
from app.storage import S3Storage

router = APIRouter(tags=["auth"])
static_dir = Path(__file__).parent / "static"

AVATAR_MAX_BYTES = 2 * 1024 * 1024
AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}


def get_db_session():
    yield from get_db()


def get_current_user(request: Request, db: Session = Depends(get_db_session)) -> User:
    user = resolve_user_from_session(db, read_session_id(request))
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return user


def _avatar_url(storage: S3Storage, user: User) -> Optional[str]:
    key = (user.avatar_object_key or "").strip()
    if not key:
        return None
    return storage.create_presigned_get_url(key)


def user_to_me_out(storage: S3Storage, user: User) -> AuthMeOut:
    return AuthMeOut(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        display_name=display_name(user),
        role=user.role,
        is_active=user.is_active,
        avatar_url=_avatar_url(storage, user),
    )


def admin_user_out(user: User) -> AdminUserOut:
    return AdminUserOut(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        display_name=display_name(user),
        role=user.role,
        is_active=user.is_active,
        is_super_admin=is_super_admin(user),
        created_at=user.created_at,
    )


@router.get("/login")
def login_page():
    return FileResponse(static_dir / "login.html")


@router.post("/auth/login")
def auth_login(payload: AuthLoginIn, response: Response, db: Session = Depends(get_db_session)):
    username = validate_username(payload.username)
    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    session = create_session(db, user.id)
    set_session_cookie(response, session.id)
    return {"success": True}


@router.post("/auth/logout")
def auth_logout(request: Request, response: Response, db: Session = Depends(get_db_session)):
    sid = read_session_id(request)
    if sid:
        delete_session(db, sid)
    clear_session_cookie(response)
    return {"success": True}


@router.get("/auth/me", response_model=AuthMeOut)
def auth_me(user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    storage = S3Storage()
    return user_to_me_out(storage, user)


@router.patch("/users/me", response_model=AuthMeOut)
def update_profile(
    payload: UserProfileUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    if payload.username is not None:
        new_name = validate_username(payload.username)
        if new_name.lower() != user.username.lower():
            exists = db.scalar(
                select(User).where(
                    func.lower(User.username) == new_name.lower(),
                    User.id != user.id,
                    User.deleted_at.is_(None),
                )
            )
            if exists:
                raise HTTPException(status_code=400, detail="用户名已存在")
            user.username = new_name
    if payload.nickname is not None:
        user.nickname = payload.nickname.strip() or None
    user.updated_at = now_cn_naive()
    db.commit()
    db.refresh(user)
    return user_to_me_out(S3Storage(), user)


@router.post("/users/me/password")
def change_password(
    payload: UserPasswordChangeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码不正确")
    validate_password_complexity(payload.new_password)
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = now_cn_naive()
    db.commit()
    return {"success": True}


@router.post("/users/me/avatar", response_model=AuthMeOut)
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    if file.content_type not in AVATAR_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPEG、PNG、WebP 图片")
    data = await file.read()
    if len(data) > AVATAR_MAX_BYTES:
        raise HTTPException(status_code=400, detail="头像文件不能超过 2MB")
    ext = "jpg" if file.content_type == "image/jpeg" else "png" if file.content_type == "image/png" else "webp"
    key = f"avatar/{user.id}.{ext}"
    storage = S3Storage()
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        storage.upload_file(
            tmp_path,
            key,
            content_type=file.content_type,
            cache_control="max-age=0, must-revalidate",
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    old_key = (user.avatar_object_key or "").strip()
    user.avatar_object_key = key
    user.updated_at = now_cn_naive()
    db.commit()
    db.refresh(user)
    if old_key and old_key != key:
        try:
            storage.delete_object(old_key)
        except Exception:
            pass
    return user_to_me_out(storage, user)


# --- Admin user management ---


@router.get("/admin/users", response_model=list[AdminUserOut])
def list_admin_users(_admin: User = Depends(require_admin), db: Session = Depends(get_db_session)):
    users = db.scalars(
        select(User).where(User.deleted_at.is_(None)).order_by(User.created_at.asc())
    ).all()
    return [admin_user_out(u) for u in users]


@router.post("/admin/users", response_model=AdminUserOut)
def create_admin_user(
    payload: AdminUserCreate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    username = validate_username(payload.username)
    exists = get_user_by_username(db, username)
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    validate_password_complexity(payload.password)
    role = payload.role if payload.role in ("admin", "user") else "user"
    user = User(
        username=username,
        password_hash=hash_password(payload.password),
        nickname=(payload.nickname or "").strip() or None,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return admin_user_out(user)


@router.patch("/admin/users/{user_id}", response_model=AdminUserOut)
def update_admin_user(
    user_id: int,
    payload: AdminUserUpdate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.nickname is not None:
        user.nickname = payload.nickname.strip() or None
    if payload.role is not None:
        if payload.role not in ("admin", "user"):
            raise HTTPException(status_code=400, detail="无效角色")
        if user.role == "admin" and payload.role != "admin":
            if count_active_admins(db, exclude_user_id=user.id) < 1:
                raise HTTPException(status_code=400, detail="不能移除最后一名管理员")
        user.role = payload.role
    if payload.is_active is not None:
        if is_super_admin(user) and payload.is_active is False:
            raise HTTPException(status_code=400, detail="不能禁用超级管理员账号")
        user.is_active = payload.is_active
        if not payload.is_active:
            revoke_all_sessions_for_user(db, user.id)
    user.updated_at = now_cn_naive()
    db.commit()
    db.refresh(user)
    return admin_user_out(user)


@router.delete("/admin/users/{user_id}")
def delete_admin_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录账号")
    if user.role == "admin" and count_active_admins(db, exclude_user_id=user.id) < 1:
        raise HTTPException(status_code=400, detail="不能删除最后一名管理员")
    user.deleted_at = now_cn_naive()
    user.is_active = False
    revoke_all_sessions_for_user(db, user.id)
    db.commit()
    return {"success": True}


@router.post("/admin/users/{user_id}/reset-password")
def reset_admin_user_password(
    user_id: int,
    payload: AdminUserResetPassword,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    validate_password_complexity(payload.new_password)
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = now_cn_naive()
    revoke_all_sessions_for_user(db, user.id)
    db.commit()
    return {"success": True}
