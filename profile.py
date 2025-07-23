from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import asession
from tables import UsersTable
from menu import main_menu

profile = Router()


class ProfileChange(StatesGroup):
    nick = State()
    club = State()
    pfp = State()


@profile.callback_query(F.data == "profile_show")
async def profile_show(callback: CallbackQuery):
    await callback.answer()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌Меню", callback_data="menu")],
        [InlineKeyboardButton(text="📝Изменить профиль", callback_data="profile_change")]
    ])
    async with asession() as session:
        profile_info = await session.get(UsersTable, callback.from_user.id)
    if profile_info.pfp:
        await callback.message.answer_photo(profile_info.pfp,
                                            f"🙍‍♂️Ваш профиль:\n\nНик: {profile_info.nick}\nКлуб: {profile_info.club}",
                                            reply_markup=markup)
    else:
        await callback.message.answer(f"🙍‍♂️Ваш профиль:\n\nНик: {profile_info.nick}\nКлуб: {profile_info.club}",
                                      reply_markup=markup)


@profile.callback_query(F.data == "profile_change")
async def profile_change_choose(callback: CallbackQuery):
    await callback.answer()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Ник", callback_data="profile_change_nick"),
            InlineKeyboardButton(text="Клуб", callback_data="profile_change_club"),
            InlineKeyboardButton(text="Картинка", callback_data="profile_change_pfp")
        ],
        [
            InlineKeyboardButton(text="📌Меню", callback_data="menu")
        ]])
    await callback.message.answer("Выберите, что вы хотите изменить:", reply_markup=markup)


@profile.callback_query(F.data[:15] == "profile_change_")
async def profile_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data[15:] == "nick":
        await callback.message.answer("Введите новый ник")
        await state.set_state(ProfileChange.nick)
    elif callback.data[15:] == "club":
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
        await callback.message.answer("Введите новый клуб или выберите из списка:", reply_markup=markup)
        await state.set_state(ProfileChange.club)
    else:
        await callback.message.answer("Отправьте новую картинку")
        await state.set_state(ProfileChange.pfp)


@profile.message(ProfileChange.nick)
async def profile_update_nick(message: Message, state: FSMContext):
    await state.clear()
    async with asession() as session:
        profile_info = await session.get(UsersTable, message.from_user.id)
        profile_info.nick = message.text
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📌Меню", callback_data="menu"),
        InlineKeyboardButton(text="🔑Профиль", callback_data="profile_show")
    ]])
    await message.answer("🎉Успешно", reply_markup=markup)
    await main_menu(message)


@profile.message(ProfileChange.club)
async def profile_update_club(message: Message, state: FSMContext):
    await state.clear()
    async with asession() as session:
        profile_info = await session.get(UsersTable, message.from_user.id)
        profile_info.club = message.text
        await session.commit()
    await message.answer("🎉Успешно")
    await main_menu(message)


@profile.message(ProfileChange.pfp)
async def profile_update_pfp(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌Вы отправили не фото! Попробуйте отправить ещё раз")
        return
    await state.clear()
    async with asession() as session:
        profile_info = await session.get(UsersTable, message.from_user.id)
        profile_info.pfp = message.photo[-1].file_id
        await session.commit()
    await message.answer("🎉Успешно")
    await main_menu(message)
