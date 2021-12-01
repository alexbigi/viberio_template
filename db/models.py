from datetime import datetime

from sqlalchemy import Column, INTEGER, TEXT, DATETIME, PrimaryKeyConstraint

from db.base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(INTEGER, autoincrement=True, primary_key=True, index=True)
    user_id = Column(TEXT, default=None)
    name = Column(TEXT, default=None)
    country = Column(TEXT, default=None)
    api_version = Column(INTEGER, default=None)
    language = Column(TEXT, default=None)
    reg_time = Column(DATETIME, default=datetime.now)
    __table_args__ = (PrimaryKeyConstraint(id),)

    def to_dict(self):
        return dict([(k, getattr(self, k)) for k in self.__dict__.keys() if not k.startswith("_")])

    def __repr__(self):
        return f'User {self.id}'


class Dialog_resources(Base):
    __tablename__ = "dialog_res"

    id = Column(INTEGER, primary_key=True)
    res = Column(TEXT)

    def __repr__(self):
        return f'Res {self.id} - {self.res}'


class States(Base):
    __tablename__ = "states"

    id = Column(INTEGER, autoincrement=True, primary_key=True, index=True)
    user_id = Column(TEXT)
    state = Column(TEXT)
    vars = Column(TEXT)

    def to_dict(self):
        return dict([(k, getattr(self, k)) for k in self.__dict__.keys() if not k.startswith("_")])