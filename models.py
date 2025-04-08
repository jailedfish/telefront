from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, declarative_base
from os import environ as env
from dotenv import load_dotenv
load_dotenv()
eng = create_engine(env.get('POSTGRES_URL'))
session = sessionmaker(bind=eng)()

class Base(declarative_base()):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

class User(Base):
    __tablename__ = 'user'

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
