from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from db.base_class import Base, TimeStamp


class User(Base, TimeStamp):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    active = Column(Boolean, default=False)
    tokens = relationship("OutstandingTokens",
                          back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"{self.email_id}"
