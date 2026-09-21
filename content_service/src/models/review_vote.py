from shared.db.types import created_at_type, uuid_pk
from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class ReviewVoteORM(BaseORM):
    __tablename__ = "review_votes"

    review_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("book_reviews.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid_pk] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    vote: Mapped[int] = mapped_column(SmallInteger)

    created_at: Mapped[created_at_type]

    __table_args__ = (
        CheckConstraint(
            "vote IN (1, 0, -1)",
            name="chk_review_votes_vote_value",
        ),
    )
