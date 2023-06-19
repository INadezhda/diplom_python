import sqlalchemy as sq
import requests
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.orm import declarative_base, relationship


with open('config.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    name_bd = lines[5].rstrip()
    login = lines[7].rstrip()
    parol = lines[9].rstrip()

DSN = f'postgresql://{login}:{parol}@localhost:5432/{name_bd}'
engine = sq.create_engine(DSN)
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id_vk = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, unique=True, primary_key=True)

    def __str__(self):
        return f'{self.id_vk}'


def Create_tables():
    engine = sq.create_engine(DSN)
    Base.metadata.create_all(engine)


def find_user_vk(user_id):
    engine = sq.create_engine(DSN)
    with Session(engine) as session:
        find_bd = session.query(User).filter(User.id_vk == user_id).all()
        for i in find_bd:
            return i


def count_offset():
    engine = sq.create_engine(DSN)
    with Session(engine) as session:
        count_offset = session.query(User).count()
        return count_offset


def add_user_vk(user_id):
    engine = sq.create_engine(DSN)
    with Session(engine) as session:
        count_user = session.query(User.id).count()
        add_user = User(id_vk=user_id, id=count_user + 1)
        session.add(add_user)
        session.commit()
