from aiogram import Bot
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

load_dotenv(dotenv_path="./.venv/.env")
token = Bot(os.getenv("key"))
pay = os.getenv("pay")

engine = create_async_engine(url="sqlite+aiosqlite:///./studleague.db")

asession = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


clubs_list = ["StudLeague", "TechnoMafia"]
