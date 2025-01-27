from config import settings
import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot(settings['TOKEN'])
mero_info = []


def tournaments_list(message, typ):  # typ = 1 - команда вызвана админом, = 0 - обычным пользователем
    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()

    cur.execute('SELECT * FROM tournaments')
    data = cur.fetchall()

    cur.close()
    base.close()

    markup = types.InlineKeyboardMarkup()
    if typ:
        markup.add(types.InlineKeyboardButton('🎴Создать турнир', callback_data='create_tourn'))
        for i in data:
            markup.add(types.InlineKeyboardButton(i[2], callback_data=i[1]+'ad'))
    else:
        for i in data:
            if i[9]:
                markup.add(types.InlineKeyboardButton(i[2], callback_data=i[1]))
        markup.add(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
    bot.send_message(message.chat.id, "🎟Выберите турнир:", reply_markup=markup)


def info(name, desc, date, limit, status, rules=None, score=None, typ=None, members=None, cost=None, distance=None):
    out = ''
    out += name + '\n\n' + desc + '\n\n'
    if distance:
        if int(distance) == 4:
            out += '📏Дистанция: ' + distance + ' игры\n'
        else:
            out += '📏Дистанция: ' + distance + ' игр\n'
    out += '🗓Дата: ' + date + '\n'
    if rules:
        out += '📖Правила: ' + rules + '\n'
    if score:
        out += '🎰Скоринг: ' + score + '\n'
    if typ:
        if typ == 'team':
            if int(cost) > 0:
                out += '💸Взнос за команду ' + str(cost) + ' рублей\n\n'
            out += '🗄Тип: командный' + '\n'
        else:
            if int(cost) > 0:
                out += '💸Взнос ' + str(cost) + ' рублей\n\n'
            out += '🗄Тип: личный' + '\n'
    else:
        if int(cost) > 0:
                out += '💸Взнос ' + str(cost) + ' рублей\n\n'
    if members:
        if typ != 'team':
            out += '🙍‍♂️' + str(members) + '/' + str(limit) + ' участников\n'
        else:
            out += '👬' + str(members) + '/' + str(limit) + ' команд\n'
    else:
        if typ != 'team':
            out += '🙍‍♂️Лимит ' + str(limit) + ' участников\n'
        else:
            out += '👨‍👨‍👦Лимит ' + str(limit) + ' команд\n'

    if int(status) == 1 and members:
        if members < int(limit):
            out += '💡Статус: Регистрация открыта'
        else:
            out += '💡Статус: Турнир заполнен'
    elif int(status) == 2 and members:
        if members < int(limit):
            out += '💡Статус: Можно подать заявку на участие'
        else:
            out += '💡Статус: Турнир заполнен'
    elif int(status) == 1:
        out += '💡Статус: Регистрация открыта'
    elif int(status) == 2:
        out += '💡Статус: Можно подать заявку на участие'
    elif int(status) == 0:
        out += '💡Статус: Виден только админам'
    return out


def tournament_info(message, identify, typ):  # typ = 1 - команда вызвана админом, = 0 - обычным пользователем,
    base = sqlite3.connect('tournament')
    cur = base.cursor()

    try:
        cur.execute(f'SELECT * FROM {identify}')
        players = cur.fetchall()
    except:
        players = []

    cur.close()
    base.close()

    base = sqlite3.connect('tournaments_list')
    cur = base.cursor()
    cur.execute('SELECT * FROM tournaments WHERE identify = ?', (identify,))
    data = cur.fetchall()
    cur.close()
    base.close()

    status = 0
    typ_tour = ''
    for i in data:
        typ_tour = i[7]
        status = i[9]

    cnt = 0  # счётчик игроков в турнире
    if players:
        if status == 2:
            for i in players:
                if i[6] == 1:
                    cnt += 1
        else:
            for i in players:
                cnt += 1

    output = ''
    for i in data:
        output = info(i[2], i[3], i[4], rules=i[5], score=i[6], typ=i[7], limit=i[8], status=i[9], members=cnt, cost=i[10], distance=i[11])
        break

    markup = types.InlineKeyboardMarkup()
    if typ == 1:
        if status == 2:
            markup.add(types.InlineKeyboardButton('📜Посмотреть заявки', callback_data=identify + 'requests'))
        markup.add(types.InlineKeyboardButton('📝Изменить турнир', callback_data=identify + 'edit'))
        markup.add(types.InlineKeyboardButton('👀Удалить турнир', callback_data=identify + 'delete'))
        markup.add(types.InlineKeyboardButton('💌Рассылка', callback_data=identify + 'send'))
        markup.add(types.InlineKeyboardButton('🖼Посмореть профили', callback_data=identify + 'profiles'))
    else:
        markup.add(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
        if status == 1:
            markup.add(types.InlineKeyboardButton('📝Регистрация', callback_data=identify + 'tourn_reg'))
        else:
            markup.add(types.InlineKeyboardButton('📝Отправить заявку', callback_data=identify + 'tourn_reg'))
        if typ_tour == 'team':
            markup.add(types.InlineKeyboardButton('📷Фото', callback_data=identify + 'add_photo'))
        markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=identify + 'members'))

    try:
        save_path = f'photos\\announcements\\{identify}.png'
        with open(save_path, 'rb') as file:
            bot.send_photo(message.chat.id, file, caption=output, reply_markup=markup)  # Вывод описания турнира с фото
    except:
        bot.send_message(message.chat.id, output, reply_markup=markup)  # Вывод описания турнира


