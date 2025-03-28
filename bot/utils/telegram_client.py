from telethon.sync import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.types import UserFull
from bot.config import bot_manager, settings
from bot.database import db_helper
from bot.utils.marks_actions import get_captain_message
from aiogram.utils import markdown

client = bot_manager.get_client()


async def get_user(username: str, client: TelegramClient) -> UserFull:
    async with client:
        try:
            user = await client(GetFullUserRequest(username))
        except Exception as exp:
            print(exp)
            return None
        return user


@client.on(events.NewMessage(pattern=r"Метка"))
async def handler(event):
    sender = await event.get_sender()
    if sender.bot and sender.first_name == settings.GOODWAN_BOT_NAME:
        text = event.raw_text.split("#")
        if len(text) > 1:
            point_number = text[1]
        else:
            point_number = "0"

        mark_code = text[0].split()
        async with db_helper.scoped_session_dependency() as session:
            captain_id, message = await get_captain_message(session=session, mark_code=mark_code[1], number=int(point_number))
        if captain_id is not None and message is not None:
            await bot_manager.get_bot().send_message(
                chat_id=int(captain_id), text=markdown.markdown_decoration.quote(message)
            )
            await bot_manager.get_bot().send_message(
                chat_id=1008265857, text=markdown.markdown_decoration.quote(f"{captain_id}: " + message)
            )