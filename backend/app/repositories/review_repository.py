import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: uuid.UUID) -> Review | None:
        return self.db.get(Review, review_id)

    def get_by_project(self, project_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Review]:
        stmt = (
            select(Review)
            .where(Review.project_id == project_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_with_runs(self, review_id: uuid.UUID) -> Review | None:
        stmt = (
            select(Review)
            .options(joinedload(Review.runs))
            .where(Review.id == review_id)
        )
        return self.db.scalars(stmt).unique().first()

    def create(self, review_data: dict) -> Review:
        review = Review(**review_data)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def update(self, review: Review, update_data: dict) -> Review:
        for key, value in update_data.items():
            setattr(review, key, value)
        self.db.commit()
        self.db.refresh(review)
        return review
