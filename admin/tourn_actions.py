from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, delete
from utils import tourn_cache

from config import asession, token
from tournaments import morph
from tables import TournamentsTable, RegistrationsTable, UsersTable, AdminsTable

ad_tourn = Router()


class TournCreate(StatesGroup):
    club = State()
    name = State()
    desc = State()
    distance = State()
    date = State()
    federation = State()
    type = State()
    cost = State()
    limit = State()
    status = State()
    pfp = State()


class TournEdit(StatesGroup):
    num = State()
    field = State()
    in_bd = State()


class TournDelete(StatesGroup):
    confirm = State()


class Newsletter(StatesGroup):
    num = State()
    text = State()
    confirm = State()


class AdminAdd(StatesGroup):
    club = State()
    id = State()


class AdminRemove(StatesGroup):
    club = State()
    id = State()


@ad_tourn.callback_query(F.data[:12] == 'create_tourn')
async def create_tournament1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(club=callback.data[12:])
    await state.set_state(TournCreate.name)
    await callback.answer()
    await callback.message.answer("Введите название турнира:")


@ad_tourn.message(TournCreate.name)
async def create_tournament2(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(TournCreate.desc)
    await message.answer("Введите описание турнира:")


@ad_tourn.message(TournCreate.desc)
async def create_tournament3(message: Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await state.set_state(TournCreate.distance)
    await message.answer("Введите количество игр (только число):")


@ad_tourn.message(TournCreate.distance)
async def create_tournament4(message: Message, state: FSMContext):
    try:
        int(message.text)
    except:
        await message.answer("❌Вы ввели не целое число!\nВведите количество игр числом:")
        return
    await state.update_data(distance=message.text)
    await state.set_state(TournCreate.date)
    await message.answer("Введите дату турнира:")


@ad_tourn.message(TournCreate.date)
async def create_tournament5(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(TournCreate.federation)
    await message.answer("Введите федерацию, по правилам которой проходит турнир (Polemica, ФСМ, МСЛ):")


@ad_tourn.message(TournCreate.federation)
async def create_tournament6(message: Message, state: FSMContext):
    await state.update_data(federation=message.text)
    await state.set_state(TournCreate.type)
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Личный"), KeyboardButton(text="Командный")]],
                                 resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите тип турнира:", reply_markup=markup)


@ad_tourn.message(TournCreate.type)
async def create_tournament7(message: Message, state: FSMContext):
    await state.update_data(type=False if message.text == "Командный" else True)
    await state.set_state(TournCreate.cost)
    await message.answer("Введите стоимость турнира (только число в рублях). Если турнир бесплатный, введите 0:")


@ad_tourn.message(TournCreate.cost)
async def create_tournament8(message: Message, state: FSMContext):
    try:
        int(message.text)
    except:
        await message.answer(
            "❌Вы ввели не целое число!\nВведите стоимость турнира в рублях. Если турнир бесплатный, введите 0:")
        return
    await state.update_data(cost=message.text)
    await state.set_state(TournCreate.limit)
    await message.answer("Введите лимит участников турнира (только число):")


@ad_tourn.message(TournCreate.limit)
async def create_tournament9(message: Message, state: FSMContext):
    try:
        int(message.text)
    except:
        await message.answer("❌Вы ввели не целое число!\nВведите максимальное число участников турнира:")
        return
    await state.update_data(limit=message.text)
    await state.set_state(TournCreate.status)
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Скрытый"),
        KeyboardButton(text="Открытый"),
        KeyboardButton(text="По заявкам")
    ]], one_time_keyboard=True, resize_keyboard=True)
    await message.answer("Выберите статус турнира на данный момент:", reply_markup=markup)


@ad_tourn.message(TournCreate.status)
async def create_tournament10(message: Message, state: FSMContext):
    await state.update_data(status=2 if message.text == "По заявкам" else (1 if message.text == "Открытый" else 0))
    await state.set_state(TournCreate.pfp)
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Пропустить")
    ]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("📷Отправьте 1 фотографию-обложку турнира или нажмите кнопку:", reply_markup=markup)


@ad_tourn.message(TournCreate.pfp)
async def create_tournament11(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(pfp=message.photo[-1].file_id)
    data = await state.get_data()
    await state.clear()
    async with asession() as session:
        new_tournament = TournamentsTable(club=data["club"],
                                          name=data["name"],
                                          desc=data["desc"],
                                          distance=data["distance"],
                                          date=data["date"],
                                          federation=data["federation"],
                                          type=data["type"],
                                          cost=data["cost"],
                                          limit=data["limit"],
                                          status=data["status"])
        if "pfp" in data:
            new_tournament.pfp = data["pfp"]
        session.add(new_tournament)
        await session.flush()
        tourn_id = new_tournament.num
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏆Турнир", callback_data="admin_tourn_info" + str(tourn_id))]])
    await message.answer("🎉Турнир успешно создан!", reply_markup=markup)


@ad_tourn.callback_query(F.data[:10] == 'edit_tourn')
async def edit_tournament1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TournEdit.field)
    await state.update_data(num=callback.data[10:])
    markup = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="Название"),
            KeyboardButton(text="Описание"),
            KeyboardButton(text="Дистанция")
        ],
        [
            KeyboardButton(text="Дата"),
            KeyboardButton(text="Федерация"),
            KeyboardButton(text="Стоимость")
        ],
        [
            KeyboardButton(text="Лимит участников"),
            KeyboardButton(text="Статус"),
            KeyboardButton(text="Картинку")
        ]
    ], resize_keyboard=True, one_time_keyboard=True)
    await callback.answer()
    await callback.message.answer("🕹Выберите, что вы хотите изменить:", reply_markup=markup)


