import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.api.endpoints.endpoints import get_uow_factory, get_summary_service
from app.db.database import Base
from app.services.summary import SummaryService
from app.utils.unit_of_work import UnitOfWork, UnitOfWorkFactory
from main import app as fastapi_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(async_engine):
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session):
    def override_summary_service():
        return SummaryService(UnitOfWork(session_factory=lambda: db_session))

    def override_uow_factory():
        return UnitOfWorkFactory(session_factory=lambda: db_session)

    fastapi_app.dependency_overrides[get_summary_service] = override_summary_service
    fastapi_app.dependency_overrides[get_uow_factory] = override_uow_factory

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides = {}
