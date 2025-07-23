from aiogram import Dispatcher
import asyncio

from config import token
from tables import create_tables
from reg import reg
from tournaments import tourn
from menu import menu
from profile import profile
from admin.tourns import ad_menu
from admin.tourn_actions import ad_tourn


async def start():
    await create_tables()

    dp = Dispatcher()

    dp.include_routers(reg, profile, tourn, ad_menu, ad_tourn, menu)
    await dp.start_polling(token)


if __name__ == '__main__':
    try:
        asyncio.run(start())
    except:
        pass
