from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy import select

from config import asession
from tables import AdminsTable

menu = Router()


async def main_menu(message: Message):
    async with asession() as session:
        query = select(AdminsTable.id)
        result = await session.execute(query)
        admins = result.all()[0]
    markup = InlineKeyboardBuilder([
        [
            InlineKeyboardButton(text="🏆Турниры", callback_data="tournaments"),
            InlineKeyboardButton(text="🎮Клубные турниры", callback_data="events"),
            InlineKeyboardButton(text="🔑Профиль", callback_data="profile_show")
        ],
        [
            InlineKeyboardButton(text="📖Правила", url="https://clck.ru/3MYPfq"),
            InlineKeyboardButton(text="🗯Группа VK", url="https://vk.com/studmafiaspb"),
            InlineKeyboardButton(text="🛠Техподдержка", url="https://t.me/acc_maf")
        ]
    ])
    if message.chat.id in admins:
        markup.row(InlineKeyboardButton(text="⚙Админ панель", callback_data="admin_menu"))
    await message.answer("📌Выберите опцию:", reply_markup=markup.as_markup())


@menu.message(Command("id"))
async def user_id_answer(message: Message):
    await message.answer("🫵Твой id: ", str(message.from_user.id))


@menu.callback_query(F.data == "menu")
async def menu_from_callback(callback: CallbackQuery):
    await callback.answer()
    await main_menu(callback.message)


@menu.message()
async def menu_from_message(message: Message):
    '''async with asession() as session:
        user = AdminsTable(id=message.from_user.id,
                      clubs="['*']")
        session.add(user)
        await session.commit()'''
    await main_menu(message)
