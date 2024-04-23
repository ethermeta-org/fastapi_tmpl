from loguru import logger
from sqlalchemy.orm import Session
from app.db import models
from app.service_api import schemas
from constants import SAAS_DOMAIN_NAME
from sqlalchemy.dialects.postgresql import insert


def crud_create_service(db: Session, service: schemas.OMESServiceDefItemCreate) -> models.OeMesService:
    db_service = models.OeMesService(customer_code=service.customer_code, version=service.version, node=service.node,
                                     service_port=service.service_port, is_demo=service.is_demo)
    db_service.service_url = f'https://{service.customer_code}.{SAAS_DOMAIN_NAME}'
    db.add(db_service)
    return db_service


def crud_get_work_node(db: Session, node_name: str) -> models.WorkNodes:
    return db.query(models.WorkNodes).filter(models.WorkNodes.name == node_name).first()


def crud_create_work_node(db: Session, **kwargs) -> models.WorkNodes:
    node = models.WorkNodes(**kwargs)
    try:
        db.add(node)
        db.commit()
        db.refresh(node)
    except Exception as e:
        logger.error(e)
    return node
