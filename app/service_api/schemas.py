from pydantic import BaseModel, field_validator

from app.service_api.constants import SUPPORT_VERSIONS


class OMESServiceCommonDefItem(BaseModel):
    customer_code: str = ""

    @field_validator('customer_code', mode='before')
    @classmethod
    def validate_customer_code(cls, customer_code):
        if not customer_code:
            raise ValueError('Customer code Is Required')
        return customer_code.strip()


class OMESServiceDefItemCreate(OMESServiceCommonDefItem):
    version: str = "latest"
    is_demo: bool = True
    node: str = 'Node1'  # 工作节点
    service_port: int = 8069  # 端口

    @field_validator('version', mode='before')
    @classmethod
    def validate_version_support(cls, version):
        if version not in SUPPORT_VERSIONS:
            raise ValueError(f'{version} Is Not Supported, Please Check Support Versions In {SUPPORT_VERSIONS}')
        return version.strip()


class OMESServiceItem(OMESServiceDefItemCreate):
    id: int
    service_url: str

    class Config:
        from_attributes = True


class OMESProxyDefItem(OMESServiceCommonDefItem):
    is_remote_mode: bool = False
    remote_host_name: str = 'host.docker.internal'
