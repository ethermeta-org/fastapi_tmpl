from typing import Union

from jinja2 import PackageLoader, Environment, select_autoescape
from loguru import logger

from app.service_api.schemas import OMESServiceDefItemCreate, OMESProxyDefItem

DOCKER_COMPOSE_TMPL_FILE = 'docker-compose.yaml.jinja'

SERVICE_EXPORT_TMPL_FILE = 'service_export_traefik.yaml.jinja'

loader = PackageLoader('app', 'templates')

env = Environment(
    loader=loader,
    autoescape=select_autoescape()
)


def render_file_content(item: Union[OMESServiceDefItemCreate, OMESProxyDefItem], tmpl_file: str) -> str:
    text = ''
    if not tmpl_file:
        logger.error('未提供模版文件名称, 请确认')
        return text
    try:
        template = env.get_template(tmpl_file)
        d = item.model_dump()
        text = template.render(item=d)
    except Exception as e:
        logger.error(e)
    finally:
        return text


def render_new_service_file_content(item: OMESServiceDefItemCreate) -> str:
    return render_file_content(item, DOCKER_COMPOSE_TMPL_FILE)


def render_new_proxy_file_content(item: OMESProxyDefItem) -> str:
    return render_file_content(item, SERVICE_EXPORT_TMPL_FILE)