def registering(message, identify, club=None): # typ занят!
    base_users = sqlite3.connect('users')
    cur_users = base_users.cursor()

    if club:
        base_tourn = sqlite3.connect('mero')
        cur_tourn = base_tourn.cursor()
        base_info = sqlite3.connect('clubs')
        cur_info = base_info.cursor()

    else:
        base_tourn = sqlite3.connect('tournament')
        cur_tourn = base_tourn.cursor()
        base_info = sqlite3.connect('tournaments_list')
        cur_info = base_info.cursor()

    cur_users.execute('SELECT * FROM users WHERE id = ?', (message.chat.id, ))
    user = cur_users.fetchall()
    if user == []:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton('📝Зарегистрироваться в боте', callback_data='start_reg'))
        bot.send_message(message.chat.id, f"❌Ошибка: вы не зарегистрированы в боте!", reply_markup=markup)
        return

    status = 0
    typ = ''
    limit = 0
    if club:
        cur_tourn.execute(f'CREATE TABLE IF NOT EXISTS {club+identify} (num INTEGER PRIMARY KEY, id TEXT NOT NULL, nick TEXT NOT NULL, club TEXT NOT NULL, paid INTEGER, confirm INTEGER, request INTEGER)')
        base_tourn.commit()
        cur_tourn.execute(f'SELECT * FROM {club+identify}')

        cur_info.execute(f'SELECT status, limits FROM {club} WHERE identify = ?', (identify,))
        status_base = cur_info.fetchall()
        for i in status_base:
            status = i[0]
            limit = i[1]
    else:
        cur_tourn.execute(f'CREATE TABLE IF NOT EXISTS {identify} (num INTEGER PRIMARY KEY, id TEXT NOT NULL, nick TEXT NOT NULL, club TEXT NOT NULL, paid INTEGER, confirm INTEGER, request INTEGER)')
        base_tourn.commit()
        cur_tourn.execute(f'SELECT * FROM {identify}')
        cur_info.execute('SELECT status, limits, type FROM tournaments WHERE identify = ?', (identify,))
        status_base = cur_info.fetchall()
        for i in status_base:
            status = i[0]
            limit = i[1]
            typ = i[2]
    players = cur_tourn.fetchall()

    cur_info.close()
    base_info.close()
    cur_users.close()
    base_users.close()

    cnt = 0
    for i in players:  # Если пользователь уже зарегистрирован на меро/турнир
        cnt += 1
        if i[1] == str(message.chat.id):
            markup = types.InlineKeyboardMarkup()
            if club:
                markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=club + identify + 'members'))
                markup.add(types.InlineKeyboardButton('❌Отменить регистрацию', callback_data=club + identify + 'cancel_reg'))
            else:
                markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников турнира', callback_data=identify + 'members'))
                markup.add(types.InlineKeyboardButton('❌Отменить регистрацию', callback_data=identify + 'cancel_reg'))
            markup.add(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
            if i[6] == 0 and status == 2:
                bot.send_message(message.chat.id, f"❌Вы уже подали заявку!", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f"❌Вы уже зарегистрированы!", reply_markup=markup)
            cur_tourn.close()
            base_tourn.close()
            return

    if cnt >= int(limit):  # Если меро/турнир заполнен
        markup = types.InlineKeyboardMarkup()
        if club:
            markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=club + identify + 'members'))
        else:
            markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=identify + 'members'))
        markup.row(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
        bot.send_message(message.chat.id, f"❌Места закончились!", reply_markup=markup)
        cur_tourn.close()
        base_tourn.close()
        cur_users.close()
        base_users.close()
        return

    if typ == 'team':
        teamreg1(message, identify, status)
        return
    for i in user:  # Подготовка к передаче данных в таблицу для рега
        nick = i[2]
        club_user = i[3]

        if club:
            cur_tourn.execute(f'INSERT INTO {club+identify} (id, nick, club, request) VALUES ("{message.chat.id}", "{nick}", "{club_user}", 0)')
        else:
            cur_tourn.execute(f'INSERT INTO {identify} (id, nick, club, request) VALUES ("{message.chat.id}", "{nick}", "{club_user}", 0)')
        base_tourn.commit()

        cur_tourn.close()
        base_tourn.close()

        markup = types.InlineKeyboardMarkup()
        if club:
            markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=club + identify + 'members'))
        else:
            markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=identify + 'members'))
        markup.row(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
        if status == 1:
            bot.send_message(message.chat.id, "🎉Вы зарегистрировались!", message_effect_id='5107584321108051014', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "🎉Ваша заявка отправлена!", message_effect_id='5107584321108051014', reply_markup=markup)
        break


def teamreg1(message, identify, status):
    global mero_info
    mero_info.append(identify)
    mero_info.append(status)
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('📝Зарегистрироваться', web_app=types.WebAppInfo(
        url='https://acc-maf.github.io/StudLeagueBot/team_reg.html')))
    bot.send_message(message.chat.id, '📝Нажмите на кнопку для регистрации команды', reply_markup=markup)


