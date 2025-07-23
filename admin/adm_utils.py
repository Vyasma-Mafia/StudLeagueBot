from aiogram.types import BufferedInputFile
from sqlalchemy import select
from io import BytesIO
from cachetools import LRUCache
from asyncache import cached

from config import token, asession
from tables import UsersTable, PaymentsTable, RegistrationsTable, TournamentsTable

users_cache = LRUCache(maxsize=1)


async def photo_to_file(photo_id: str, polemica_id: str | None):
    file = await token.get_file(photo_id)
    file = await token.download_file(file.file_path)
    file_buffer = BytesIO()
    file_buffer.write(file.read())
    file_buffer.seek(0)
    return BufferedInputFile(file=file_buffer.getvalue(), filename=f"{polemica_id}.png")


@cached(users_cache)
async def all_users():
    async with asession() as session:
        query = select(UsersTable)
        result = await session.execute(query)
        users = result.scalars().all()
    answer = ""
    cnt = 0
    for i in users:
        cnt += 1
        answer += f"{cnt}. {i.nick} - @{i.username} - {i.club} - {i.id}\n"
    answers = []
    for i in range(len(answer)//2000 + 1):
        answers.append(answer[2000 * i:2000 * (i + 1)])

    return answers


async def get_payments_logs():
    async with asession() as session:
        query = (
            select(PaymentsTable.cost, PaymentsTable.was, UsersTable.nick, UsersTable.username, TournamentsTable.name)
            .join(UsersTable, PaymentsTable.user_id == UsersTable.id)
            .join(RegistrationsTable, PaymentsTable.reg_id == RegistrationsTable.num)
            .join(TournamentsTable, RegistrationsTable.event_id == TournamentsTable.num)
        )
        result = await session.execute(query)
        payments = result.all()[::-1][:30]
    answer = "Список последних 30 оплат, начиная с последних:\n"
    cnt = 0
    for i in payments:
        cnt += 1
        if i.was:
            answer += "✅"
        else:
            answer += "❌"
        answer += f"{cnt}. {i.nick} - @{i.username} - {i.cost}р за {i.name}\n"
    answers = []
    for i in range(len(answer)//2000 + 1):
        answers.append(answer[2000 * i:2000 * (i + 1)])

    return answers
