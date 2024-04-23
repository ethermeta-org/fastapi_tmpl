from http import HTTPStatus
from typing import Union

from dynaconf import Dynaconf
from fastapi import APIRouter, Header, Depends, HTTPException, BackgroundTasks

from app.db import models
from app.exception import AnyLinkerException
from app.service_api import schemas
from sqlalchemy.orm import Session

from app.depends import get_db, get_config
from app.service_api.crud import crud_create_service, crud_get_work_node
from app.service_api.schemas import OMESProxyDefItem
from app.utils.docker_utils import create_oemes_docker_container, EVN_DOCKER_URL
from app.utils.ssh_utils import create_transfer_proxy_service_config
from utils import is_dev_environment

router = APIRouter()


@router.post("/oemes", status_code=HTTPStatus.CREATED.value, response_model=schemas.OMESServiceItem)
async def do_create_oemes_service(
        service_item: schemas.OMESServiceDefItemCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        config: Dynaconf = Depends(get_config),
        x_org_name: Union[str, None] = Header(default=None, example="anylinker"),
) -> models.OeMesService:
    try:
        d = crud_create_service(db, service_item)
        node = crud_get_work_node(db, service_item.node)
        proxy_item = OMESProxyDefItem(customer_code=service_item.customer_code, is_remote_mode=True)
        create_transfer_proxy_service_config(proxy_item, config)
        endpoint = EVN_DOCKER_URL
        if node and not is_dev_environment():
            endpoint = node.endpoint
        background_tasks.add_task(create_oemes_docker_container, endpoint, service_item)
        db.commit()
        db.refresh(d)
    except Exception as e:
        raise AnyLinkerException(detail=str(e))
    return d