def teamreg2(message, data):
    bot.send_message(message.chat.id, '.', reply_markup=types.ReplyKeyboardRemove())  # сообщение для удаления плиток
    bot.delete_message(message.chat.id, message.message_id + 1)
    global mero_info  # [0] - identify, [1] - status
    base_tourn = sqlite3.connect('tournament')
    cur_tourn = base_tourn.cursor()

    nick = data["nick"]
    members = ''
    for i in range(len(data) - 1):
        members += data['member' + str(i)] + ', '
    members = members[:-2]

    cur_tourn.execute(f'INSERT INTO {mero_info[0]} (id, nick, club, request) VALUES ("{message.chat.id}", "{nick}", "{members}", 0)')
    base_tourn.commit()  # в столбец club попадают ники участников команды
    cur_tourn.close()
    base_tourn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=mero_info[0] + 'members'))
    markup.row(types.InlineKeyboardButton('📷Добавить фото', callback_data=mero_info[0] + 'add_photo'))
    markup.row(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
    if mero_info[1] == 1:
        bot.send_message(message.chat.id, "🎉Вы зарегистрировались!", message_effect_id='5107584321108051014', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "🎉Ваша заявка отправлена!", message_effect_id='5107584321108051014', reply_markup=markup)
    mero_info.clear()


def mero_members(message, identify, typ, club=None):  # typ = 1 - вызвана при ручном изменении участников турнира
    status, type_tour = 0, ''
    if club:
        base = sqlite3.connect('mero')
        cur = base.cursor()
        base_info = sqlite3.connect('clubs')
        cur_info = base_info.cursor()
        cur_info.execute(f'SELECT status FROM {club} WHERE identify = ?', (identify,))
        status_base = cur_info.fetchall()
        cur_info.close()
        base_info.close()
        for i in status_base:
            status = i[0]
            type_tour = 'solo'
    else:
        base = sqlite3.connect('tournament')
        cur = base.cursor()
        base_info = sqlite3.connect('tournaments_list')
        cur_info = base_info.cursor()
        cur_info.execute('SELECT status, type FROM tournaments WHERE identify = ?', (identify,))
        status_base = cur_info.fetchall()
        cur_info.close()
        base_info.close()
        for i in status_base:
            status = i[0]
            type_tour = 'solo'

    if status != 2:
        try:
            if club:
                cur.execute(f'SELECT * FROM {club+identify}')
            else:
                cur.execute(f'SELECT * FROM {identify}')
            players = cur.fetchall()
        except:
            players = []
    else:
        try:
            if club:
                cur.execute(f'SELECT * FROM {club+identify} WHERE request = 1')
            else:
                cur.execute(f'SELECT * FROM {identify} WHERE request = 1')
            players = cur.fetchall()
        except:
            players = []

    cur.close()
    base.close()

    players_output = ''
    cc = 0  # счётчик игроков
    for i in players:
        cc += 1
        if i[5] and i[5] == 1:
            players_output += '✅'
        if type_tour == 'team':
            if typ and typ == 1:
                players_output += f'№{cc}. {i[2]} - @{bot.get_chat(i[1]).username} - {i[3]}'  # Команды
            else:
                players_output += f'№{i[0]}. {i[2]} - @{bot.get_chat(i[1]).username} - {i[3]}'  # Команды
        else:
            if typ and typ == 1:
                players_output += f'№{cc}. {i[2]} - @{bot.get_chat(i[1]).username} - {i[3]}'  # Игроки
            else:
                players_output += f'№{i[0]}. {i[2]} - @{bot.get_chat(i[1]).username} - {i[3]}'  # Игроки
        if i[4] and i[4] == 1:
            players_output += ' - взнос оплачен'
        players_output += '\n'
    if players_output == '':
        players_output = 'Участников нет!'

    markup = types.InlineKeyboardMarkup()
    if typ == 1:
        for i in players:
            if i[1] == str(message.chat.id):
                if club:
                    markup.row(types.InlineKeyboardButton('❌Отменить регистрацию', callback_data=club+identify+'cancel_reg'))
                else:
                    markup.row(types.InlineKeyboardButton('❌Отменить регистрацию', callback_data=identify+'cancel_reg'))
                break
        else:
            if club:
                markup.row(types.InlineKeyboardButton('📝Зарегистрироваться', callback_data=club+identify+'reg'))
            else:
                markup.row(types.InlineKeyboardButton('📝Зарегистрироваться', callback_data=identify+'tourn_reg'))
        markup.row(types.InlineKeyboardButton('📌Меню', callback_data='menu'))
    bot.send_message(message.chat.id, players_output, reply_markup=markup)


def cancel_reg(message, identify, club=None):
    if club:
        base = sqlite3.connect('mero')
        cur = base.cursor()
    else:
        base = sqlite3.connect('tournament')
        cur = base.cursor()

    if club:
        cur.execute(f'SELECT * FROM {club+identify}')
    else:
        cur.execute(f'SELECT * FROM {identify}')
    players = cur.fetchall()

    for i in players:
        if i[1] == str(message.chat.id):  # Отмена регистрации (проверка на наличие в списке)
            if club:
                cur.execute(f'DELETE FROM {club+identify} WHERE id = {message.chat.id}')
            else:
                cur.execute(f'DELETE FROM {identify} WHERE id = {message.chat.id}')
            base.commit()
            markup = types.InlineKeyboardMarkup()
            if club:
                markup.row(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=club+identify+'members'))
            else:
                markup.row(types.InlineKeyboardButton('🙍‍♂️Список участников', callback_data=identify+'members'))
            markup.row(types.InlineKeyboardButton('📌Вернуться в меню', callback_data='menu'))
            bot.send_message(message.chat.id, "🎉Регистрация отменена", message_effect_id='5107584321108051014', reply_markup=markup)

    cur.close()
    base.close()


