import databases
import sqlalchemy
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

engine = None
SessionLocal = None


def get_database(database_url: str) -> databases.Database:
    database = databases.Database(database_url, min_size=5, max_size=25)
    return database


def get_database_url(user: str, database: str, host: str, port: int, password: str) -> str:
    # SQLAlchemy specific code, as with any other app
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return DATABASE_URL


def create_engine(database_url: str) -> Engine:
    global SessionLocal
    pool_params = {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
        "pool_recycle": 1800,  # 15分钟
        "pool_pre_ping": True,
        "echo_pool": True
    }
    engine = sqlalchemy.create_engine(database_url, **pool_params)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine
