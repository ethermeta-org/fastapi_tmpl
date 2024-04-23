from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class WorkNodes(DeclarativeBase):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    endpoint = Column(String(128), nullable=False)


class OeMesService(DeclarativeBase):
    __tablename__ = "services"
    __table_args__ = (
        UniqueConstraint("node", "service_port"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    node = Column(String(64), index=True, nullable=False)  # 所在的节点
    service_port = Column(Integer, nullable=False)
    customer_code = Column(String(64), unique=True, nullable=False)
    service_url = Column(String(255), unique=True, nullable=False)
    version = Column(String(32), default='latest', nullable=False)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return "{}".format(self.__tablename__)
