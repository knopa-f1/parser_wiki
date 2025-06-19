from app.db.database import async_session_maker

from app.repositories.article import ArticleRepository
from app.repositories.summary import SummaryRepository


class UnitOfWork:
    def __init__(self, session_factory=None):
        if session_factory is None:
            self.session_factory = async_session_maker
        else:
            self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.articles = ArticleRepository(self.session)
        self.summaries = SummaryRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


class UnitOfWorkFactory: # pylint: disable=too-few-public-methods
    def __init__(self, session_factory=async_session_maker):
        self.session_factory = session_factory

    def __call__(self) -> UnitOfWork:
        return UnitOfWork(session_factory=self.session_factory)
