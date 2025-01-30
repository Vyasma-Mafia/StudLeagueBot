from defs_meros import *
import os
from config import settings
import telebot
from telebot import types
import sqlite3
from json import loads
import datetime

admins = ['7917683744', '737942168', '6070976396', '1396645155', '871296258', '1984219536', '1105133767']
technoadmins = ['469495683']  # Лжедмитрий
darkturnadmins = ['890876763', '831232089']  # Фиалка, Велосипедостроитель
letiadmins = ['985038251']  # Руина
bonchadmins = []
polytechadmins = []
miningadmins = ['5904573214']  # Пингвини
eveningadmins = ['625677497']  # Стронг
blackinsideadmins = ['672758760']  # Rearm

bot = telebot.TeleBot(settings['TOKEN'])
current_club = ''


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    base = sqlite3.connect('users')
    cur = base.cursor()
    cur.execute('SELECT id FROM users')
    users = cur.fetchall()
    cur.close()
    base.close()

    for i in users:
        if str(i[0]) == str(message.chat.id): # Зареган ли юзер? Да -> Кнопка меню и скип регистрации
            markup.add(types.InlineKeyboardButton('📌Меню', callback_data='menu'))
            markup.add(types.InlineKeyboardButton('👨‍🏫Гайд по боту', callback_data='help'))
            bot.send_message(message.chat.id, "Привет!👋\n", reply_markup=markup)
            break
    else:
        markup.add(types.InlineKeyboardButton('✏Создать профиль', callback_data='start_reg'))
        bot.send_message(message.chat.id, "Привет!👋\n", reply_markup=markup)


def start_reg(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('✏Создать профиль', web_app=types.WebAppInfo(
        url='https://acc-maf.github.io/StudLeagueBot/start_reg.html')))
    bot.send_message(message.chat.id, "Нажмите кнопку для регистрации", reply_markup=markup)


def end_reg(message, data):
    if data["nick"][0] == '/':
        bot.send_message(message.chat.id,
                         "Ник не может начинаться со /, введите данные заново", reply_markup=types.ReplyKeyboardRemove())
        start_reg(message)
        return
    base = sqlite3.connect('users')
    cur = base.cursor()
    cur.execute(f'DELETE FROM users WHERE id = {message.chat.id}')  # Удаление старого аккаунта пользователя
    base.commit()
    cur.execute(f'INSERT INTO users (id, nick, club) VALUES ("{message.chat.id}", "{data["nick"]}", "{data["club"]}")')
    base.commit()
    cur.close()
    base.close()
    bot.send_message(message.chat.id, "🎉Вы успешно зарегистрировались! Также вы можете прикрепить свое фото для анонсов турниров, нажав кнопку ниже.", message_effect_id='5046509860389126442', reply_markup=types.ReplyKeyboardRemove())
    profileshow(message)


