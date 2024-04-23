import inspect
import logging
import os
import signal
import sys
from functools import partial
from http import HTTPStatus

import click
import sqlalchemy
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException
from gunicorn.app.base import BaseApplication
from gunicorn.arbiter import Arbiter
from gunicorn.glogging import Logger
from loguru import logger
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request
from starlette.responses import JSONResponse

from release import PROJECT_NAME
from app.common_api.api import api_router as common_api_router
from app.database import get_database_url, get_database, create_engine
from app.schema import AnyLinkerErrorWebResponse, AnyLinkerErrorResponse
from app.service_api.api import api_router as service_api_router
from app.service_api.crud import crud_create_work_node
from config import settings
from constants import API_V1_STR, API_SERVICE_PREFIX
from utils import is_dev_environment

LOG_FORMAT = "<r>{time}</r>: <lvl>{level}</lvl> <g>{message}</g>"

logger.remove(handler_id=None)  # 清除所有原有配置

ENV_SERVICE_FASTAPI_HTTP_PORT = int(os.getenv('ENV_SERVICE_FASTAPI_HTTP_PORT', '9000'))


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def modify_default_logger_handler(handler_name: str, is_debug_lvl: bool) -> None:
    _logger = logging.getLogger(handler_name)
    intercept_handler = InterceptHandler()
    _logger.handlers.clear()
    _logger.addHandler(intercept_handler)
    if is_debug_lvl and is_dev_environment():
        _logger.setLevel(logging.DEBUG)


def set_log_handler():
    l = ["sqlalchemy.engine", "sqlalchemy.pool"]
    for handler in l:
        modify_default_logger_handler(handler, True)


async def set_uvicorn_log_handler():
    l = ["uvicorn", "uvicorn.access", "uvicorn.error"]
    for handler in l:
        modify_default_logger_handler(handler, True)


middlewares = []

extra_app_config = {}


async def http_exception(request: Request, exc: Exception):
    msg = str(exc)
    logger.error(msg)
    url_path = request.url.path
    r = AnyLinkerErrorWebResponse(
        error=AnyLinkerErrorResponse(message=msg, target=url_path)
    )
    return JSONResponse(content=r.model_dump(), status_code=HTTPStatus.BAD_REQUEST)


exception_handlers = {
    HTTPException: http_exception,
}


async def add_config(app: FastAPI, setting):
    app.config = setting


# 数据库连接
async def database_connect(app: FastAPI, database_url: str, with_demo: bool = False) -> None:
    logger.info("Database Connecting!!!")
    from app.db.models import DeclarativeBase
    engine = create_engine(database_url)

    DeclarativeBase.metadata.create_all(engine)  # 创建模型
    database = get_database(database_url)
    app.state.db = database
    await database.connect()
    logger.info("Database Connection Established")
    if with_demo:
        logger.info('加载测试数据')
        from app.database import SessionLocal
        session = SessionLocal
        with open('demo/worknode_data.yaml', 'r') as f:
            data = yaml.safe_load(f)
            for node in data:
                with session() as db:
                    crud_create_work_node(db, **node)


async def database_disconnect(app: FastAPI):
    database = app.state.db
    if database:
        await database.disconnect()
    logger.info("Database Disconnected")


app = FastAPI(
    title=release.PROJECT_NAME,
    docs_url="/app/docs",
    redoc_url="/app/redoc",
    openapi_url=f"/app/openapi.json",
    description=release.DESC,
    summary=release.DESC,
    version=release.VERSION,
    terms_of_service="https://www.anylinker.com/terms/",
    middleware=middlewares,
    on_startup=[set_uvicorn_log_handler],
    # on_shutdown=[database_disconnect],
    exception_handlers=exception_handlers,
    **extra_app_config,
)

app.include_router(common_api_router, prefix=API_V1_STR)
app.include_router(service_api_router, prefix=API_SERVICE_PREFIX)


