import os
import pprint
import tempfile
from typing import Optional

import docker
from loguru import logger

from app.exception import AnyLinkerException
from app.service_api import schemas
from constants import OEMES_IMAGE_NAME

EVN_DOCKER_URL = os.getenv('EVN_DOCKER_URL', 'unix://var/run/docker.sock')


class DockerUtils(object):

    def __init__(self, url: str, clean_session: bool = False):
        self._url = url
        self._client: Optional[docker.DockerClient] = None
        self._clean_session = clean_session

    def __enter__(self) -> 'DockerUtils':
        if not self._client:
            client = docker.DockerClient(base_url=self._url)
            self._client = client
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client is not None and self._clean_session:
            self._client.close()
            self._client = None

    def run_container(self, name: str, image_name: str, **kwargs):
        logger.info(f'尝试启动容器: {name} Image: {image_name}')
        logger.debug(
            f'尝试启动容器: {name} Image: {image_name}, kwargs: {pprint.pprint(kwargs, indent=4)}')

        if not self._client:
            raise RuntimeError(f'请先初始化Docker客户端: {self._url}')

        kwargs.update({'name': name, 'detach': True, 'auto_remove': True})

        return self._client.containers.run(image=image_name, **kwargs)


def create_oemes_docker_container(base_url: str = EVN_DOCKER_URL,
                                  service: Optional[schemas.OMESServiceDefItemCreate] = None):
    if not service:
        err_msg = '未定义需要启动的服务,请检查'
        raise AnyLinkerException(detail=err_msg)
    with docker.DockerClient(base_url=base_url) as client:
        service_name = f'{service.customer_code}_oemes_service'
        image_name = f"{OEMES_IMAGE_NAME}:{service.version or 'latest'}"
        kwargs = {
            'extra_hosts': {'host.docker.internal': 'host-gateway'},
            'cpu_period': 100000,
            'cpu_quota': 70000 if service.is_demo else 200000,  # demo模式下最多70%一个核心, 否则最多可使用2个核心 = 200%
            'mem_limit': '500m' if service.is_demo else '1g',
            'mem_reservation': '256m',
            'ports': {service.service_port or 8069: 8069}
        }
        try:
            client.run_container(name=service_name, image=image_name, **kwargs)
            logger.info(f'容器{service_name}已启动!')
        except Exception as e:
            raise AnyLinkerException(detail=str(e))