@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton('🎮Игры в клубах', callback_data='clubs_list')
    btn2 = types.InlineKeyboardButton('🏆Турниры', callback_data='tournaments_list')
    btn3 = types.InlineKeyboardButton('🔑Профиль', callback_data='profile_show')
    btn4 = types.InlineKeyboardButton('🗓Расписание', callback_data='schedule')
    btn5 = types.InlineKeyboardButton('👨‍🏫Гайд по боту', callback_data='help')
    btn6 = types.InlineKeyboardButton('📖Правила', url='https://t.me/mafiarulesteach_bot')
    btn7 = types.InlineKeyboardButton('🗯Группа в VK', url='https://vk.com/studmafiaspb')
    btn8 = types.InlineKeyboardButton('🛠Техподдержка', url='https://t.me/acc_maf')
    btn9 = types.InlineKeyboardButton('💸Задонатить организаторам', callback_data='donut')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
    bot.send_message(message.chat.id, "📌Выберите опцию:", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callbacks(callback):
    if callback.data == 'menu': # Открыть меню
        menu(callback.message)
        return
    if callback.data == 'donut': # Выслать счет для доната
        donut1(callback.message)
        return
    if callback.data == 'schedule': # Расписание
        schedule(callback.message)
        return
    if callback.data == 'profile_show': # Просмотр профиля (из меню)
        profileshow(callback.message)
        return
    if callback.data == 'profile_change': # Изменение профиля (из просмотра)
        profilechange1(callback.message)
        return
    if callback.data == 'start_reg': # Начало регистрации в боте
        start_reg(callback.message)
        return
    if callback.data == 'tournaments_list':  # Посмотреть список турниров
        tournaments_list(callback.message, 0)
        return
    if callback.data == 'ad_tournaments_list':  # Посмотреть список турниров
        tournaments_list(callback.message, 1)
        return
    if callback.data == 'clubs_list': # Посмотреть список клубов
        clubs_list(callback.message)
        return
    if callback.data == 'userslist': # посмотреть список зареганных юзеров в боте
        userslist(callback.message, 1)
        return
    if callback.data == 'userchange': # изменить юзера бота
        datachange1(callback.message)
        return
    if callback.data == 'create_tourn': # создать турнир
        tournament_create1(callback.message)
        return
    if callback.data == 'spam': # для рассылки пользователям бота
        spam1(callback.message)
        return
    if callback.data == 'help': # Открыть меню
        us_help(callback.message)
        return
    if callback.data == 'ad_help': # Открыть меню
        ad_help(callback.message)
        return

    base_tourn = sqlite3.connect('tournaments_list')
    cur_tourn = base_tourn.cursor()
    cur_tourn.execute('SELECT identify FROM tournaments')
    data = cur_tourn.fetchall()
    cur_tourn.close()
    base_tourn.close()

    for i in data: # i[0] - идентификатор турнира
        if callback.data == i[0]: # Для просмотра инфы о турнире
            tournament_info(callback.message, i[0], 0)
            return
        if callback.data == i[0] + 'ad': # Для админ просмотра инфы о турнире
            tournament_info(callback.message, i[0], 1)
            return
        if callback.data == i[0] + 'tourn_reg': # для регистрации на турнир
            registering(callback.message, i[0])
            return
        if callback.data == i[0] + 'members': # для просмотра участников турнира
            mero_members(callback.message, i[0], 1)
            return
        if callback.data == i[0] + 'cancel_reg': # для отмены регистрации на турнир
            cancel_reg(callback.message, i[0])
            return
        if callback.data == i[0] + 'edit': # изменить турнир
            tournament_edit1(callback.message, i[0])
            return
        if callback.data == i[0] + 'delete': # удалить турнир
            tournament_delete(callback.message, i[0])
            return
        if callback.data == i[0] + 'send': # рассылка участникам турнира
            send1(callback.message, i[0])
            return
        if callback.data == i[0] + 'confirm': # для подтверждения участия в меро
            confirm(callback.message, i[0])
            return
        if callback.data == i[0] + 'profiles': # просмотр профилей участников турнира
            profiles_view(callback.message, i[0])
            return
        if callback.data == i[0] + 'requests': # просмотр заявок на турнир
            check_requests(callback.message, i[0])
            return
        if callback.data == i[0] + 'add_photo': # для добавления/изменения фото при заявке на турнир
            photo_comm_tourn_get(callback.message, i[0])
            return

    clubs = ['DarkTurn', 'LETI', 'Polytech', 'Mining', 'EveningParty', 'TechnoMafia', 'BONCHMAFIA', 'BlackInside']
    for i in clubs:
        base_clubs = sqlite3.connect('clubs')
        cur_clubs = base_clubs.cursor()
        cur_clubs.execute(f'SELECT identify, limits FROM {i}')
        data_ = cur_clubs.fetchall()
        cur_clubs.close()
        base_clubs.close()
        if callback.data == i + 'admin': # для админ-просмотра списка мероприятий клуба
            club_admin(callback.message, i)
            return
        if callback.data == i + 'create': # для админ-создания мероприятия клуба
            mero_create1(callback.message, i)
            return
        for j in data_: # j[0] - идентификатор мероприятия
            if callback.data == i + j[0] + 'reg': # для регистрации на мероприятие клуба
                registering(callback.message, j[0], club=i)
                return
            if callback.data == i + j[0] + 'members': # для просмотра участников мероприятия
                mero_members(callback.message, j[0], 1, club=i)
                return
            if callback.data == i + j[0] + 'cancel_reg': # для отмены регистрации на мероприятие
                cancel_reg(callback.message, j[0], club=i)
                return
            if callback.data == i + j[0] + 'info': # для просмотра инфы о мероприятии
                clubs_evening_info(callback.message, j[0], i, 0)
                return
            if callback.data == i + j[0] + 'admininfo': # для админ-просмотра инфы о мероприятии
                clubs_evening_info(callback.message, j[0], i, 1)
                return
            if callback.data == i + j[0] + 'edit': # для изменения инфы о мероприятии
                mero_edit1(callback.message, j[0], i)
                return
            if callback.data == i + j[0] + 'delete': # для удаления мероприятия
                mero_delete(callback.message, j[0], i)
                return
            if callback.data == i + j[0] + 'send': # для рассылки участникам мероприятия
                send1(callback.message, j[0], i)
                return
            if callback.data == i + j[0] + 'confirm': # для подтверждения участия в меро
                confirm(callback.message, j[0], i)
                return
            if callback.data == i + j[0] + 'profiles': # для просмотра профилей участников мероприятия
                profiles_view(callback.message, j[0], i)
                return
            if callback.data == i + j[0] + 'requests': # для просмотра заявок на мероприятия
                check_requests(callback.message, j[0], i)
                return

    for i in data:  # i[0] - идентификатор мероприятия
        base = sqlite3.connect('tournament')
        cur = base.cursor()
        try:
            cur.execute(f'SELECT id FROM {i[0]}')
        except:
            continue
        members = cur.fetchall()
        cur.close()
        base.close()
        for k in members:  # k[0] - айди участника подавшего заявку на меро
            if callback.data == k[0] + i[0] + 'accept':
                accept_request(callback.message, i[0], k[0])
                return
            if callback.data == k[0] + i[0] + 'decline':
                decline_request(callback.message, i[0], k[0])
                return

    for i in clubs:
        base_clubs = sqlite3.connect('clubs')
        cur_clubs = base_clubs.cursor()
        cur_clubs.execute(f'SELECT identify FROM {i}')
        data_ = cur_clubs.fetchall()
        cur_clubs.close()
        base_clubs.close()
        for j in data_:  # j[0] - идентификатор мероприятия
            base = sqlite3.connect('mero')
            cur = base.cursor()
            try:
                cur.execute(f'SELECT id FROM {i + j[0]}')
            except:
                continue
            members = cur.fetchall()
            cur.close()
            base.close()
            for k in members: # k[0] - айди участника подавшего заявку на меро
                if callback.data == k[0] + i + j[0] + 'accept':
                    accept_request(callback.message, j[0], k[0], i)
                    return
                if callback.data == k[0] + i + j[0] + 'decline':
                    decline_request(callback.message, j[0], k[0], i)
                    return


@bot.message_handler(content_types=['web_app_data'])
def web_app(message):
    data = loads(message.web_app_data.data)
    if message.web_app_data.button_text == '📝Зарегистрироваться':
        teamreg2(message, data)
        return
    if message.web_app_data.button_text == '✏Создать профиль':
        end_reg(message, data)
        return

    if "identify" in data:
        dicti = "abcdefghijklmnopqrstuvwxyz0123456789_-"
        if not all(char in dicti for char in data["identify"].lower()):
            bot.send_message(message.chat.id,
                             "❌Неверный идентификатор! Используйте только английские буквы, цифры, _ и -",
                             reply_markup=types.ReplyKeyboardRemove())
            return

    if message.web_app_data.button_text == '🎴Создать турнир':
        tournament_create2(message, data)
        return
    if message.web_app_data.button_text == '🎴Создать мероприятие':
        mero_create2(message, data)
        return
    else:
        bot.send_message(message.chat.id, '❌Произошла ошибка, попробуйте ещё раз вызвать команду (НЕ просто нажать на кнопку)')


def clubs_list(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('TechnoMafia')
    btn2 = types.KeyboardButton('Чёрный ход')
    btn3 = types.KeyboardButton('LETI-MAFIA')
    #btn4 = types.KeyboardButton('BONCHMAFIA')
    #btn5 = types.KeyboardButton('Polytech mafia community')
    btn6 = types.KeyboardButton('Mining Mafia')
    btn7 = types.KeyboardButton('Вечерняя партия')
    btn8 = types.KeyboardButton('Black Inside')
    markup.row(btn1, btn2, btn3)
    markup.row(btn6, btn7, btn8)
    bot.send_message(message.chat.id, "🕹Выберите клуб: ", reply_markup=markup)
    bot.register_next_step_handler(message, club_evening)


def club_evening(message):
    bot.send_message(message.chat.id, '.', reply_markup=types.ReplyKeyboardRemove())  # сообщение для удаления плиток
    try:
        bot.delete_message(message.chat.id, message.message_id+1)
    except Exception as e:
        print(e)
    if message.text == 'Чёрный ход':
        club = 'DarkTurn'
    elif message.text == 'LETI-MAFIA':
        club = 'LETI'
    elif message.text == 'Polytech mafia community':
        club = 'Polytech'
    elif message.text == 'Mining Mafia':
        club = 'Mining'
    elif message.text == 'Вечерняя партия':
        club = 'EveningParty'
    elif message.text == 'TechnoMafia':
        club = 'TechnoMafia'
    elif message.text == 'BONCHMAFIA':
        club = 'BONCHMAFIA'
    elif message.text == 'Black Inside':
        club = 'BlackInside'
    else:
        bot.send_message(message.chat.id, '❌Клуб не найден!')
        menu(message)
        return

    base = sqlite3.connect('clubs')
    cur = base.cursor()

    cur.execute(f'SELECT * FROM {club}')
    data = cur.fetchall()

    cur.close()
    base.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
    for i in data:
        if int(i[6]) != 0: # если статус = 1, то есть его могут увидеть участники
            markup.add(types.InlineKeyboardButton(i[2], callback_data=club + i[1] + 'info'))
    bot.send_message(message.chat.id, '🎫Выберите мероприятие: ', reply_markup=markup)


def clubs_evening_info(message, identify, club, typ):  # typ = 1 - команда вызвана админом, = 0 - обычным пользователем
    base_mero = sqlite3.connect('mero')
    cur_mero = base_mero.cursor()

    try:
        cur_mero.execute(f'SELECT * FROM {club+identify}')
        players = cur_mero.fetchall()
    except:
        players = []

    cur_mero.close()
    base_mero.close()

    base = sqlite3.connect('clubs')
    cur = base.cursor()
    cur.execute(f'SELECT * FROM {club} WHERE identify = ?', (identify,))
    data = cur.fetchall()
    cur.close()
    base.close()

    for i in data:
        status = i[6]

    cnt = 0  # счётчик игроков в турнире
    if players:
        if status == 2:
            for i in players:
                if i[6] == 1:
                    cnt += 1
        else:
            for i in players:
                cnt += 1

    markup = types.InlineKeyboardMarkup()
    for i in data:
        output = info(i[2], i[3], i[4], i[5], i[6], members=cnt, cost=i[7])
        if typ:
            if i[6] == 2:
                markup.add(types.InlineKeyboardButton('📜Посмотреть заявки', callback_data=club + i[1] + 'requests'))
            markup.add(types.InlineKeyboardButton('📝Изменить', callback_data=club + i[1] + 'edit'))
            markup.add(types.InlineKeyboardButton('👀Удалить', callback_data=club + i[1] + 'delete'))
            markup.add(types.InlineKeyboardButton('💌Рассылка', callback_data=club + i[1] + 'send'))
            markup.add(types.InlineKeyboardButton('🖼Посмотреть профили', callback_data=club + i[1] + 'profiles'))
            markup.add(types.InlineKeyboardButton('🙍‍♂️Посмотреть участников', callback_data=club + i[1] + 'members'))
        else:
            markup.add(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
            if i[6] == 1:
                markup.add(types.InlineKeyboardButton('📝Регистрация', callback_data=club + i[1] + 'reg'))
            else:
                markup.add(types.InlineKeyboardButton('📝Отправить заявку', callback_data=club + i[1] + 'reg'))
            markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=club + i[1] + 'members'))
        try:
            save_path = f'photos\\{club}\\{identify}.png'
            with open(save_path, 'rb') as file:
                bot.send_photo(message.chat.id, file, caption=output, reply_markup=markup)  # Вывод описания меро с фото
        except:
            bot.send_message(message.chat.id, output, reply_markup=markup)  # Вывод описания меро
        break


def profileshow(message):
    base = sqlite3.connect('users')
    cur = base.cursor()

    cur.execute('SELECT * FROM users')
    data = cur.fetchall()

    cur.close()
    base.close()

    for i in data:
        if i[1] == str(message.chat.id):
            save_path = f'pp\\{message.chat.id}.png'
            try:
                with open(save_path, 'rb') as file:
                    bot.send_photo(i[1], file)
            except:
                pass
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
            markup.add(types.InlineKeyboardButton('📝Изменить профиль', callback_data='profile_change'))
            bot.send_message(message.chat.id, '🙍‍♂️Ваш профиль:\n\nНик: ' + i[2] + '\nКлуб: ' + i[3], reply_markup=markup)
            break
    else:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton('📝Зарегистрироваться в боте', callback_data='start_reg'))
        bot.send_message(message.chat.id, f"❌Ошибка: вы не зарегистрированы в боте!", reply_markup=markup)


