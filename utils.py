from sqlalchemy import select
from cachetools import TTLCache
from asyncache import cached
from datetime import timedelta

from tables import RegistrationsTable, TournamentsTable
from config import asession

tourn_cache = TTLCache(maxsize=1, ttl=timedelta(3).total_seconds())


async def is_user_registered(user_id: int, event_id: int) -> bool:
    async with asession() as session:
        query = select(RegistrationsTable).where(
            (RegistrationsTable.user_id == user_id) &
            (RegistrationsTable.event_id == event_id)
            )
        await session.flush()
        result = await session.execute(query)
        result = result.scalar_one_or_none()
    return result is not None


async def is_user_paid(user_id: int, event_id: int) -> bool:
    async with asession() as session:
        query = select(RegistrationsTable.paid).where(
            (RegistrationsTable.user_id == user_id) &
            (RegistrationsTable.event_id == event_id)
            )
        await session.flush()
        result = await session.execute(query)
        result = result.scalar_one_or_none()
    return result


@cached(tourn_cache)
async def get_tournament_info(number: int):
    async with asession() as session:
        query = select(TournamentsTable).where(TournamentsTable.num == number)
        result = await session.execute(query)
        tourn_info = result.all()[0][0]
        query = select(RegistrationsTable.num).where(RegistrationsTable.event_id == number)
        result = await session.execute(query)
    try:
        members = len(result.all()[0])
    except:
        members = 0
    return [tourn_info, members]
