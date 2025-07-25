from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, delete, desc
from pymorphy3 import MorphAnalyzer

from config import asession, pay
from tables import TournamentsTable, RegistrationsTable, UsersTable, PaymentsTable
from utils import is_user_registered, get_tournament_info, is_user_paid

tourn = Router()
morph = MorphAnalyzer()


@tourn.callback_query(F.data == "tournaments")
async def tournament_list(callback: CallbackQuery):
    async with (asession() as session):
        query = select(TournamentsTable.name, TournamentsTable.num, TournamentsTable.status).where(
            TournamentsTable.club == "StudLeague")
        result = await session.execute(query)
        tournament_names = result.mappings().all()
    markup = InlineKeyboardBuilder()
    for i in tournament_names:
        if i.status != 0:
            markup.row(InlineKeyboardButton(text=i.name, callback_data="tourn_info" + str(i.num)))
    markup.row(InlineKeyboardButton(text="📌Меню", callback_data="menu"))
    await callback.answer()
    await callback.message.answer("🕹Выберите турнир:", reply_markup=markup.as_markup())


@tourn.callback_query(F.data == "events")
async def event_list(callback: CallbackQuery):
    async with (asession() as session):
        query = (select(TournamentsTable.name, TournamentsTable.num, TournamentsTable.club, TournamentsTable.status)
                 .where(TournamentsTable.club != "StudLeague"))
        result = await session.execute(query)
        tournament_names = result.mappings().all()
    markup = InlineKeyboardBuilder()
    for i in tournament_names:
        if i.status != 0:
            markup.row(InlineKeyboardButton(text=f"{i.club} - {i.name}", callback_data="tourn_info" + str(i.num)))
    markup.row(InlineKeyboardButton(text="📌Меню", callback_data="menu"))
    await callback.answer()
    await callback.message.answer("🕹Выберите турнир:", reply_markup=markup.as_markup())


@tourn.callback_query(F.data[:10] == "tourn_info")
async def tournament_info(callback: CallbackQuery):
    tourn_info = await get_tournament_info(int(callback.data[10:]))
    members = tourn_info[1]
    tourn_info = tourn_info[0]

    markup = InlineKeyboardBuilder()
    user_registered = await is_user_registered(callback.from_user.id, int(callback.data[10:]))
    if not user_registered and members < int(tourn_info.limit):
        markup.add(InlineKeyboardButton(text="🎫Зарегистрироваться", callback_data="registration" + callback.data[10:]))
    elif user_registered:
        markup.add(
            InlineKeyboardButton(text="🎟Отменить регистрацию", callback_data="unregistration" + callback.data[10:]))
        if tourn_info.cost > 0 and not await is_user_paid(callback.from_user.id, int(callback.data[10:])):
            markup.add(InlineKeyboardButton(text="💸Оплатить участие", callback_data="pay" + callback.data[10:]))
    markup.add(
        InlineKeyboardButton(text="🙋‍♂️Список участников", callback_data="participants" + callback.data[10:]),
        InlineKeyboardButton(text="📌Меню", callback_data="menu")).adjust(1)

    text = f"""
{tourn_info.name}\n
{tourn_info.desc}\n
📏Дистанция: {tourn_info.distance} {morph.parse('игра')[0].make_agree_with_number(tourn_info.distance).word}
🗓Дата: {tourn_info.date}
📖Федерация: {tourn_info.federation}
🗄Тип: {"Личный" if tourn_info.type else "Командный"}\n
💸Стоимость: {tourn_info.cost} рублей
🙍‍♂️Лимит: {(str(members) + "/") if members else ""}{tourn_info.limit} участников
💡Статус: {"По заявкам" if tourn_info.status == 2 else ("Открытый" if tourn_info.status == 1 else "Скрытый")}
"""
    if tourn_info.pfp:
        await callback.answer()
        await callback.message.answer_photo(tourn_info.pfp, text, reply_markup=markup.as_markup())
    else:
        await callback.message.edit_text(text, reply_markup=markup.as_markup())