def profilechange1(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('📝Изменить профиль', web_app=types.WebAppInfo(
        url='https://acc-maf.github.io/StudLeagueBot/profile_edit.html')))
    markup.add(types.KeyboardButton('🖼Изменить картику'))
    bot.send_message(message.chat.id, '🗜Выберите кнопку:', reply_markup=markup)
    bot.register_next_step_handler(message, profilechange2)


def profilechange2(message):
    if message.text == '🖼Изменить картику':
        bot.send_message(message.chat.id, "📷Отправьте фотографию")
        bot.register_next_step_handler(message, profilechange3)
        return
    if message.text:
        bot.send_message(message.chat.id, "❌Не пон", reply_markup=types.ReplyKeyboardRemove())
        return
    data = loads(message.web_app_data.data)
    base = sqlite3.connect('users')
    cur = base.cursor()
    if "nick" in data:
        cur.execute('UPDATE users SET nick = ? WHERE id = ?', (data["nick"], message.chat.id))
    if "club" in data:
        cur.execute('UPDATE users SET club = ? WHERE id = ?', (data["club"], message.chat.id))
    base.commit()
    cur.close()
    base.close()

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
    menu(message)


def profilechange3(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌Вы отправили не фото!")
        menu(message)
        return
    image = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
    save_path = f'pp\\{message.chat.id}.png'
    with open(save_path, 'wb+') as file:
        file.write(image)

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
    menu(message)


def photo_comm_tourn_get(message, identify):
    save_path = f"photos\\{identify}\\{message.chat.id}.png"
    try:
        with open(save_path, 'rb') as file:
            bot.send_photo(message.chat.id, file)
    except:
        pass
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("Отмена"))
    bot.send_message(message.chat.id, "📷Отправьте фотографию вашей команды", reply_markup=markup)
    bot.register_next_step_handler(message, photo_comm_tourn, identify)


def photo_comm_tourn(message, identify):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, "Отменено", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        return
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌Вы отправили не фото!")
        mero_members(message, identify, 0, club=None)
        return
    image = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
    if not os.path.isdir(f"photos\\{identify}"):
        os.mkdir(f"photos\\{identify}")
    save_path = f"photos\\{identify}\\{message.chat.id}.png"
    with open(save_path, 'wb+') as file:
        file.write(image)

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
    tournament_info(message, identify, 0)


@bot.pre_checkout_query_handler(func=lambda callback: True)
def pre_checkout_query(pre_check):
    bot.answer_pre_checkout_query(pre_check.id, True)


@bot.message_handler(content_types=['successful_payment'])
def success(message):
    payload = message.successful_payment.invoice_payload
    if payload == 'donut':
        bot.send_message(message.chat.id, "❤Большое спасибо за поддержку студлиги!!!", message_effect_id='5044134455711629726')
        bot.send_message(-4691783391, f"{message.from_user.first_name} {message.from_user.last_name} поддержал нас на {int(message.successful_payment.total_amount/100)} рублей!!")
        return
    base_tourn = sqlite3.connect('tournaments_list')
    cur_tourn = base_tourn.cursor()

    base_clubs = sqlite3.connect('clubs')
    cur_clubs = base_clubs.cursor()

    cur_tourn.execute('SELECT identify FROM tournaments')
    data = cur_tourn.fetchall()


    for i in data:  # i[0] - идентификатор турнира
        if payload == i[0]:
            base_mero = sqlite3.connect('tournament')
            cur_mero = base_mero.cursor()
            cur_mero.execute(f'UPDATE {i[0]} SET paid = ? WHERE id = ?', (1, message.chat.id))
            base_mero.commit()
            cur_clubs.close()
            base_clubs.close()
            cur_tourn.close()
            base_tourn.close()
            cur_mero.close()
            base_mero.close()
            bot.send_message(message.chat.id, "💸Взнос успешно оплачен", message_effect_id='5104841245755180586')
            return

    clubs = ['DarkTurn', 'LETI', 'Polytech', 'Mining', 'EveningParty', 'TechnoMafia', 'BONCHMAFIA', 'BlackInside']
    for i in clubs:
        cur_clubs.execute(f'SELECT identify FROM {i}')
        data = cur_clubs.fetchall()
        for j in data:  # j[0] - идентификатор мероприятия
            if payload == i + j[0]:
                base_mero = sqlite3.connect('mero')
                cur_mero = base_mero.cursor()
                cur_mero.execute(f'UPDATE {i + j[0]} SET paid = ? WHERE id = ?', (1, message.chat.id))
                base_mero.commit()
                cur_clubs.close()
                base_clubs.close()
                cur_tourn.close()
                base_tourn.close()
                cur_mero.close()
                base_mero.close()
                bot.send_message(message.chat.id, "💸Взнос успешно оплачен", message_effect_id='5104841245755180586')
                return


@bot.message_handler(commands=['admin'])
def admin(message):
    global admins, letiadmins, bonchadmins, miningadmins, technoadmins, darkturnadmins, eveningadmins, polytechadmins, blackinsideadmins
    markup = types.InlineKeyboardMarkup(row_width=4)
    for i in admins:
        if str(message.chat.id) == i:
            markup.add(types.InlineKeyboardButton('🏆Турнир', callback_data='ad_tournaments_list'))
            markup.add(types.InlineKeyboardButton('🙍‍♂️Пользователи бота', callback_data='userslist'))
            markup.add(types.InlineKeyboardButton('💌Рассылка', callback_data='spam'))
            markup.add(types.InlineKeyboardButton('TechnoMafia', callback_data='TechnoMafia' + 'admin'))
            markup.add(types.InlineKeyboardButton('Чёрный ход', callback_data='DarkTurn' + 'admin'))
            markup.add(types.InlineKeyboardButton('LETI-MAFIA', callback_data='LETI' + 'admin'))
            markup.add(types.InlineKeyboardButton('BONCHMAFIA', callback_data='BONCHMAFIA' + 'admin'))
            markup.add(types.InlineKeyboardButton('Polytech mafia community', callback_data='Polytech' + 'admin'))
            markup.add(types.InlineKeyboardButton('Mining Mafia', callback_data='Mining' + 'admin'))
            markup.add(types.InlineKeyboardButton('Вечерняя партия', callback_data='EveningParty' + 'admin'))
            markup.add(types.InlineKeyboardButton('Black Inside', callback_data='BlackInside' + 'admin'))
            break
    else:
        for i in technoadmins:
            if str(message.chat.id) == i:
                markup.add(types.InlineKeyboardButton('TechnoMafia', callback_data='TechnoMafia' + 'admin'))
                break
        else:
            for i in darkturnadmins:
                if str(message.chat.id) == i:
                    markup.add(types.InlineKeyboardButton('Чёрный ход', callback_data='DarkTurn' + 'admin'))
                    break
            else:
                for i in letiadmins:
                    if str(message.chat.id) == i:
                        markup.add(types.InlineKeyboardButton('LETI-MAFIA', callback_data='LETI' + 'admin'))
                        break
                else:
                    for i in bonchadmins:
                        if str(message.chat.id) == i:
                            markup.add(types.InlineKeyboardButton('BONCHMAFIA', callback_data='BONCHMAFIA' + 'admin'))
                            break
                    else:
                        for i in polytechadmins:
                            if str(message.chat.id) == i:
                                markup.add(types.InlineKeyboardButton('Polytech mafia community', callback_data='Polytech' + 'admin'))
                                break
                        else:
                            for i in miningadmins:
                                if str(message.chat.id) == i:
                                    markup.add(types.InlineKeyboardButton('Mining Mafia', callback_data='Mining' + 'admin'))
                                    break
                            else:
                                for i in eveningadmins:
                                    if str(message.chat.id) == i:
                                        markup.add(types.InlineKeyboardButton('Вечерняя партия', callback_data='EveningParty' + 'admin'))
                                        break
                                else:
                                    for i in blackinsideadmins:
                                        if str(message.chat.id) == i:
                                            markup.add(types.InlineKeyboardButton('Black Inside', callback_data='BlackInside' + 'admin'))
                                            break
                                    else:
                                        bot.send_message(message.chat.id, f"❌Ты не админ.")
                                        return

    markup.add(types.InlineKeyboardButton('🔓Админ-гайд по боту', callback_data='ad_help'))
    bot.send_message(message.chat.id, '🔐Вы админ:', reply_markup=markup)


def club_admin(message, club):
    base = sqlite3.connect('clubs')
    cur = base.cursor()

    cur.execute(f'SELECT name, identify FROM {club}')
    data = cur.fetchall()

    cur.close()
    base.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🎴Создать мероприятие', callback_data=club + 'create'))
    for i in data:
        markup.add(types.InlineKeyboardButton(i[0], callback_data=club + i[1] + 'admininfo'))
    bot.send_message(message.chat.id, '🎟Выберите мероприятие: ', reply_markup=markup)


def userslist(message, typ):
    base = sqlite3.connect('users')
    cur = base.cursor()

    cur.execute('SELECT * FROM users')
    players = cur.fetchall()

    players_output = ''
    for i in players:
        players_output += f'№{i[0]}. {i[1]} - @{bot.get_chat(i[1]).username} - {i[2]} - {i[3]}\n'

    markup = types.InlineKeyboardMarkup()
    if typ:
        markup.add(types.InlineKeyboardButton('📝Изменить', callback_data='userchange'))

    bot.send_message(message.chat.id, players_output, reply_markup=markup)

    cur.close()
    base.close()


def datachange1(message):
    bot.send_message(message.chat.id, f"📑Введите номер пользователя, данные которого хотите изменить")
    bot.register_next_step_handler(message, datachange2)


def datachange2(message):
    base = sqlite3.connect('users')
    cur = base.cursor()

    cur.execute('SELECT * FROM users')
    players = cur.fetchall()

    cur.close()
    base.close()

    until = 0
    try:
        until = int(message.text)
    except:
        bot.send_message(message.chat.id, "❌Введите только число!")
        bot.register_next_step_handler(message, datachange1)

    cnt = 0
    for i in players:
        cnt += 1
        if cnt == until:
            markup = types.ReplyKeyboardMarkup()
            markup.add(types.KeyboardButton('✒Ник'), types.KeyboardButton('🎩Клуб'))
            bot.send_message(message.chat.id, "Что вы хотите изменить?", reply_markup=markup)
            bot.register_next_step_handler(message, datachange3, i)
            break
    else:
        bot.send_message(message.chat.id, "❌Пользователь с таким номером не зарегистрирован")
        return


def datachange3(message, i):
    if message.text == '✒Ник':
        bot.send_message(message.chat.id, "🖋Введите новый ник", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, datachange4, i)
    elif message.text == '🎩Клуб':
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('TechnoMafia')
        btn2 = types.KeyboardButton('Чёрный ход')
        btn3 = types.KeyboardButton('LETI-MAFIA')
        btn4 = types.KeyboardButton('BONCHMAFIA')
        btn5 = types.KeyboardButton('Polytech mafia community')
        btn6 = types.KeyboardButton('Mining Mafia')
        btn7 = types.KeyboardButton('Вечерняя партия')
        btn8 = types.KeyboardButton('Polemica SPb')
        btn9 = types.KeyboardButton('Иллюzия ОбмаNа')
        btn10 = types.KeyboardButton('TITAN SPb')
        markup.row(btn1, btn2, btn3, btn4)
        markup.row(btn5, btn6, btn7)
        markup.row(btn8, btn9, btn10)
        bot.send_message(message.chat.id, "🎓Введите новый клуб", reply_markup=markup)
        bot.register_next_step_handler(message, datachange5, i)
    else:
        bot.send_message(message.chat.id, '.', reply_markup=types.ReplyKeyboardRemove())  # сообщение для удаления плиток
        bot.delete_message(message.chat.id, message.message_id + 1)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
        bot.send_message(message.chat.id, "❌Не понял, воспользуйтесь кнопками!", reply_markup=markup)


def datachange4(message, i):
    base = sqlite3.connect('users')
    cur = base.cursor()

    cur.execute('UPDATE users SET nick = ? WHERE num = ?', (message.text, i[0]))
    base.commit()
    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
    cur.close()
    base.close()

    userslist(message, 1)


def datachange5(message, i):
    base = sqlite3.connect('users')
    cur = base.cursor()

    cur.execute('UPDATE users SET club = ? WHERE num = ?', (message.text, i[0]))
    base.commit()
    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
    cur.close()
    base.close()

    userslist(message, 1)


def profiles_view(message, identify, club=None):
    if club:
        base = sqlite3.connect('mero')
        cur = base.cursor()
        try:
            cur.execute(f'SELECT * FROM {club + identify}')
        except:
            bot.send_message(message.chat.id, "❌Участников нет!")
            cur.close()
            base.close()
            return
        typ = 'solo'
    else:
        base = sqlite3.connect('tournament')
        cur = base.cursor()
        try:
            cur.execute(f'SELECT * FROM {identify}')
        except:
            bot.send_message(message.chat.id, "❌Участников нет!")
            cur.close()
            base.close()
            return
        base_tourn = sqlite3.connect('tournaments_list')
        cur_tourn = base_tourn.cursor()
        cur_tourn.execute(f'SELECT type FROM tournaments WHERE identify = ?', (identify,))
        type_base = cur_tourn.fetchall()
        cur_tourn.close()
        base_tourn.close()
        typ = ''
        for i in type_base:
            typ = i[0]
            break

    players = cur.fetchall()
    cur.close()
    base.close()

    if typ != 'team':
        for i in players:
            try:
                save_path = f'pp\\{i[1]}.png'  # f'pp/{i[1]}.png'
                with open(save_path, 'rb') as file:
                    bot.send_photo(message.chat.id, file)
            except:
                pass
            bot.send_message(message.chat.id, 'Ник: ' + i[2] + '\nКлуб: ' + i[3])
    else:
        for i in players:
            try:
                save_path = f'photos\\{identify}\\{i[1]}.png'  # f'pp/{identify}/{i[1]}.png'
                with open(save_path, 'rb') as file:
                    bot.send_photo(message.chat.id, file, caption='Название команды: ' + i[2] + '\nСостав: ' + i[3])
            except:
                bot.send_message(message.chat.id, 'Название команды: ' + i[2] + '\nСостав: ' + i[3])


def tournament_create1(message):
    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()
    cur.execute('SELECT identify FROM tournaments')
    data = cur.fetchall()
    cur.close()
    base.close()

    cnt = 0
    output = ''
    bot.send_message(message.chat.id, '‼При создании понадобится ввести идентификатор мероприятия. Он должен содержать только английские буквы, цифры, -_, без пробелов. Необходимо, чтобы он был уникальным и соответствовал названию турнира.\nПримеры: my_first_tourn1, StudLeague3\n\nЗанятые индетефикаторы:.')
    for i in data:
        cnt += 1
        output += str(cnt) + '. ' + i[0] + '\n'
    if output != '':
        bot.send_message(message.chat.id, output)
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('🎴Создать турнир', web_app=types.WebAppInfo(
        url='https://acc-maf.github.io/StudLeagueBot/tournament_create.html')))
    bot.send_message(message.chat.id, '🗜Нажмите на кнопку для создания турнира', reply_markup=markup)


def tournament_create2(message, data):
    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()

    cur.execute('SELECT identify FROM tournaments')
    ids = cur.fetchall()
    for i in ids:
        if data["identify"] == i[0]:
            bot.send_message(message.chat.id, '❌Такой идентификатор уже занят!', reply_markup=types.ReplyKeyboardRemove())
            cur.close()
            base.close()
            return

    try:
        cur.execute(
            f'INSERT INTO tournaments (identify, name, desc, date, rules, score, type, limits, status, cost, distance) VALUES ("{data["identify"]}", "{data["name"]}", "{data["desc"]}", "{data["date"]}", "{data["rules"]}", "{data["score"]}", "{data["typ"]}", "{int(data["limit"])}", 0, "{int(data["cost"])}", "{data["distance"]}")')
    except:
        cur.close()
        base.close()
        bot.send_message(message.chat.id, "❌Произошла ошибка (скорее всего, вы не заполнили какое-то поле)", reply_markup=types.ReplyKeyboardRemove())
        return
    base.commit()
    cur.close()
    base.close()

    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("❌Пропустить"))
    bot.send_message(message.chat.id, "🎉Успешный успех\n\n📷Отправьте фотографию, которая будет прикреплена к информации",
                     reply_markup=markup)
    bot.register_next_step_handler(message, tournament_create3, data["identify"])


def tournament_create3(message, identify):
    if message.text == '❌Пропустить':
        bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        tournament_info(message, identify, 1)
        return
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌Не пон", reply_markup=types.ReplyKeyboardRemove())
        tournament_info(message, identify, 1)
        return
    image = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
    save_path = f"photos\\announcements\\{identify}.png"
    with open(save_path, 'wb+') as file:
        file.write(image)

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(),
                     message_effect_id='5107584321108051014')
    tournament_info(message, identify, 1)


def mero_create1(message, club):
    global current_club
    current_club = club
    base = sqlite3.connect('clubs')
    cur = base.cursor()
    cur.execute(f'SELECT identify FROM {club}')
    data = cur.fetchall()
    cur.close()
    base.close()
    cnt = 0
    output = ''
    bot.send_message(message.chat.id, '‼При создании понадобится ввести идентификатор мероприятия. Он должен содержать только английские буквы, цифры, -_, без пробелов. Необходимо, чтобы он был уникальным и соответствовал названию турнира.\nПримеры: techno_evening1, bonchevening8\n\nЗанятые индетефикаторы:.')
    for i in data:
        cnt += 1
        output += str(cnt) + '. ' + i[0] + '\n'
    if output != '':
        bot.send_message(message.chat.id, output)
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('🎴Создать мероприятие', web_app=types.WebAppInfo(
        url='https://acc-maf.github.io/StudLeagueBot/mero_create.html')))
    bot.send_message(message.chat.id, '🗜Нажмите на кнопку для создания мероприятия', reply_markup=markup)


def mero_create2(message, data):
    global current_club
    base = sqlite3.connect('clubs')
    cur = base.cursor()

    try:
        cur.execute(f'SELECT identify FROM {current_club}')
    except:
        cur.close()
        base.close()
        bot.send_message(message.chat.id, "❌Произошла ошибка на стороне бота, попробуйте снова", reply_markup=types.ReplyKeyboardRemove())
        admin(message)
        return

    ids = cur.fetchall()
    for i in ids:
        if data["identify"] == i[0]:
            bot.send_message(message.chat.id, '❌Такой идентификатор уже занят!',
                             reply_markup=types.ReplyKeyboardRemove())
            cur.close()
            base.close()
            return

    if data['proh']:
        desc = data['desc'] + '\n\n' + data["proh"]
    else:
        desc = data['desc']
    data['date'] = datetime.datetime.strptime(data['date'].split('T')[0], "%Y-%m-%d").strftime("%d/%m/%Y") + ' ' + data['date'].split('T')[1]
    cur.execute(
        f'INSERT INTO {current_club} (identify, name, desc, date, limits, status, cost) VALUES ("{data["identify"]}", "{data["name"]}", "{desc}", "{data["date"]}", "{int(data["limit"])}", 0, "{int(data["cost"])}")')
    base.commit()
    cur.close()
    base.close()

    bot.send_message(message.chat.id, "🎉Успешный успех", message_effect_id='5107584321108051014',
                     reply_markup=types.ReplyKeyboardRemove())
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("❌Пропустить"))
    bot.send_message(message.chat.id,
                     "🎉Успешный успех\n\n📷Отправьте фотографию, которая будет прикреплена к информации", reply_markup=markup)
    bot.register_next_step_handler(message, mero_create3, data["identify"], current_club)


def mero_create3(message, identify, club):
    if message.text == '❌Пропустить':
        bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        clubs_evening_info(message, identify, club, 1)
        return
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌Не пон", reply_markup=types.ReplyKeyboardRemove())
        clubs_evening_info(message, identify, club, 1)
        return
    image = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
    save_path = f"photos\\{club}\\{identify}.png"
    with open(save_path, 'wb+') as file:
        file.write(image)

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(),
                     message_effect_id='5107584321108051014')
    clubs_evening_info(message, identify, club, 1)


def tournament_edit1(message, identify):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('🖍Редактировать турнир', web_app=types.WebAppInfo(
        url='https://acc-maf.github.io/StudLeagueBot/tournament_edit.html')))
    markup.add(types.KeyboardButton('➕Добавить участников'))
    markup.add(types.KeyboardButton('➖Удалить участников'))
    markup.add(types.KeyboardButton('🖼Изменить картинку'))
    bot.send_message(message.chat.id, '🗜Выберите кнопку', reply_markup=markup)
    bot.register_next_step_handler(message, tournament_edit2, identify)


def tournament_edit2(message, identify):
    if message.text == '➕Добавить участников':
        edit3(message, identify)
        return
    if message.text == '➖Удалить участников':
        edit4(message, identify)
        return
    if message.text == '🖼Изменить картинку':
        edit5(message, identify)
        return
    if message.text:
        bot.send_message(message.chat.id, "❌Не пон", reply_markup=types.ReplyKeyboardRemove())
        return
    data = loads(message.web_app_data.data)
    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()
    if "name" in data:
        cur.execute('UPDATE tournaments SET name = ? WHERE identify = ?', (data["name"], identify))
    if "desc" in data:
        cur.execute('UPDATE tournaments SET desc = ? WHERE identify = ?', (data["desc"], identify))
    if "distance" in data:
        cur.execute('UPDATE tournaments SET distance = ? WHERE identify = ?', (data["distance"], identify))
    if "date" in data:
        cur.execute('UPDATE tournaments SET date = ? WHERE identify = ?', (data["date"], identify))
    if "rules" in data:
        cur.execute('UPDATE tournaments SET rules = ? WHERE identify = ?', (data["rules"], identify))
    if "score" in data:
        cur.execute('UPDATE tournaments SET score = ? WHERE identify = ?', (data["score"], identify))
    if "limit" in data:
        cur.execute('UPDATE tournaments SET limits = ? WHERE identify = ?', (data["limit"], identify))
    if "cost" in data:
        cur.execute('UPDATE tournaments SET cost = ? WHERE identify = ?', (data["cost"], identify))
    if "status" in data:
        cur.execute('UPDATE tournaments SET status = ? WHERE identify = ?', (data["status"], identify))
    base.commit()
    cur.close()
    base.close()

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')


def mero_edit1(message, identify, club):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('🖍Редактировать мероприятие', web_app=types.WebAppInfo(
        url='https://acc-maf.github.io/StudLeagueBot/mero_edit.html')))
    markup.add(types.KeyboardButton('➕Добавить участников'))
    markup.add(types.KeyboardButton('➖Удалить участников'))
    markup.add(types.KeyboardButton('🖼Изменить картинку'))
    bot.send_message(message.chat.id, '🗜Выберите кнопку', reply_markup=markup)
    bot.register_next_step_handler(message, mero_edit2, identify, club)


def mero_edit2(message, identify, club):
    if message.text == '➕Добавить участников':
        edit3(message, identify, club)
        return
    if message.text == '➖Удалить участников':
        edit4(message, identify, club)
        return
    if message.text == '🖼Изменить картинку':
        edit5(message, identify, club)
        return
    if message.text:
        bot.send_message(message.chat.id, "❌Не пон", reply_markup=types.ReplyKeyboardRemove())
        return
    data = loads(message.web_app_data.data)
    base = sqlite3.connect('clubs')
    cur = base.cursor()
    if "name" in data:
        cur.execute(f'UPDATE {club} SET name = ? WHERE identify = ?', (data["name"], identify))
    if "desc" in data:
        cur.execute(f'UPDATE {club} SET desc = ? WHERE identify = ?', (data["desc"], identify))
    if "date" in data:
        data['date'] = datetime.datetime.strptime(data['date'].split('T')[0], "%Y-%m-%d").strftime("%d/%m/%Y") + ' ' + data['date'].split('T')[1]
        cur.execute(f'UPDATE {club} SET date = ? WHERE identify = ?', (data["date"], identify))
    if "limit" in data:
        cur.execute(f'UPDATE {club} SET limits = ? WHERE identify = ?', (data["limit"], identify))
    if "cost" in data:
        cur.execute(f'UPDATE {club} SET cost = ? WHERE identify = ?', (data["cost"], identify))
    if "status" in data:
        cur.execute(f'UPDATE {club} SET status = ? WHERE identify = ?', (data["status"], identify))

    base.commit()
    cur.close()
    base.close()

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
    clubs_evening_info(message, identify, club, 1)


def edit3(message, identify, club=None):
    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()
    cur.execute(f'SELECT type FROM tournaments WHERE identify = ?', (identify,))
    typ_base = cur.fetchall()
    cur.close()
    base.close()
    typ = ''
    for i in typ_base:
        typ = i[0]
    if typ == 'solo':
        mero_members(message, identify, 0, club=club)
        bot.send_message(message.chat.id, "^^^ Участники ^^^", reply_markup=types.ReplyKeyboardRemove())

        userslist(message, 0)
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton('Другой участник'))
        markup.add(types.KeyboardButton('Отмена'))
        bot.send_message(message.chat.id, "Введите номер участника, если он есть в списке ^^^ или выберите кнопку", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton('Отмена'))
        mero_members(message, identify, 0, club=club)
        bot.send_message(message.chat.id, "Введите название команды", reply_markup=markup)

    bot.register_next_step_handler(message, edit3_1, identify, typ, club)


def edit3_(message, identify, typ, club=None):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Другой участник'))
    markup.add(types.KeyboardButton('Отмена'))
    bot.send_message(message.chat.id, "Введите номер участника или выберите кнопку", reply_markup=markup)
    bot.register_next_step_handler(message, edit3_1, identify, typ, club)


def edit3_1(message, identify, typ, club=None):
    if message.text.strip() == 'Отмена':
        bot.send_message(message.chat.id, "Отменено", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        if club:
            clubs_evening_info(message, identify, club, 1)
        else:
            tournament_info(message, identify, 1)
        return

    if typ != 'team':
        try:
            int(message.text.strip())
        except:
            if message.text.strip() == 'Другой участник':
                bot.send_message(message.chat.id, "Введите его ник", reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(message, edit3_2, identify, club)
            else:
                bot.send_message(message.chat.id, "❌Вы ввели не целое число!", reply_markup=types.ReplyKeyboardRemove())
                return
        else:
            base_us = sqlite3.connect('users')
            cur_us = base_us.cursor()
            cur_us.execute('SELECT * FROM users WHERE num = ?', (int(message.text.strip()),))
            users = cur_us.fetchall()
            cur_us.close()
            base_us.close()
            nick = ''
            club_user = ''
            us_id = ''
            for i in users:
                us_id = i[1]
                nick = i[2]
                club_user = i[3]
                break

            if club:
                base_memb = sqlite3.connect('mero')
                cur_memb = base_memb.cursor()
                cur_memb.execute(
                    f'CREATE TABLE IF NOT EXISTS {club + identify} (num INTEGER PRIMARY KEY, id TEXT NOT NULL, nick TEXT NOT NULL, club TEXT NOT NULL, paid INTEGER, confirm INTEGER, request INTEGER)')
                base_memb.commit()
                cur_memb.execute(
                    f'INSERT INTO {club + identify} (id, nick, club) VALUES ("{us_id}", "{nick}", "{club_user}")')
                base_memb.commit()
            else:
                base_memb = sqlite3.connect('tournament')
                cur_memb = base_memb.cursor()
                cur_memb.execute(
                    f'CREATE TABLE IF NOT EXISTS {identify} (num INTEGER PRIMARY KEY, id TEXT NOT NULL, nick TEXT NOT NULL, club TEXT NOT NULL, paid INTEGER, confirm INTEGER, request INTEGER)')
                base_memb.commit()
                cur_memb.execute(
                    f'INSERT INTO {identify} (id, nick, club) VALUES ("{us_id}", "{nick}", "{club_user}")')
                base_memb.commit()
            bot.send_message(message.chat.id, "🎉Успешно", message_effect_id='5107584321108051014')
            cur_memb.close()
            base_memb.close()

            edit3_(message, identify, club)
    else:
        bot.send_message(message.chat.id, "Введите ники участников команды", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, edit3_3, identify, message.text, club)


def edit3_2(message, identify, club=None): # В message.text содержится ник
    bot.send_message(message.chat.id, "Введите клуб участника")
    bot.register_next_step_handler(message, edit3_3, identify, message.text, club=club)


def edit3_3(message, identify, nick, club=None):
    if club:
        base_memb = sqlite3.connect('mero')
        cur_memb = base_memb.cursor()
        cur_memb.execute(
            f'CREATE TABLE IF NOT EXISTS {club + identify} (num INTEGER PRIMARY KEY, id TEXT NOT NULL, nick TEXT NOT NULL, club TEXT NOT NULL, paid INTEGER, confirm INTEGER, request INTEGER)')
        base_memb.commit()
        cur_memb.execute(
            f'INSERT INTO {club + identify} (id, nick, club, request) VALUES ("None", "{nick}", "{message.text}", 0)')
    else:
        base_memb = sqlite3.connect('tournament')
        cur_memb = base_memb.cursor()
        cur_memb.execute(f'CREATE TABLE IF NOT EXISTS {identify} (num INTEGER PRIMARY KEY, id TEXT NOT NULL, nick TEXT NOT NULL, club TEXT NOT NULL, paid INTEGER, confirm INTEGER, request INTEGER)')
        base_memb.commit()
        cur_memb.execute(
            f'INSERT INTO {identify} (id, nick, club, request) VALUES ("None", "{nick}", "{message.text}", 0)')
    base_memb.commit()
    bot.send_message(message.chat.id, "🎉Успешно", message_effect_id='5107584321108051014')
    cur_memb.close()
    base_memb.close()

    edit3_(message, identify, club)


def edit4(message, identify, club=None):
    mero_members(message, identify, 0, club=club)
    bot.send_message(message.chat.id, "^^^ Участники ^^^", reply_markup=types.ReplyKeyboardRemove())

    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Отмена'))
    bot.send_message(message.chat.id, "Введите номер участника (только целое число)", reply_markup=markup)
    bot.register_next_step_handler(message, edit4_1, identify, club)


def edit4_1(message, identify, club=None):
    if message.text.strip() == 'Отмена':
        bot.send_message(message.chat.id, "Отменено", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        if club:
            clubs_evening_info(message, identify, club, 1)
        else:
            tournament_info(message, identify, 1)
        return

    try:
        int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "Вы ввели не целое число!")
        edit4(message, identify, club)
        return
    if club:
        base_memb = sqlite3.connect('mero')
        cur_memb = base_memb.cursor()
        cur_memb.execute(f'DELETE FROM {club + identify} WHERE num = ?', (int(message.text.strip()),))
        base_memb.commit()
    else:
        base_memb = sqlite3.connect('tournament')
        cur_memb = base_memb.cursor()
        cur_memb.execute(f'DELETE FROM {identify} WHERE num = ?', (int(message.text.strip()),))
        base_memb.commit()
    bot.send_message(message.chat.id, "🎉Успешно", message_effect_id='5107584321108051014')
    cur_memb.close()
    base_memb.close()

    edit4(message, identify, club)


def edit5(message, identify, club=None):
    bot.send_message(message.chat.id, "📷Отправьте фотографию, которая будет прикреплена к информации")
    bot.register_next_step_handler(message, edit5_1,identify, club)


def edit5_1(message, identify, club):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌Не пон", reply_markup=types.ReplyKeyboardRemove())
        return
    image = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
    if club:
        save_path = f"photos\\{club}\\{identify}.png"
    else:
        save_path = f"photos\\announcements\\{identify}.png"
    with open(save_path, 'wb+') as file:
        file.write(image)

    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(),
                     message_effect_id='5107584321108051014')


def tournament_delete(message, identify):
    base_list = sqlite3.connect('tournaments_list')
    cur_list = base_list.cursor()

    base_tour = sqlite3.connect('tournament')
    cur_tour = base_tour.cursor()

    try:
        cur_list.execute('DELETE FROM tournaments WHERE identify = ?', (identify,))
        base_list.commit()
        bot.send_message(message.chat.id, "🎉Успешно", message_effect_id='5107584321108051014')
    except Exception as e:
        bot.send_message(message.chat.id, "❌Ошибка, скорее всего, неверный идентификатор")
        print(e)
    try:
        cur_tour.execute(f'DROP TABLE {identify}')
        base_tour.commit()
    except Exception as e:
        print(e)

    cur_list.close()
    base_list.close()
    cur_tour.close()
    base_tour.close()


def mero_delete(message, identify, club):
    base_list = sqlite3.connect('clubs')
    cur_list = base_list.cursor()

    base_mero = sqlite3.connect('mero')
    cur_mero = base_mero.cursor()

    try:
        cur_list.execute(f'DELETE FROM {club} WHERE identify = ?', (identify,))
        base_list.commit()
        bot.send_message(message.chat.id, "🎉Успешно", message_effect_id='5107584321108051014')
    except Exception as e:
        bot.send_message(message.chat.id, "❌Ошибка, скорее всего, неверный идентификатор")
        print(e)
    try:
        cur_mero.execute(f'DROP TABLE {club+identify}')
        base_mero.commit()
    except Exception as e:
        print(e)

    cur_list.close()
    base_list.close()

    cur_mero.close()
    base_mero.close()


def spam1(message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Отмена'))
    bot.send_message(message.chat.id, "💬Введите сообщение, которое хотите разослать всем юзерам бота", reply_markup=markup)
    bot.register_next_step_handler(message, spam2)


def spam2(message):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, "Отменено", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        admin(message)
        return
    bot.send_message(message.chat.id, f'Вы точно хотите отправить "{message.text}" ВСЕМ юзерам бота? Введите ДА, чтобы подтвердить действие')
    bot.register_next_step_handler(message, spam3, message.text)


def spam3(message, text):
    if message.text != 'ДА':
        bot.send_message(message.chat.id, '❌Действие не подтверждено!')
    else:
        base = sqlite3.connect('users')
        cur = base.cursor()

        cur.execute('SELECT * FROM users')
        users = cur.fetchall()

        cur.close()
        base.close()

        for i in users:
            bot.send_message(i[1], text)


def send1(message, identify, club=None):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Отмена'))
    markup.add(types.KeyboardButton('Оплата взноса'))
    markup.add(types.KeyboardButton('Подтверждение участия'))
    bot.send_message(message.chat.id,"Введите сообщение, которое хотите разослать всем участникам или выберите кнопку ниже", reply_markup=markup)
    bot.register_next_step_handler(message, send2, identify, club)


def send2(message, identify, club):
    if message.text == 'Отмена':
        bot.send_message(message.chat.id, "Отменено", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        admin(message)
        return

    if message.text == 'Оплата взноса':
        name, typ = '', ''
        cost, status = 0, 0
        if club:
            base = sqlite3.connect('mero')
            cur = base.cursor()
            base_info = sqlite3.connect('clubs')
            cur_info = base_info.cursor()

            try:
                cur_info.execute(f'SELECT * FROM {club} WHERE identify = ?', (identify,))
            except:
                bot.send_message(message.chat.id, "Участников нет!", reply_markup=types.ReplyKeyboardRemove())
                cur.close()
                base.close()
                cur_info.close()
                base_info.close()
                return
            data = cur_info.fetchall()
            for i in data:
                name = i[2]
                status = i[6]
                cost = int(i[7])
                break

            try:
                cur.execute(f'SELECT * FROM {club + identify}')
            except:
                bot.send_message(message.chat.id, "❌Участников нет!", reply_markup=types.ReplyKeyboardRemove())
                cur.close()
                base.close()
                cur_info.close()
                base_info.close()
                return
            players = cur.fetchall()
            payload = club + identify
        else:
            base = sqlite3.connect('tournament')
            cur = base.cursor()
            base_info = sqlite3.connect('tournaments_list')
            cur_info = base_info.cursor()

            cur_info.execute('SELECT * FROM tournaments WHERE identify = ?', (identify,))
            data = cur_info.fetchall()
            for i in data:
                name = i[2]
                typ = i[7]
                status = i[9]
                cost = int(i[10])
                break

            try:
                cur.execute(f'SELECT * FROM {identify}')
            except:
                bot.send_message(message.chat.id, "❌Участников нет!", reply_markup=types.ReplyKeyboardRemove())
                cur.close()
                base.close()
                cur_info.close()
                base_info.close()
                return
            players = cur.fetchall()
            payload = identify

        cur.close()
        base.close()
        cur_info.close()
        base_info.close()

        if cost < 1:
            bot.send_message(message.chat.id, "❌Участие бесплатное!")
            return

        if players:
            if typ != 'team':
                if status != 2:
                    for i in players:
                        if not i[4]:  # paid
                            bot.send_invoice(i[1], '💸Оплатить участие', f'Вы - участник {name.lower()}. Пожалуйста, оплатите взнос за участие', payload, settings['PAY_TOKEN'], 'RUB', [types.LabeledPrice("Оплатить", cost * 100)])
                else:  # status == 2
                    for i in players:
                        if i[6] == 1 and not i[4]:  # requests and not paid
                            bot.send_invoice(i[1], '💸Оплатить участие', f'Вы - участник {name.lower()}. Пожалуйста, оплатите взнос за участие', payload, settings['PAY_TOKEN'], 'RUB', [types.LabeledPrice("Оплатить", cost*100)])
            else:  # typ = 'team'
                for i in players:
                    if status != 2:
                        if not i[4]:
                            bot.send_invoice(i[1], '💸Оплатить участие', f'Вы - создатель команды в турнире {name.lower()}. Пожалуйста, оплатите взнос за участие вашей команды', payload, settings['PAY_TOKEN'], 'RUB', [types.LabeledPrice("Оплатить", cost*100)])
                    else:  # status == 2
                        if i[6] == 1 and not i[4]:
                            bot.send_invoice(i[1], '💸Оплатить участие', f'Вы - создатель команды в турнире {name.lower()}. Пожалуйста, оплатите взнос за участие вашей команды', payload, settings['PAY_TOKEN'], 'RUB', [types.LabeledPrice("Оплатить", cost * 100)])
            bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        return

    if message.text == 'Подтверждение участия':
        markup = types.InlineKeyboardMarkup()
        name = ''
        status = 0
        if club:
            base = sqlite3.connect('mero')
            cur = base.cursor()
            base_info = sqlite3.connect('clubs')
            cur_info = base_info.cursor()

            cur_info.execute(f'SELECT * FROM {club} WHERE identify = ?', (identify,))
            data = cur_info.fetchall()
            for i in data:
                name = i[2]
                status = i[6]
                break

            try:
                cur.execute(f'SELECT * FROM {club + identify}')
            except:
                bot.send_message(message.chat.id, "❌Участников нет!", reply_markup=types.ReplyKeyboardRemove())
                cur.close()
                base.close()
                cur_info.close()
                base_info.close()
                return
            players = cur.fetchall()
            markup.add(types.InlineKeyboardButton('✅Подтвердить участие', callback_data=club+identify+'confirm'))
        else:
            base = sqlite3.connect('tournament')
            cur = base.cursor()
            base_info = sqlite3.connect('tournaments_list')
            cur_info = base_info.cursor()

            cur_info.execute('SELECT * FROM tournaments WHERE identify = ?', (identify,))
            data = cur_info.fetchall()
            for i in data:
                name = i[2]
                status = i[9]
                break

            try:
                cur.execute(f'SELECT * FROM {identify}')
            except:
                bot.send_message(message.chat.id, "❌Участников нет!", reply_markup=types.ReplyKeyboardRemove())
                cur.close()
                base.close()
                cur_info.close()
                base_info.close()
                return
            players = cur.fetchall()
            markup.add(types.InlineKeyboardButton('✅Подтвердить участие', callback_data=identify+'confirm'))

        cur.close()
        base.close()
        cur_info.close()
        base_info.close()

        if status != 2:
            for i in players:
                bot.send_message(i[1], f'Вы - участник {name.lower()}. ✅Подтвердите свое участие', reply_markup=markup)
        else:
            for i in players:
                if i[6] == 1:
                    bot.send_message(i[1], f'Вы - участник {name.lower()}. ✅Подтвердите свое участие', reply_markup=markup)
        bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')
        return

    if club:
        base = sqlite3.connect('mero')
        cur = base.cursor()
        cur.execute(f'SELECT * FROM {club + identify}')
    else:
        base = sqlite3.connect('tournament')
        cur = base.cursor()
        cur.execute(f'SELECT * FROM {identify}')
    players = cur.fetchall()
    cur.close()
    base.close()
    for i in players:
        if i[1] != '0' and i[6] == 1:
            bot.send_message(i[1], message.text)
    bot.send_message(message.chat.id, "🎉Успешно", reply_markup=types.ReplyKeyboardRemove(), message_effect_id='5107584321108051014')


'''@bot.message_handler(commands=['add'])
def creating_tables(message):
    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()
    #clubs = ['DarkTurn', 'LETI', 'Polytech', 'Mining', 'EveningParty', 'TechnoMafia', 'BONCHMAFIA', 'BlackInside']
    #for club in clubs:
    cur.execute(f'ALTER TABLE tournaments ADD COLUMN distance TEXT NOT NULL DEFAULT {None}')
    base.commit()
    cur.close()
    base.close()

    #base = sqlite3.connect('users')
    #cur = base.cursor()
    #cur.execute('CREATE TABLE IF NOT EXISTS users (num INTEGER PRIMARY KEY, id TEXT NOT NULL, nick TEXT NOT NULL, club TEXT NOT NULL)')
    #base.commit()
    #cur.close()
    #base.close()

    base = sqlite3.connect('clubs')
    cur = base.cursor()
    clubs = ['DarkTurn', 'LETI', 'Polytech', 'Mining', 'EveningParty', 'TechnoMafia', 'BONCHMAFIA', 'BlackInside']
    for club in clubs:
        cur.execute(f'CREATE TABLE IF NOT EXISTS {club} (num INTEGER PRIMARY KEY, identify TEXT NOT NULL, name TEXT NOT NULL, desc TEXT NOT NULL, date TEXT NOT NULL, limits INTEGER, status INTEGER, cost INTEGER)')
        base.commit()
    cur.close()
    base.close()

    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS tournaments (num INTEGER PRIMARY KEY, identify TEXT NOT NULL, name TEXT NOT NULL, desc TEXT NOT NULL, date TEXT NOT NULL, rules TEXT NOT NULL, score TEXT NOT NULL, type TEXT NOT NULL, limits INTEGER, status INTEGER, cost INTEGER)')
    base.commit()
    cur.close()
    base.close()

    bot.send_message(message.chat.id, 'У')'''


def donut1(message):
    bot.send_message(message.chat.id, "❤Спасибо, что решили поддержать нас!!\nПожалуйста, введите сумму, на которую хотите нас поддержать (60р и больше)")
    bot.register_next_step_handler(message, donut2)


def donut2(message):
    try:
        int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌Введите целое число")
        return
    if int(message.text.strip()) < 60:
        bot.send_message(message.chat.id, "❌Минимальная сумма 60р!")
        return
    bot.send_invoice(message.chat.id, 'Донат', 'Поддержите организаторов студлиги!', 'donut', settings['PAY_TOKEN'], 'RUB', [types.LabeledPrice("❤", int(message.text)*100)])


@bot.message_handler()
def meow(message):
    if message.text.lower() == 'мяу':
        bot.reply_to(message, "мяу")
        print(f"Мяу от {message.from_user.first_name} {message.from_user.last_name}")
    if "send" in message.text:
         bot.send_message(-4691783391, message.text[5:])


while True:
    try:
        bot.polling(none_stop=True)
    except:
        pass
