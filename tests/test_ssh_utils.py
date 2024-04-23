from unittest import TestCase

from app.service_api.schemas import OMESProxyDefItem
from app.utils.ssh_utils import create_transfer_proxy_service_config


class Test(TestCase):
    def test_create_transfer_proxy_service_config(self):
        from config import settings
        item = OMESProxyDefItem(customer_code='111', is_remote_mode=True)
        create_transfer_proxy_service_config(item, settings)
        self.fail()
