from aiogram import Bot
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv(dotenv_path="./.venv/.env")
token = Bot(os.getenv("key"))
pay = os.getenv("pay")
bdKey = os.getenv("db")

engine = create_async_engine(url=bdKey)

asession = async_sessionmaker(engine)


clubs_list = ["StudLeague", "TechnoMafia"]
