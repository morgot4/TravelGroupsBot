import aiohttp
import asyncio


async def fetch_updates(url):
    """Функция, которая раз в секунду запрашивает обновления с сервера."""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(await response.json())
                        # await process_updates(data)
        except Exception as e:
            print(f"Ошибка при запросе {url}:\n {e}")

        await asyncio.sleep(2)


async def process_updates(data):
    for item in data:
        print(item)
