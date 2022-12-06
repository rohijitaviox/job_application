from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import (
    Column,
    DateTime,
    func
)


@as_declarative()
class Base:
    id: Any
    __name__: str
    # Generate __tablename__ automatically

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimeStamp(object):
    created = Column(DateTime, server_default=func.now())
    modified = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())
