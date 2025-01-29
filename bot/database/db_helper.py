from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, async_scoped_session
from asyncio import current_task
from bot.config import settings
from .models import Base


class DatabaseHelper:
    def __init__(self, url, echo):
        self.engine = create_async_engine(
            url=url,
            echo=echo
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    def get_scoped_session(self) -> AsyncSession:
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task
        )
        return session
    
    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        yield session
        await session.close()
    
    async def create_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


db_helper = DatabaseHelper(url=settings.DATABASE_URL_asyncpg, echo=False)