from starlette.requests import Request
from dynaconf import Dynaconf


def get_db():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_config(request: Request) -> Dynaconf:
    return request.app.config