@ad_tourn.message(TournEdit.field)
async def edit_tournament2(message: Message, state: FSMContext):
    await state.set_state(TournEdit.in_bd)
    await state.update_data(field=message.text)
    if message.text == "Картинку":
        await message.answer("📷Отправьте новую картинку:")
    if message.text != "Статус":
        await message.answer(f"Введите {morph.parse("новый")[0].
                             inflect({morph.parse(message.text.lower())[0].tag.gender}).word
                             if morph.parse(message.text.lower())[0].tag.gender else "новый"} {message.text.lower()}")
        return
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="Скрытый"),
        KeyboardButton(text="Открытый"),
        KeyboardButton(text="По заявкам"),
    ]], resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите новый статус:", reply_markup=markup)


@ad_tourn.message(TournEdit.in_bd)
async def edit_tournament3(message: Message, state: FSMContext):
    data = await state.get_data()
    async with asession() as session:
        info = await session.get(TournamentsTable, int(data["num"]))
        match data["field"]:
            case "Название":
                info.name = message.text
            case "Описание":
                info.desc = message.text
            case "Дистанция":
                try:
                    int(message.text)
                except:
                    await message.answer("Вы ввели не целое число!\nВведите максимальное число участников турнира:")
                    return
                info.distance = int(message.text)
            case "Дата":
                info.date = message.text
            case "Федерация":
                info.federation = message.text
            case "Стоимость":
                try:
                    int(message.text)
                except:
                    await message.answer("❌Вы ввели не целое число!\nВведите стоимость турнира:")
                    return
                info.cost = int(message.text)
            case "Лимит участников":
                try:
                    int(message.text)
                except:
                    await message.answer("❌Вы ввели не целое число!\nВведите максимальное число участников турнира:")
                    return
                info.limit = int(message.text)
            case "Статус":
                info.status = 2 if message.text == "По заявкам" else (1 if message.text == "Открытый" else 0)
            case "Картинку":
                if not message.photo:
                    await message.answer("❌Вы отправили не картинку!\nПопробуйте ещё раз")
                    return
                info.pfp = message.photo[-1].file_id
        await session.commit()
    await state.clear()
    tourn_cache.clear()
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏆Турнир", callback_data="admin_tourn_info" + str(data["num"]))]])
    await message.answer("✅Изменения успешно внесены!", reply_markup=markup)


@ad_tourn.callback_query(F.data[:12] == 'delete_tourn')
async def delete_tournament1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TournDelete.confirm)
    await state.update_data(confirm=callback.data[12:])
    await callback.answer()
    await callback.message.answer("‼Вы точно хотите удалить турнир? Введите ДА для подтверждения")


@ad_tourn.message(TournDelete.confirm)
async def delete_tournament2(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    if message.text != "ДА":
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🏆Турнир", callback_data="admin_tourn_info" + str(data["confirm"]))]])
        await message.answer("❎Действие отменено", reply_markup=markup)
        return
    async with asession() as session:
        query = (delete(RegistrationsTable)
                 .where(RegistrationsTable.event_id == int(data["confirm"])))
        await session.execute(query)
        query = (delete(TournamentsTable)
                 .where(TournamentsTable.num == int(data["confirm"])))
        await session.execute(query)
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📌Меню", callback_data="menu")]])
    await message.answer("✅Турнир успешно удален", reply_markup=markup)


@ad_tourn.callback_query(F.data[:10] == "newsletter")
async def newsletter1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(num=int(callback.data[10:]))
    await state.set_state(Newsletter.text)
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отменить")]], resize_keyboard=True, one_time_keyboard=True)
    await callback.answer()
    await callback.message.answer("💬Введите текст, который хотите разослать:", reply_markup=markup)


@ad_tourn.message(Newsletter.text)
async def newsletter2(message: Message, state: FSMContext):
    if message.text == "Отменить":
        await state.clear()
        await message.answer("❎Отменено")
        return
    await state.update_data(text=message.text)
    await state.set_state(Newsletter.confirm)
    await message.answer("‼Вы уверены, что хотите разослать это сообщение?\nВведите ДА, чтобы разослать")


@ad_tourn.message(Newsletter.confirm)
async def newsletter3(message: Message, state: FSMContext):
    if message.text != "ДА":
        await state.clear()
        await message.answer("❎Рассылка отменена")
    data = await state.get_data()
    if data["num"] == 0:
        await newsletter4(message, data)
        return
    async with asession() as session:
        query = select(RegistrationsTable.user_id).where(data["num"] == RegistrationsTable.event_id)
        result = await session.execute(query)
        users = result.all()
        tourn_name = await session.get(TournamentsTable, data["num"])
    text = f"<b>{tourn_name.name}</b>\n\n{data["text"]}"
    if not users:
        await message.answer("Участников нет!")
        return
    for i in users[0]:
        await token.send_message(i, text, parse_mode="html")
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏆Турнир", callback_data="admin_tourn_info" + str(data["num"])),
        InlineKeyboardButton(text="📌Меню", callback_data="menu")
    ]])
    await message.answer("🎉Успешно!", reply_markup=markup)


