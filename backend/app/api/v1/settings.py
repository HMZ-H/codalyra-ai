from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.encryption import decrypt_value, encrypt_value
from app.database.models.user import User
from app.database.session import get_db
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/settings", tags=["settings"])


class ApiKeyUpdate(BaseModel):
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


class ApiKeyStatus(BaseModel):
    has_gemini_key: bool = False
    gemini_key_preview: str | None = None
    has_openai_key: bool = False
    openai_key_preview: str | None = None
    has_anthropic_key: bool = False
    anthropic_key_preview: str | None = None


def _key_preview(encrypted: str | None) -> tuple[bool, str | None]:
    if not encrypted:
        return False, None
    try:
        key = decrypt_value(encrypted)
        preview = key[:4] + "..." + key[-4:] if len(key) > 8 else "****"
        return True, preview
    except Exception:
        return True, "****"


@router.get("/api-keys", response_model=ApiKeyStatus)
def get_api_key_status(
    current_user: User = Depends(get_current_active_user),
) -> ApiKeyStatus:
    g_has, g_prev = _key_preview(current_user.gemini_api_key_encrypted)
    o_has, o_prev = _key_preview(current_user.openai_api_key_encrypted)
    a_has, a_prev = _key_preview(current_user.anthropic_api_key_encrypted)
    return ApiKeyStatus(
        has_gemini_key=g_has, gemini_key_preview=g_prev,
        has_openai_key=o_has, openai_key_preview=o_prev,
        has_anthropic_key=a_has, anthropic_key_preview=a_prev,
    )


@router.put("/api-keys")
def update_api_key(
    data: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    if data.gemini_api_key is not None:
        current_user.gemini_api_key_encrypted = encrypt_value(data.gemini_api_key)
    if data.openai_api_key is not None:
        current_user.openai_api_key_encrypted = encrypt_value(data.openai_api_key)
    if data.anthropic_api_key is not None:
        current_user.anthropic_api_key_encrypted = encrypt_value(data.anthropic_api_key)
    db.commit()
    return {"status": "saved"}


@router.delete("/api-keys")
def delete_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    current_user.gemini_api_key_encrypted = None
    current_user.openai_api_key_encrypted = None
    current_user.anthropic_api_key_encrypted = None
    db.commit()
    return {"status": "deleted"}


@router.delete("/api-keys/{provider}")
def delete_provider_key(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    field_map = {
        "gemini": "gemini_api_key_encrypted",
        "openai": "openai_api_key_encrypted",
        "anthropic": "anthropic_api_key_encrypted",
    }
    field = field_map.get(provider)
    if not field:
        return {"status": "unknown provider"}
    setattr(current_user, field, None)
    db.commit()
    return {"status": "deleted"}
