from .base import Base
from sqlalchemy.orm import Mapped


class AdminsOrm(Base):
    __tablename__ = "admins"

    username: Mapped[str]
    telegram_id: Mapped[int]
