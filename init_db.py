from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database import db_helper
from bot.database.models import MarksOrm, PointsOrm, AdminsOrm
import asyncio

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")


with open("marks.txt", "r") as f:
    data = f.read().split("\n")[:-1]

admins = [{
    "username": "andrei_k_456",
    "telegram_id": "1433128277"
    },
    {
    "username": "gesu1337",
    "telegram_id": "1008265857"
    },
]

mark_codes = []
for mark in data:
    mark_codes.append(mark.split()[1])


async def add_marks(session: AsyncSession, mark_codes):
    for code in mark_codes:
        mark = MarksOrm(
        mark_code=code,
    )
        session.add(mark)
        await session.commit()
  

async def add_points(session: AsyncSession):
    for i in range(11):
        point = PointsOrm(
            number=i,
            text=""
        )
        session.add(point)
        await session.commit()

async def add_admins(session: AsyncSession, admins):
    for admin in admins:
        admin = AdminsOrm(
            username=admin["username"],
            telegram_id=admin["telegram_id"]
        )
        session.add(admin)
        await session.commit()

async def init():
    session = db_helper.get_scoped_session()
    await add_marks(session=session, mark_codes=mark_codes)
    await add_points(session=session)
    await add_admins(session=session, admins=admins)
    await session.close()


asyncio.run(init())