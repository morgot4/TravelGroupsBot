from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    async_scoped_session,
)
from asyncio import current_task
from bot.config import settings
from contextlib import asynccontextmanager

class DatabaseHelper:
    def __init__(self, url, echo):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    def get_scoped_session(self) -> AsyncSession:
        return async_scoped_session(
            session_factory=self.session_factory, scopefunc=current_task
        )

    @asynccontextmanager
    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            await session.remove()  


db_helper = DatabaseHelper(url=settings.DATABASE_URL_asyncpg, echo=False)