class CustomLogger(Logger):
    def __init__(self, cfg):
        super(CustomLogger, self).__init__(cfg)
        self.access_log = logger


class GunicornApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.engine = None
        self.options = options or {}
        self.application = app
        self.engine: Arbiter
        super().__init__()

    def load_config(self):
        c = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in c.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    def run(self):
        try:
            self.engine = Arbiter(self)
            self.engine.run()
        except RuntimeError as e:
            print("\nError: %s\n" % e, file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)

    def shutdown(self):
        self.engine.signal(signal.SIGINT, None)


def set_customer_logger():
    if is_dev_environment():
        logger.add(sys.stdout, format=LOG_FORMAT, level="DEBUG")
    else:
        logger.add(
            f'/etc/anylinker/logs/{PROJECT_NAME}.log',
            rotation="12:00",  # 每天凌晨归档
            level="INFO",
            retention="30 days",
            encoding="utf-8",
            format=LOG_FORMAT,
            enqueue=True,
        )  # 文件日志
    # 重载logger


@click.command()
@click.option("--config", default='config.yaml', type=click.Path(exists=True), envvar='ENV_ANYLINKER_CONFIG_FILE',
              help="Config File Path")
@click.option("--port", default=9010, help="Server Port")
@click.option("--demo", default=False, envvar='ENV_ANYLINKER_WITH_DEMO', help="With Demo Data")
@click.option("--db_host", default=settings.DATABASE.HOST, help="Database Host")
@click.option("--db_port", default=settings.DATABASE.PORT, help="Database Port")
@click.option("--db_user", default=settings.DATABASE.USER, help="Database User Name")
@click.option("--db_password", default=settings.DATABASE.PASSWORD, help="Database User Password")
@click.option("--db_name", default=settings.DATABASE.NAME, help="Database name")
def main(config: str, port: int, demo: bool, db_host: str, db_port: int, db_user: str, db_password: str, db_name: str):
    set_customer_logger()
    set_log_handler()
    logger.info(f'系统启动: {db_host}, {db_port}, {db_user}, {db_name}')
    if config != 'config.yaml':
        if os.path.exists(config):
            logger.info(f'从{config}文件读取配置文件')
            settings.load_file(path=config)  # 重新读取配置文件
        else:
            logger.error(f'{config}配置文件不存在,从默认配置文件: {os.getcwd()}/config.yaml 启动!!!')
    settings.update(
        {'database.host': db_host, 'database.port': db_port, 'database.user': db_user, 'database.password': db_password,
         'database.name': db_name})
    database_url = get_database_url(user=settings.DATABASE.USER, database=settings.DATABASE.NAME,
                                    host=settings.DATABASE.HOST, port=settings.DATABASE.PORT,
                                    password=settings.DATABASE.PASSWORD)
    database_onconnect = partial(database_connect, app=app, database_url=database_url, with_demo=demo)
    app.add_event_handler('startup', database_onconnect)
    database_ondisconnect = partial(database_disconnect, app=app)
    app.add_event_handler('shutdown', database_ondisconnect)
    add_config_on_startup = partial(add_config, app=app, setting=settings)
    app.add_event_handler('startup', add_config_on_startup)
    if is_dev_environment():
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=port,
            log_level="debug",
        )
    else:
        options = {
            "bind": "%s:%s" % ("0.0.0.0", port),
            "daemon": True,
            "check_config": True,
            "proc_name": PROJECT_NAME,
            "timeout": 20,
            "graceful_timeout": 15,
            "keepalive": 40,
            "workers": 4,
            "worker_class": "uvicorn.workers.UvicornWorker",
            "accesslog": "-",  # 必须启用才有access log
            "access_log_format": '%a %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"',
            "logger_class": CustomLogger,
        }
        _gunicorn_app = GunicornApplication(app, options)
        _gunicorn_app.run()


if __name__ == "__main__":
    main()
