import sqlalchemy.exc
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import models


class Repo:
    def __init__(self, session):
        self._session = session

    async def _add_user(self, id, name, country, api_version, language):
        obj = await self._session.execute(select(models.User).where(models.User.user_id == id))
        try:
            check = obj.scalars().one()
        except sqlalchemy.exc.NoResultFound:
            u = models.User(user_id=id, name=name, country=country, api_version=api_version, language=language)
            self._session.add(u)

    async def add_user(self, id, name, country, api_version, language):
        try:
            await self._add_user(id, name, country, api_version, language)
            await self._session.commit()
        except IntegrityError as err:
            await self._session.rollback()
        except SQLAlchemyError as err:
            await self._session.rollback()
            # logging.exception(err)

    async def add_user_from_message(self, id, name, country, api_version, language):
        await self.add_user(id, name, country, api_version, language)

    async def get_all_users(self) -> list:
        res = await self._session.execute(select(models.User).order_by(models.User.id))
        return [c.to_dict() for c in res.scalars().all()]

    async def get_user_by_id(self, user_id) -> dict:
        obj = await self._session.get(models.User, user_id)
        return obj.to_dict()

    async def get_current_state(self, user_id):
        obj = await self._session.execute(select(models.States).where(models.States.user_id == user_id))
        try:
            check = obj.scalars().one()
            state_dict = check.to_dict()
            return {"state": state_dict["state"], "vars": eval(state_dict["vars"])}
        except sqlalchemy.exc.NoResultFound:
            try:
                u = models.States(user_id=user_id, state="*", vars="{}")
                self._session.add(u)
                await self._session.commit()
            except IntegrityError as err:
                await self._session.rollback()
            except SQLAlchemyError as err:
                await self._session.rollback()
            return {"state": "*", "vars": {}}

    async def set_state(self, user_id, state):
        try:
            await self._session.execute(
                update(models.States).where(models.States.user_id == user_id).values(state=state))
            await self._session.commit()
        except IntegrityError as err:
            await self._session.rollback()
        except SQLAlchemyError as err:
            await self._session.rollback()
        pass

    async def set_state_vars(self, user_id, vars):
        try:
            await self._session.execute(update(models.States).where(models.States.user_id == user_id).values(vars=str(vars)))
            await self._session.commit()
        except IntegrityError as err:
            await self._session.rollback()
        except SQLAlchemyError as err:
            await self._session.rollback()
        pass

    @property
    def session(self):
        return self._session
