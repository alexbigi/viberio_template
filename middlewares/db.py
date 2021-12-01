from db.repository import Repo
from viberio.dispatcher.middlewares import LifetimeControllerMiddleware


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ['error', 'update']

    def __init__(self, sm):
        super().__init__()
        self.sessionmaker = sm

    async def pre_process(self, obj, data, *args):
        session = self.sessionmaker()
        data["repo"] = Repo(session)

    async def post_process(self, obj, data, *args):
        repo: Repo = data.get("repo")
        if repo:
            await repo.session.close()