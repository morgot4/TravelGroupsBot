from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ARRAY, Integer, text


class MarksOrm(Base):
    __tablename__ = "marks"

    mark_code: Mapped[str] = mapped_column(
        primary_key=True, nullable=False, autoincrement=False
    )
    captain_username: Mapped[str] = mapped_column(nullable=True)
    captain_telegram_id: Mapped[str] = mapped_column(nullable=True)
    captain_phone_number: Mapped[str] = mapped_column(nullable=True)
    history: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=True, server_default=text("'{}'"))
