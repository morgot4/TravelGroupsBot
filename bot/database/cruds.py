from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from .models import MarksOrm, AdminsOrm


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


async def orm_delete_mark(session: AsyncSession, mark: MarksOrm) -> None:
    await session.delete(mark)
    await session.commit()


async def orm_select_admin(session: AsyncSession, telegram_id: int) -> AdminsOrm | None:
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


async def orm_delete_admin(session: AsyncSession, admin: AdminsOrm):
    await session.delete(admin)
    await session.commit()
