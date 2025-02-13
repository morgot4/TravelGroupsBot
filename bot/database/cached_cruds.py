from redis import asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import MarksOrm, AdminsOrm, PointsOrm
from bot.database.cruds import (
    orm_select_mark,
    orm_select_admin,
    orm_select_mark_by_phone_number,
    orm_select_mark_by_telegram_id,
    orm_select_point,
)
from bot.config import settings

rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

async def get_cached_mark(
    session: AsyncSession, key: str, delete: False, find_by="code"
) -> MarksOrm | None:
    mark_data = await rd.hgetall(f"mark:{key}")
    if mark_data:
        if delete:
            await rd.delete(f"mark:{key}")
            mark = await orm_select_mark(session=session, mark_code=key)
            return mark

        return MarksOrm(
            mark_code=key,
            captain_telegram_id=(
                None
                if mark_data["captain_telegram_id"] == "None"
                else mark_data["captain_telegram_id"]
            ),
            captain_username=(
                None
                if mark_data["captain_username"] == "None"
                else mark_data["captain_username"]
            ),
            captain_phone_number=(
                None
                if mark_data["captain_phone_number"] == "None"
                else mark_data["captain_phone_number"]
            ),
            last_point=(
                None
                if mark_data["last_point"] == "None"
                else mark_data["last_point"]
            ),
        )
    if find_by == "code":
        mark = await orm_select_mark(session=session, mark_code=key)
    elif find_by == "phone":
        mark = await orm_select_mark_by_phone_number(session=session, phone_number=key)
    elif find_by == "telegram_id":
        mark = await orm_select_mark_by_telegram_id(session=session, telegram_id=key)
    if mark and not delete:
        await add_cached_mark(mark=mark)

    return mark


async def get_cached_admin(
    session: AsyncSession, admin_telegram_id: str, delete=False
) -> AdminsOrm | None:
    admin_data = await rd.hgetall(f"admin:{admin_telegram_id}")
    if admin_data:
        if delete:
            await rd.delete(f"admin:{admin_telegram_id}")
        return AdminsOrm(telegram_id=admin_telegram_id, username=admin_data["username"])

    admin = await orm_select_admin(session=session, telegram_id=admin_telegram_id)
    if admin and not delete:
        await rd.hset(
            f"admin:{admin_telegram_id}", mapping={"username": admin.username}
        )
        await rd.expire(f"admin:{admin_telegram_id}", 3600)

    return admin


async def get_cached_point(
    session: AsyncSession, number: int, delete=False
) -> PointsOrm | None:
    point_data = await rd.hgetall(f"point:{number}")
    if point_data:
        if delete:
            await rd.delete(f"point:{number}")
        return PointsOrm(number=number, text=point_data["text"])

    point = await orm_select_point(session=session, number=number)
    if point and not delete:
        await rd.hset(f"point:{number}", mapping={"text": point.text})
        await rd.expire(f"point:{number}", 3600)

    return point


async def add_cached_mark(mark: MarksOrm):
    await rd.hset(
        f"mark:{mark.mark_code}",
        mapping={
            "captain_telegram_id": (
                "None" if mark.captain_telegram_id is None else mark.captain_telegram_id
            ),
            "captain_phone_number": (
                "None"
                if mark.captain_phone_number is None
                else mark.captain_phone_number
            ),
            "captain_username": (
                "None" if mark.captain_username is None else mark.captain_username
            ),
            "last_point": (
                "None" if mark.last_point is None else mark.last_point
            ),
        },
    )
    await rd.expire(f"mark:{mark.mark_code}", 3600)


async def add_cached_point(point: PointsOrm):
    await rd.hset(
        f"point:{point.number}",
        mapping={
            "text": point.text,
        },
    )
    await rd.expire(f"point:{point.number}", 3600)
