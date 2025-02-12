from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class MarksOrm(Base):
    __tablename__ = "marks"

    mark_code: Mapped[str] = mapped_column(
        primary_key=True, nullable=False, autoincrement=False
    )
    captain_username: Mapped[str] = mapped_column(nullable=True)
    captain_telegram_id: Mapped[str] = mapped_column(nullable=True)
    captain_phone_number: Mapped[str] = mapped_column(nullable=True)
    last_point: Mapped[int] = mapped_column(nullable=True)
    # goodwan_id: Mapped[int] = mapped_column(nullable=True)
