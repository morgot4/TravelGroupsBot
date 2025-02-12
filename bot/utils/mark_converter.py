from bot.database.models import MarksOrm


async def mark_data_from_str(line: str, data: dict) -> dict:
    data = data.copy()
    line = line.split("~")
    data["captain_telegram_id"] = line[0]
    data["captain_phone_number"] = line[1]
    data["captain_username"] = line[2]
    return data


async def mark_from_str(line: str, data: dict) -> MarksOrm:
    data = data.copy()
    line = line.split("~")
    return MarksOrm(
        mark_code=data["mark_code"],
        captain_telegram_id=line[0],
        captain_phone_number=line[1],
        captain_username=line[2],
    )