async def newsletter4(message: Message, data: dict):
    async with asession() as session:
        query = select(UsersTable.id)
        result = await session.execute(query)
        users = result.all()[0]
    for i in users:
        await token.send_message(i, data["text"])
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📌Меню", callback_data="menu")
    ]])
    await message.answer("🎉Успешно!", reply_markup=markup)


@ad_tourn.callback_query(F.data[:10] == "admin_list")
async def admin_list(callback: CallbackQuery):
    async with (asession() as session):
        query = select(UsersTable.nick, UsersTable.username, UsersTable.id, AdminsTable.clubs
                       ).join(AdminsTable, UsersTable.id == AdminsTable.id)
        result = await session.execute(query)
        all_admins = result.all()
    admins = []
    for i in all_admins:
        clubs = eval(i.clubs) if eval(i.clubs) is not None else []
        if callback.data[10:] in clubs:
            admins.append(i)
    markup = InlineKeyboardBuilder([[
        InlineKeyboardButton(text="➕Добавить админа", callback_data="add_admin" + callback.data[10:])
    ]])
    await callback.answer()
    if not admins:
        await callback.message.answer("🕳Админов нет!", reply_markup=markup.as_markup())
        return
    text = ""
    cnt = 0
    for i in admins:
        cnt += 1
        text += f"{cnt}. {i.nick} - @{i.username} - {i.id}\n"
    markup.row(InlineKeyboardButton(text="➖Удалить админа", callback_data="remove_admin" + callback.data[10:]))
    await callback.message.answer(text, reply_markup=markup.as_markup())


@ad_tourn.callback_query(F.data[:9] == "add_admin")
async def add_admin1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(club=callback.data[9:])
    await state.set_state(AdminAdd.id)
    await callback.answer()
    await callback.message.answer("#️⃣Попросите человека, которого вы хотите добавить в админы, прописать /id\n" +
                                  "Затем отправьте его id сюда:")


@ad_tourn.message(AdminAdd.id)
async def add_admin2(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    await state.clear()
    try:
        await token.get_chat(data["id"])
    except:
        await message.answer("❌Вы ввели неверный id!")
        return
    async with asession() as session:
        query = select(AdminsTable).where(AdminsTable.id == data["id"])
        result = await session.execute(query)
        admin_user = result.all()[0][0]
        clubs = eval(admin_user.clubs) if eval(admin_user.clubs) is not None else []
        if data["club"] in clubs:
            await message.answer("🙍‍♂️Пользователь уже является администратором!")
            return
        if not admin_user:
            new_admin = AdminsTable(id=data["id"], clubs='['+data["club"]+']')
            session.add(new_admin)
        else:
            clubs.append(data["club"])
            admin_info = await session.get(AdminsTable, data["id"])
            admin_info.clubs = str(clubs)
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙Список админов", callback_data="admin_list"+data["club"])],
        [InlineKeyboardButton(text="📌Меню", callback_data="menu")]
    ])
    await message.answer("🎉Админ был успешно добавлен", reply_markup=markup)


@ad_tourn.callback_query(F.data[:12] == "remove_admin")
async def remove_admin1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(club=callback.data[12:])
    await state.set_state(AdminRemove.id)
    await callback.answer()
    await callback.message.answer("#️⃣Введите id админа, которого вы хотите удалить, из списка выше")


@ad_tourn.message(AdminRemove.id)
async def remove_admin2(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    await state.clear()
    async with asession() as session:
        admin = await session.get(AdminsTable, data["id"])
        clubs = eval(admin.clubs) if eval(admin.clubs) is not None else []
        try:
            clubs.remove(data["club"])
        except:
            await message.answer("❌Вы ввели неверный id")
            return
        admin.clubs = str(clubs)
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙Список админов", callback_data="admin_list"+data["club"])],
        [InlineKeyboardButton(text="📌Меню", callback_data="menu")]
    ])
    await message.answer("🎉Успешно", reply_markup=markup)
