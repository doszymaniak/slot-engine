from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from os import getenv

DATABASE_URL = getenv("DATABASE_URL", "sqlite:///app.db")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()