def check_requests(message, identify, club=None):
    if club:
        base = sqlite3.connect('mero')
        cur = base.cursor()
        cur.execute(f'SELECT * FROM {club+identify} WHERE request = 0')
        apps = cur.fetchall()
    else:
        base = sqlite3.connect('tournament')
        cur = base.cursor()
        cur.execute(f'SELECT * FROM {identify} WHERE request = 0')
        apps = cur.fetchall()
    cur.close()
    base.close()

    if apps:
        for i in apps:
            markup = types.InlineKeyboardMarkup()
            if club:
                markup.add(types.InlineKeyboardButton('✅Подтвердить заявку', callback_data=i[1] + club + identify + 'accept'))
                markup.add(types.InlineKeyboardButton('❌Отклонить заявку', callback_data=i[1] + club + identify + 'decline'))
            else:
                markup.add(types.InlineKeyboardButton('✅Подтвердить заявку', callback_data=i[1] + identify + 'accept'))
                markup.add(types.InlineKeyboardButton('❌Отклонить заявку', callback_data=i[1] + identify + 'decline'))
            if ',' in i[3]:
                bot.send_message(message.chat.id, f'Название: {i[2]}, Состав: {i[3]}', reply_markup=markup)
                continue
            bot.send_message(message.chat.id, f'Ник: {i[2]}, Клуб: {i[3]}', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Заявок нет!')


def accept_request(message, identify, member_id, club=None):
    if club:
        base = sqlite3.connect('mero')
        cur = base.cursor()
        cur.execute(f'UPDATE {club + identify} SET request = ? WHERE id = ?', (1, member_id))
    else:
        base = sqlite3.connect('tournament')
        cur = base.cursor()
        cur.execute(f'UPDATE {identify} SET request = ? WHERE id = ?', (1, member_id))
    base.commit()
    cur.close()
    base.close()
    bot.send_message(message.chat.id, '✅Заявка успешно принята', message_effect_id='5107584321108051014')


def decline_request(message, identify, member_id, club=None):
    if club:
        base = sqlite3.connect('mero')
        cur = base.cursor()
        cur.execute(f'DELETE FROM {club + identify} WHERE id = {member_id}')
    else:
        base = sqlite3.connect('tournament')
        cur = base.cursor()
        cur.execute(f'DELETE FROM {identify} WHERE id = {member_id}')
    base.commit()
    cur.close()
    base.close()
    bot.send_message(message.chat.id, '❌Заявка успешно отклонена', message_effect_id='5107584321108051014')


def confirm(message, identify, club=None):
    if club:
        base_mero = sqlite3.connect('mero')
        cur_mero = base_mero.cursor()
        try:
            cur_mero.execute(f'UPDATE {club + identify} SET confirm = ? WHERE id = ?', (1, message.chat.id))
        except:
            bot.send_message(message.chat.id, "❌Что-то пошло не так!")
            cur_mero.close()
            base_mero.close()
            return
        base_mero.commit()
        cur_mero.close()
        base_mero.close()
    else:
        base_mero = sqlite3.connect('tournament')
        cur_mero = base_mero.cursor()
        try:
            cur_mero.execute(f'UPDATE {identify} SET confirm = ? WHERE id = ?', (1, message.chat.id))
        except:
            bot.send_message(message.chat.id, "❌Что-то пошло не так!")
            cur_mero.close()
            base_mero.close()
            return
        base_mero.commit()
        cur_mero.close()
        base_mero.close()
    bot.send_message(message.chat.id, "🎉Вы успешно подтвердили свое участие!", message_effect_id='5107584321108051014')


def us_help(message):
    output = 'Привет! Это краткий гайд как пользоваться ботом.\n\n'
    output += 'Чтобы записаться на вечер в клубе:\n1. /menu\n2. Игры в клубах\n3. Выбери клуб\n4. Выбери мероприятие\n5. Нажми "Зарегистрироваться"\n\n'
    output += 'Чтобы записаться на турнир:\n1. /menu\n2. Турниры\n3. Выбери турнир\n4. Нажми "Зарегистрироваться"\n\n'
    output += 'Чтобы изменить свой профиль или добавить свою фотографию:\n1. /menu\n2. Профиль\n3. Изменить профиль\n4. Следовать тому, что пишет бот'
    bot.send_message(message.chat.id, output)


def ad_help(message):
    output = 'Привет! Это краткий админ гайд как пользоваться ботом.\n\n'
    output += 'Ты можешь создавать и изменять мероприятия в своем клубе. Можно создавать закрытые (ты должен сам забить участников), открытые (каждый сможет зарегистрироваться) и мероприятия по заявке.\n\n'
    output += 'Чтобы создать мероприятие:\n1. /admin\n2. Выбери свой клуб\n3. Нажми "Создать мероприятие"\n4. Заполни форму\n'
    output += '!!!МЕРОПРИЯТИЕ СОЗДАЕТСЯ ЗАКРЫТЫМ, то есть его никто не видит и не может в него записаться. Чтобы каждый смог записаться, надо изменить статус мероприятия.\n'
    output += 'Пожалуйста, удаляй мероприятия после того, как они прошли (можно спустя какое-то время)\n\n'
    output += 'Чтобы изменить мероприятие:\n1. /admin\n2. Выбери свой клуб\n3. Выбери меро, которое хочешь изменить\n4. Нажми кнопку "Изменить мероприятие"\n5. Заполни форму\n\n'
    output += 'Ещё ты можешь рассылать какие либо сообщения участникам конкретного мероприятия и брать картинки профилей для анонсов.\nЧтобы это сделать:\n'
    output += '1. /admin\n2. Выбери свой клуб\n3. Выбери мероприятие\n4. Выбери нужную опцию\n'
    output += 'Ты можешь разослать:\n- Своё сообщение (просто напиши его)\n- Счёт на оплату взноса (выбери кнопку)\n- Уведомление о подтверждении участия (выбери кнопку)\n'
    output += 'Эти сообщения придут только участникам мероприятия (тем, у кого одобрена заявка, если мероприятие по заявке). Подтверждение участия - это просто напоминание участникам о мероприятии. Добавляет им галочку в списке участников\n\n'
    output += 'Если ты хочешь создать ПЛАТНОЕ мероприятие, то можно сделать сбор денег напрямую через бота, но необходимо заранее предупредить об этом @alexstrazza И @Glasarss'

    bot.send_message(message.chat.id, output)


def schedule(message):
    output = '🏫Расписание клубов на каждую неделю этого семестра:\n\n'
    output += '🟣 Среда\n— <a href="https://vk.com/club218929976">Techno Mafia</a>, Технологический институт\n18:00-22:00\n🏛️Московский проспект 24-26/49, 250e аудитории\n📩 Проходки: раз в календарный месяц, записаться у <a href="https://vk.com/id436136968">Алисы</a>.\n\n'
    output += '🟣 Четверг\n— <a href="https://vk.com/club210592145">Polytech mafia community</a>, Политехнический университет\n18:00-22:00\n🏛️Общежитие 17. ул. Вавиловых, д.10, корп.2\n\n'
    output += '— <a href="https://t.me/mafia_itmo">Чёрный Ход</a>, ИТМО\n18:30-22:00\n🏛️Кронверский 49\n📩Проходки: необходимо заполнить <a href="https://forms.yandex.ru/cloud/66f6cb8773cee77dbdffbd87/">форму</a> до 11:00 среды\n\n'
    output += '🟣 Пятница \n— <a href="https://vk.com/club102592213">Mining Mafia</a>, Горный Университет\n17:50-21:00\n🏛️ 21-я линия Васильевского острова, 2-4/45\n📩Проходки: записаться у <a href="https://vk.com/id151957519">Романа</a> до 22:00 среды предыдущей недели.\n\n'
    output += '— <a href="https://vk.com/club219471408">LETI-MAFIA</a>, университет ЛЭТИ\n17:30-22:30\n🏛️ул. Профессора Попова 5\n📩Проходки: раз в календарный месяц, записаться у <a href="https://vk.com/id410634623">Арсения</a>.\n\n'
    output += '🟣 Суббота\n— <a href="https://vk.com/club162441832">Вечерняя партия</a>, СПбГУПТД\n17:30-21:30\n🏛️ул. Большая Морская 18, аудитории 506, 512-513\n📩Проходки: заполнить <a href="https://docs.google.com/forms/d/e/1FAIpQLScAZNiT3vFAa33n5PmUQ0koVgVJVnoPo_x_PB2inN_cr2WGzA/viewform">форму</a> до 22:00 среды\n\n'
    output += '— <a href="https://vk.com/club154981253">BONCHMAFIA</a>, Бонч-Бруевича\n15:00-21:00\n🏛️пр-к Большевиков 22\n📩Проходки: записаться у <a href="https://vk.com/id231502695">Елизаветы</a> до 22:00 среды.'
    bot.send_message(message.chat.id, output, parse_mode='html')
