from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from menu import main_menu
from config import asession
from tables import UsersTable
from admin.adm_utils import users_cache

reg = Router()


class BotReg(StatesGroup):
    nick = State()
    club = State()
    pfp = State()
    polemica_id = State()


@reg.message(CommandStart())
async def start_nick(message: Message, state: FSMContext):
    async with asession() as session:
        registered = await session.get(UsersTable, message.from_user.id)
    if registered:
        await main_menu(message)
        return
    await message.answer("👋Привет! Введи свой игровой ник⬇")
    await state.set_state(BotReg.nick)


@reg.message(BotReg.nick)
async def start_club(message: Message, state: FSMContext):
    await state.update_data(nick=message.text)
    markup = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="TechnoMafia"),
            KeyboardButton(text="Черный ход"),
            KeyboardButton(text="BONCHMAFIA")
        ],
        [
            KeyboardButton(text="Mining Mafia"),
            KeyboardButton(text="Polytech mafia community"),
            KeyboardButton(text="Вечерняя партия")
        ],
        [
            KeyboardButton(text="PolemicaSPb"),
            KeyboardButton(text="Иллюzия ОбмаNа"),
            KeyboardButton(text="TITAN SPb"),
            KeyboardButton(text="FoxMafia")
        ]
    ], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("👍Прекрасно! Теперь введи свой клуб (или выбери из предложенных)⬇", reply_markup=markup)
    await state.set_state(BotReg.club)


@reg.message(BotReg.club)
async def start_polemica_id(message: Message, state: FSMContext):
    await state.update_data(club=message.text)
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Пропустить")
    ]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("👌Отлично! Если ты зарегистрирован на сайте https://polemicagame.com, " +
                         "то отправь свой id профиля (перейти на сайт, затем перейти в профиль " +
                         "и скопировать цифры из адреса ссылки)⬇", reply_markup=markup)
    await state.set_state(BotReg.polemica_id)


@reg.message(BotReg.polemica_id)
async def start_pfp(message: Message, state: FSMContext):
    if message.text != "Пропустить":
        await state.update_data(polemica_id=message.text)
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Пропустить")
    ]], resize_keyboard=True)
    await message.answer("🤟Круто! И наконец, отправь свою фотографию." +
                         "Она будет использоваться для анонсов турниров⬇", reply_markup=markup)
    await state.set_state(BotReg.pfp)


@reg.message(BotReg.pfp)
async def start_final(message: Message, state: FSMContext):
    if not message.photo and message.text != "Пропустить":
        await message.answer("❌Вы отправили не фото! Отправьте фотографию или нажмите на кнопку")
        return
    if message.photo:
        await state.update_data(pfp=message.photo[-1].file_id)
    data = await state.get_data()
    await state.clear()
    async with asession() as session:
        user = UsersTable(id=message.from_user.id,
                          username=message.from_user.username,
                          nick=data["nick"],
                          club=data["club"])
        if "polemica_id" in data:
            user.polemica_id = data["polemica_id"]
        if "pfp" in data:
            user.pfp = data["pfp"]
        session.add(user)
        await session.commit()
    users_cache.clear()
    await message.answer("👏Вы успешно зарегистрировались!", reply_markup=ReplyKeyboardRemove())
    await main_menu(message)
