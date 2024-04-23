import os
import tempfile
from typing import Optional

from dynaconf import Dynaconf
from loguru import logger
from pssh.clients import SSHClient

from app.service_api.schemas import OMESProxyDefItem
from app.utils.render_engine import render_new_proxy_file_content
from constants import TRAEFIK_PROXY_CONF_ROOT_PATH


class SSHUtils:
    def __init__(self, ip: str, port: int = 22, username: str = 'root', password: str = ''):
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password
        self._client: Optional[SSHClient] = None

    def __enter__(self) -> 'SSHUtils':
        if not self._client:
            client = SSHClient(self._ip, user=self._username, password=self._password, port=self._port)
            self._client = client
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client is not None:
            self._client.disconnect()
            self._client = None

    def run_command(self, command, sudo=False, user=None,
                    use_pty=False, shell=None,
                    encoding='utf-8', timeout=None, read_timeout=None):
        if not self._client:
            return None
        return self._client.run_command(command, sudo=sudo, user=user, use_pty=use_pty, shell=shell, encoding=encoding,
                                        timeout=timeout, read_timeout=read_timeout)

    def scp_send(self, local_file, remote_file, recurse=False, sftp=None):
        if not self._client:
            return None
        return self._client.scp_send(local_file=local_file, remote_file=remote_file, recurse=recurse, sftp=sftp)