@tourn.callback_query(F.data[:12] == "registration")
async def registration(callback: CallbackQuery):
    await callback.answer()
    if await is_user_registered(callback.from_user.id, int(callback.data[12:])):
        await callback.message.answer("🎟Вы уже зарегистрированы!")
        return
    async with asession() as session:
        query = select(TournamentsTable.status).where(TournamentsTable.num == int(callback.data[12:]))
        result = await session.execute(query)
        status = result.all()[0][0]
        new_reg = RegistrationsTable(user_id=callback.from_user.id,
                                     event_id=int(callback.data[12:]))
        if status == 2:
            new_reg.request = True
        session.add(new_reg)
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆Турнир", callback_data="tourn_info" + callback.data[12:])],
        [InlineKeyboardButton(text="🙍‍♂️Список участников", callback_data="participants" + callback.data[12:])],
        [InlineKeyboardButton(text="🎟Отменить регистрацию", callback_data="unregistration" + callback.data[12:])],
        [InlineKeyboardButton(text="📌Меню", callback_data="menu")]
    ])
    await callback.message.answer("🎉Вы успешно зарегистрировались!", reply_markup=markup)


@tourn.callback_query(F.data[:12] == "participants")
async def participants(callback: CallbackQuery):
    async with asession() as session:
        query = (select(RegistrationsTable.paid, RegistrationsTable.request, UsersTable.nick, UsersTable.username,
                        UsersTable.club)
                 .join(UsersTable, RegistrationsTable.user_id == UsersTable.id)
                 .where(RegistrationsTable.event_id == int(callback.data[12:])))
        result = await session.execute(query)
        members = result.all()
    answer = ""
    cnt = 0
    for i in members:
        cnt += 1
        if not i.request:
            if i.paid:
                answer += "💷"
            answer += f"{str(cnt)}. {i.nick} - @{i.username} - {i.club}\n"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆Турнир", callback_data="tourn_info" + callback.data[12:])],
        [InlineKeyboardButton(text="📌Меню", callback_data="menu")]
    ])
    if not answer:
        await callback.answer("🕳Участников нет!")
        return
    if not callback.message.photo:
        await callback.message.edit_text(answer, reply_markup=markup)
    else:
        await callback.message.answer(answer, reply_markup=markup)


@tourn.callback_query(F.data[:14] == "unregistration")
async def unregistration(callback: CallbackQuery):
    async with asession() as session:
        query = (delete(RegistrationsTable)
                 .where(((RegistrationsTable.event_id == int(callback.data[14:]))
                         & (RegistrationsTable.user_id == callback.from_user.id))))
        await session.execute(query)
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆Турнир", callback_data="tourn_info" + callback.data[14:])],
        [InlineKeyboardButton(text="🙍‍♂️Список участников", callback_data="participants" + callback.data[14:])],
        [InlineKeyboardButton(text="📌Меню", callback_data="menu")]
    ])
    await callback.answer()
    await callback.message.answer("❎Вы успешно отменили регистрацию", reply_markup=markup)


@tourn.callback_query(F.data[:3] == "pay")
async def create_invoice(callback: CallbackQuery):
    if not await is_user_registered(callback.from_user.id, int(callback.data[3:])):
        await callback.message.answer("Вы не зарегистрированы!")
        return
    async with (asession() as session):
        query = select(TournamentsTable.cost, TournamentsTable.name).where(
            TournamentsTable.num == int(callback.data[3:]))
        result = await session.execute(query)
        tourn_info = result.all()[0]
        query = select(RegistrationsTable.num
                       ).where((RegistrationsTable.user_id == callback.from_user.id) &
                               (RegistrationsTable.event_id == int(callback.data[3:])))
        result = await session.execute(query)
        user_num_in_reg = result.scalar_one_or_none()
    await callback.message.answer_invoice(title="Оплатить участие",
                                          description="Оплата участия в " + tourn_info.name,
                                          provider_token=pay,
                                          payload=str(user_num_in_reg),
                                          currency="RUB",
                                          prices=[LabeledPrice(label="Оплата",  amount=tourn_info.cost * 100)]
                                          )


@tourn.pre_checkout_query()
async def pre_check(query: PreCheckoutQuery):
    async with asession() as session:  # Логи оплаты
        payment = PaymentsTable(user_id=query.from_user.id,
                                reg_id=int(query.invoice_payload),
                                cost=query.total_amount)
        session.add(payment)
        await session.commit()
    await query.answer(ok=True)


@tourn.message(F.successful_payment)
async def successful_pay(message: Message):
    payment = message.successful_payment
    async with asession() as session:
        user = await session.get(RegistrationsTable, int(payment.invoice_payload))
        if not user:
            await message.answer("Оплата прошла, но при обработке произошла ошибка. Сообщите " +
                                 "организаторам об оплате!")
            return
        user.paid = True
        num = user.event_id

        paym = session.query(PaymentsTable).order_by(desc(PaymentsTable.num)).limit(1).first()
        paym.was = True
        await session.commit()
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏆Турнир", callback_data="tourn_info" + str(num))
    ]])
    await message.answer("Оплата прошла успешно!", reply_markup=markup)
