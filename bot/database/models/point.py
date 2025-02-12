from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class PointsOrm(Base):
    __tablename__ = "points"

    number: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=False)
    text: Mapped[str] = mapped_column(nullable=True)
