from datetime import datetime
from typing import Literal

from sqlalchemy import MetaData, DateTime, Column, Integer, String, TEXT, DATE, TIME, JSON, BOOLEAN, TIMESTAMP, select, \
    insert, delete, update, inspect, Float, func, Computed
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker, as_declarative
from sqlalchemy.sql import expression

from create_bot import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@as_declarative()
class Base:
    metadata = MetaData()


class IrkutskTZ(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(IrkutskTZ, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('Asia/Irkutsk', CURRENT_TIMESTAMP)"


class UsersDB(Base):
    """Пользователи"""
    __tablename__ = "users"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=False, server_default="")
    reg_dtime = Column(TIMESTAMP, nullable=False, server_default=IrkutskTZ())


class TicketsDB(Base):
    """Заявки на обмен"""
    __tablename__ = "tickets"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    user_id = Column(String, nullable=False)
    username = Column(String, nullable=True)
    reg_dtime = Column(DateTime(timezone=True), nullable=False, server_default=IrkutskTZ())
    operation = Column(String, nullable=False, server_default="sell")
    coin = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default="0.0")
    price = Column(Float, nullable=False, default="0.0")
    total = Column(Float, Computed("quantity * price"))
    status = Column(String, nullable=False, server_default="created")
    finish_dtime = Column(DateTime(timezone=True), nullable=True)


class BaseDAO:
    """Класс взаимодействия с БД"""
    model = None

    @classmethod
    async def get_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by).limit(1)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def get_many(cls, **filter_by) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            stmt = insert(cls.model).values(**data).returning(cls.model.id)
            result = await session.execute(stmt)
            await session.commit()
            return result.scalar()

    @classmethod
    async def update_by_id(cls, item_id: int, **data):
        async with async_session_maker() as session:
            stmt = update(cls.model).values(**data).filter_by(id=item_id)
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def delete(cls, **data):
        async with async_session_maker() as session:
            stmt = delete(cls.model).filter_by(**data)
            await session.execute(stmt)
            await session.commit()


class UsersDAO(BaseDAO):
    model = UsersDB

    @classmethod
    async def get_many_by_date(cls, start_date: datetime) -> list:
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).where(cls.model.reg_dtime >= start_date)
            result = await session.execute(query)
            return result.mappings().all()


class TicketsDAO(BaseDAO):
    model = TicketsDB

    @classmethod
    async def get_many_by_date(cls, start_date: datetime, status: Literal["created", "finished"]) -> list:
        async with async_session_maker() as session:
            query = select(func.count(cls.model.id), func.sum(cls.model.total), cls.model.status).\
                where(cls.model.reg_dtime >= start_date, cls.model.status == status).group_by(cls.model.status)
            result = await session.execute(query)
            return result.mappings().one_or_none()

