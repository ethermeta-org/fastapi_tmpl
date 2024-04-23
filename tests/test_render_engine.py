from unittest import TestCase

from app.utils.render_engine import render_new_service_file_content, render_new_proxy_file_content
from app.service_api.schema import OMESServiceDefItem, OMESProxyDefItem


class TestUtilsRender(TestCase):
    def test_render_new_service(self):
        t = OMESServiceDefItem(customer_code='13123', version="1.0")
        text = render_new_service_file_content(t)
        self.fail()

    def test_render_new_proxy(self):
        t = OMESProxyDefItem(customer_code='13123')
        text = render_new_proxy_file_content(t)
        self.fail()
