from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, delete

from config import asession, clubs_list
from tables import AdminsTable, TournamentsTable, RegistrationsTable, UsersTable
from tournaments import morph
from admin.adm_utils import photo_to_file, all_users, get_payments_logs

ad_menu = Router()


@ad_menu.callback_query(F.data == 'admin_menu')
async def panel(callback: CallbackQuery):
    async with asession() as session:
        query = select(AdminsTable.clubs).where(AdminsTable.id == callback.from_user.id)
        result = await session.execute(query)
        clubs = eval(result.all()[0][0])
    if clubs[0] == '*':
        markup = InlineKeyboardBuilder()
        for i in clubs_list:
            markup.add(InlineKeyboardButton(text=i, callback_data='adminka' + i))
        markup.adjust(2).row(InlineKeyboardButton(text="🙍‍♂️Пользователи бота", callback_data="all_users"),
                   InlineKeyboardButton(text="💌Рассылка для всех", callback_data="newsletter0"))
        markup.row(InlineKeyboardButton(text="Глобальные админы", callback_data="admin_list" + '*'),
                   InlineKeyboardButton(text="💴👀Логи оплаты", callback_data="logs_payments"),
                   InlineKeyboardButton(text="📌Меню", callback_data="menu"))
    else:
        markup = InlineKeyboardBuilder()
        for i in clubs:
            markup.add(InlineKeyboardButton(text=i, callback_data='adminka' + i))
        markup.adjust(2).add(InlineKeyboardButton(text="📌Меню", callback_data="menu"))
    await callback.answer()
    await callback.message.answer("⚙Вы админ!", reply_markup=markup.as_markup())


@ad_menu.callback_query(F.data[:7] == 'adminka')
async def tourn_list(callback: CallbackQuery):
    async with (asession() as session):
        query = (select(TournamentsTable.name, TournamentsTable.num)
                 .where(TournamentsTable.club == callback.data[7:]))
        result = await session.execute(query)
        tournament_names = result.mappings().all()
    markup = InlineKeyboardBuilder().add(
        InlineKeyboardButton(text="🏆Создать турнир", callback_data="create_tourn" + callback.data[7:]))
    for i in tournament_names:
        markup.row(InlineKeyboardButton(text=i.name, callback_data="admin_tourn_info" + str(i.num)))
    markup.row(InlineKeyboardButton(text="🙍‍♂️Админы", callback_data="admin_list" + callback.data[7:]))
    markup.row(InlineKeyboardButton(text="📌Меню", callback_data="menu"))
    await callback.answer()
    await callback.message.answer("🕹Выберите турнир:", reply_markup=markup.as_markup())


@ad_menu.callback_query(F.data[:16] == "admin_tourn_info")
async def tournament_info(callback: CallbackQuery):
    async with asession() as session:
        query = select(TournamentsTable).where(TournamentsTable.num == int(callback.data[16:]))
        result = await session.execute(query)
        tourn_info = result.all()[0][0]
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✒Изменить турнир", callback_data="edit_tourn" + str(tourn_info.num)),
         InlineKeyboardButton(text="🗑Удалить турнир", callback_data="delete_tourn" + str(tourn_info.num))],
        [InlineKeyboardButton(text="💌Рассылка", callback_data="newsletter" + str(tourn_info.num)),
         InlineKeyboardButton(text="🖼Профили участников", callback_data="profiles" + str(tourn_info.num))],
        [InlineKeyboardButton(text="🙋‍♂️Участники и заявки", callback_data="adparticipants" + str(tourn_info.num)),
         InlineKeyboardButton(text="📌Меню", callback_data="menu")]
    ])
    text = f"""
{tourn_info.name}\n
{tourn_info.desc}\n
📏Дистанция: {tourn_info.distance} {morph.parse('игра')[0].make_agree_with_number(tourn_info.distance).word}
🗓Дата: {tourn_info.date}
📖Федерация: {tourn_info.federation}
🗄Тип: {"Личный" if tourn_info.type else "Командный"}\n
💸Стоимость: {tourn_info.cost} рублей
🙍‍♂️Лимит: {tourn_info.limit} участников
💡Статус: {"По заявкам" if tourn_info.status == 2 else ("Открытый" if tourn_info.status == 1 else "Скрытый")}
"""
    await callback.answer()
    if tourn_info.pfp:
        await callback.message.answer_photo(tourn_info.pfp, text, reply_markup=markup)
    else:
        await callback.message.edit_text(text, reply_markup=markup)


