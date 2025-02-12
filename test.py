# # импортируем модуль

# from bs4 import BeautifulSoup

# with open('test.html', encoding='utf-8') as f:
#         html = f.read()

# # инициализируем html-код страницы
# soup = BeautifulSoup(html, 'lxml')
# # считываем заголовок страницы
# data = soup.find_all("td", )
# res = []
# for i, el in enumerate(data):
#     if el.text == "BLE метка ":
#         mark = data[i-3].text
#         id =  data[i-4].text
#         res.append((id, mark))


# with open("marks.txt", "w") as f:
#     for mark in res:
#         f.write(f"{mark[0]} {mark[1]}\n")


from telethon import TelegramClient, events
from bot.config import settings
