from .base import Base
from sqlalchemy.orm import Mapped


class UsersOrm(Base):
    __tablename__ = "users"

    username: Mapped[str]
    telegram_id: Mapped[int]
    phone_number: Mapped[str]