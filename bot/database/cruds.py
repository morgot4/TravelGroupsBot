from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import MarksOrm, AdminsOrm, PointsOrm


async def orm_select_mark(session: AsyncSession, mark_code: str) -> MarksOrm | None:
    query = select(MarksOrm).where(MarksOrm.mark_code == mark_code)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_mark_by_phone_number(
    session: AsyncSession, phone_number: str
) -> MarksOrm | None:
    query = select(MarksOrm).where(MarksOrm.captain_phone_number == phone_number)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_mark_by_telegram_id(
    session: AsyncSession, telegram_id: str
) -> MarksOrm | None:
    query = select(MarksOrm).where(MarksOrm.captain_telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_add_mark(session: AsyncSession, data: dict):
    mark = MarksOrm(
        mark_code=data["mark_code"],
        captain_username=data["captain_username"],
        captain_telegram_id=data["captain_telegram_id"],
        captain_phone_number=data["captain_phone_number"],
        history=data["history"]
    )
    session.add(mark)
    await session.commit()


async def orm_update_mark(session: AsyncSession, mark: MarksOrm, data: dict):
    for name, value in data.items():
        setattr(mark, name, value)
    await session.commit()


async def orm_select_marks(session: AsyncSession) -> list[MarksOrm]:
    query = select(MarksOrm)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_mark(session: AsyncSession, mark_code: str) -> None:
    await session.execute(delete(MarksOrm).where(MarksOrm.mark_code == mark_code))
    await session.commit()


async def orm_select_admin(session: AsyncSession, telegram_id: str) -> AdminsOrm | None:
    query = select(AdminsOrm).where(AdminsOrm.telegram_id == telegram_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_admins(session: AsyncSession) -> list[AdminsOrm]:
    query = select(AdminsOrm)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_admin(session: AsyncSession, data: dict):
    admin = AdminsOrm(
        username=data["username"],
        telegram_id=data["telegram_id"],
    )
    session.add(admin)
    await session.commit()


async def orm_delete_admin(session: AsyncSession, telegram_id: str):
    await session.execute(delete(AdminsOrm).where(AdminsOrm.telegram_id == telegram_id))
    await session.commit()


async def orm_select_point(session: AsyncSession, number: int) -> PointsOrm | None:
    query = select(PointsOrm).where(PointsOrm.number == number)
    result = await session.execute(query)
    return result.scalar()


async def orm_select_points(session: AsyncSession) -> list[PointsOrm]:
    query = select(PointsOrm)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_point(session: AsyncSession, data: dict):
    point = PointsOrm(
        number=data["number"],
        text=data["text"],
    )
    session.add(point)
    await session.commit()


async def orm_update_point(session: AsyncSession, point: PointsOrm, data: dict):
    query = update(PointsOrm).where(PointsOrm.number == point.number).values(data)
    await session.execute(query)
    await session.commit()
 

async def orm_delete_point(session: AsyncSession, number: int):
    await session.execute(delete(PointsOrm).where(PointsOrm.number == number))
    await session.commit()
