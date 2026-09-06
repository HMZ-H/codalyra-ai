import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies import get_current_active_user
from app.database.models.user import User
from app.core.permissions import verify_review_owner
from app.core.exceptions import NotFoundException
from app.services.export_service import ExportService

router = APIRouter(prefix="/exports", tags=["exports"])


@router.get("/reviews/{review_id}")
def export_review(
    review_id: uuid.UUID,
    format: str = Query("markdown", regex="^(markdown)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    verify_review_owner(db, review_id, current_user.id)

    content = ExportService.export_markdown(db, review_id)
    if not content:
        raise NotFoundException("Review not found")

    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=review-{review_id}.md"},
    )
