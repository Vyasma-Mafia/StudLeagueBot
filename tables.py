from sqlalchemy import MetaData, ForeignKey, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from config import engine

metadata = MetaData()


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        str: Text()
    }


class UsersTable(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str]
    nick: Mapped[str]
    club: Mapped[str]
    polemica_id: Mapped[int | None]
    pfp: Mapped[str | None]


class TournamentsTable(Base):
    __tablename__ = "tournaments"
    num: Mapped[int] = mapped_column(primary_key=True)
    club: Mapped[str]
    name: Mapped[str]
    desc: Mapped[str]
    distance: Mapped[int]
    date: Mapped[str]
    federation: Mapped[str]
    type: Mapped[bool]  # True = Личный
    cost: Mapped[int]
    limit: Mapped[int]
    status: Mapped[int]  # 0 = Скрыт, 1 = Открытый рег, 2 = Рег по заявкам
    pfp: Mapped[str | None]


class RegistrationsTable(Base):
    __tablename__ = "registrations"
    num: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("tournaments.num", ondelete="CASCADE"))
    paid: Mapped[bool | None]  # оплачено (1) или нет (0)
    request: Mapped[bool | None]  # является заявкой (1) или уже записью (0)


class AdminsTable(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    clubs: Mapped[str]


class PaymentsTable(Base):
    __tablename__ = "payments"
    num: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    reg_id: Mapped[int] = mapped_column(ForeignKey("registrations.num"))
    cost: Mapped[int]
    was: Mapped[bool | None]


async def create_tables():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