@ad_menu.callback_query(F.data[:14] == "adparticipants")
async def participants(callback: CallbackQuery):
    async with asession() as session:
        query = (select(RegistrationsTable.paid, RegistrationsTable.request, UsersTable.nick, UsersTable.username,
                        UsersTable.club)
                 .join(UsersTable, RegistrationsTable.user_id == UsersTable.id)
                 .where(RegistrationsTable.event_id == int(callback.data[14:])))
        result = await session.execute(query)
        members = result.all()
    answer = ""
    cnt = 0
    are_requests = False
    for i in members:
        cnt += 1
        if i.request:
            answer += "🙏"
            are_requests = True
        elif i.paid:
            answer += "💷"
        answer += f"{str(cnt)}. {i.nick} - @{i.username} - {i.club}\n"
    markup = InlineKeyboardBuilder()
    if are_requests:
        markup.row(InlineKeyboardButton(text="🙋‍♂️Заявки", callback_data="requests" + callback.data[14:]))
    markup.add(InlineKeyboardButton(text="🏆Турнир", callback_data="admin_tourn_info" + callback.data[14:]),
               InlineKeyboardButton(text="📌Меню", callback_data="menu")).adjust(1)
    if not answer:
        await callback.answer("🕳Участников нет!")
        return
    await callback.answer()
    await callback.message.answer(answer, reply_markup=markup.as_markup())


@ad_menu.callback_query(F.data[:8] == "requests")
async def requests(callback: CallbackQuery):
    async with asession() as session:
        query = (select(RegistrationsTable.request, RegistrationsTable.num, UsersTable.nick, UsersTable.club)
                 .join(UsersTable, RegistrationsTable.user_id == UsersTable.id)
                 .where((RegistrationsTable.event_id == int(callback.data[8:]))
                        & (RegistrationsTable.request == 1)))
        result = await session.execute(query)
        request_list = result.all()
    if not request_list:
        await callback.answer("🕳Заявок нет!")
        return
    for i in request_list:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅Принять", callback_data="accept" + str(i.num))],
            [InlineKeyboardButton(text="❌Отклонить", callback_data="decline" + str(i.num))]
        ])
        await callback.message.answer(f"Ник: {i.nick}, Клуб: {i.club}", reply_markup=markup)
    await callback.answer()


@ad_menu.callback_query(F.data[:6] == "accept")
async def accept(callback: CallbackQuery):
    async with asession() as session:
        request_info = await session.get(RegistrationsTable, int(callback.data[6:]))
        request_info.request = False
        await session.commit()
    await callback.message.edit_text("✅Заявка принята")


@ad_menu.callback_query(F.data[:6] == "decline")
async def decline(callback: CallbackQuery):
    async with asession() as session:
        query = (delete(RegistrationsTable)
                 .where(RegistrationsTable.num == int(callback.data[6:])))
        await session.execute(query)
        await session.commit()
    await callback.message.edit_text("❎Заявка отклонена")


@ad_menu.callback_query(F.data[:8] == "profiles")
async def profiles(callback: CallbackQuery):
    async with asession() as session:
        query = (select(RegistrationsTable.request, UsersTable.nick, UsersTable.username, UsersTable.club,
                        UsersTable.pfp, UsersTable.polemica_id)
                 .join(UsersTable, RegistrationsTable.user_id == UsersTable.id)
                 .where(RegistrationsTable.event_id == int(callback.data[8:])))
        result = await session.execute(query)
        members = result.all()
    await callback.answer()
    for i in members:
        if not i.request:
            text = f"{i.nick} - @{i.username} - {i.club}"
            if i.pfp:
                if i.polemica_id:
                    await callback.message.answer_document(document=await photo_to_file(i.pfp, i.polemica_id),
                                                           caption=text)
                else:
                    await callback.message.answer_document(document=await photo_to_file(i.pfp, i.nick),
                                                           caption=text)
            else:
                await callback.message.answer(text)


@ad_menu.callback_query(F.data == "all_users")
async def users(callback: CallbackQuery):
    us = await all_users()
    await callback.answer()
    for i in us:
        await callback.message.answer(i)


@ad_menu.callback_query(F.data == "logs_payments")
async def payments_logs(callback: CallbackQuery):
    pays = await get_payments_logs()
    await callback.answer()
    for i in pays:
        await callback.message.answer(i)
