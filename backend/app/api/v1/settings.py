from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.database.models.user import User
from app.core.encryption import encrypt_value, decrypt_value

router = APIRouter(prefix="/settings", tags=["settings"])


class ApiKeyUpdate(BaseModel):
    gemini_api_key: str


class ApiKeyStatus(BaseModel):
    has_gemini_key: bool
    gemini_key_preview: str | None = None


@router.get("/api-keys", response_model=ApiKeyStatus)
def get_api_key_status(
    current_user: User = Depends(get_current_active_user),
) -> ApiKeyStatus:
    if current_user.gemini_api_key_encrypted:
        try:
            key = decrypt_value(current_user.gemini_api_key_encrypted)
            preview = key[:4] + "..." + key[-4:] if len(key) > 8 else "****"
        except Exception:
            preview = "****"
        return ApiKeyStatus(has_gemini_key=True, gemini_key_preview=preview)
    return ApiKeyStatus(has_gemini_key=False)


@router.put("/api-keys")
def update_api_key(
    data: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    current_user.gemini_api_key_encrypted = encrypt_value(data.gemini_api_key)
    db.commit()
    return {"status": "saved"}


@router.delete("/api-keys")
def delete_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    current_user.gemini_api_key_encrypted = None
    db.commit()
    return {"status": "deleted"}
