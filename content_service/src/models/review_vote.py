import uuid

from shared.db.types import created_at_type
from sqlalchemy import CheckConstraint, ForeignKey, Index, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseORM


class ReviewVoteORM(BaseORM):
    __tablename__ = "review_votes"
    __table_args__ = (
        CheckConstraint(
            "vote IN (1, -1)",
            name="chk_review_votes_vote_value",
        ),
        Index("ix_review_votes_review_id_vote", "review_id", "vote"),
        {"comment": "Реакции пользователей на рецензии книг (лайки и дизлайки)"},
    )

    review_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("book_reviews.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Ссылка на оцениваемый отзыв",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Пользователь, поставивший реакцию",
    )

    vote: Mapped[int] = mapped_column(
        SmallInteger, comment="Тип реакции: 1 (Лайк) или -1 (Дизлайк)"
    )

    created_at: Mapped[created_at_type] = mapped_column(
        comment="Дата и время постановки реакции"
    )
