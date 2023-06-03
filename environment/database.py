from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from environment.config import DATABASE_URL


engine = create_engine(DATABASE_URL, connect_args={
    "check_same_thread": False
}, echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)



