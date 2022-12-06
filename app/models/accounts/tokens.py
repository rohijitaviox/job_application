from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.base_class import Base,TimeStamp


class OutstandingToken(Base,TimeStamp):
    id = Column(Integer, primary_key=True)
    jti = Column(UUID, nullable=False)  # index
    token_type = Column(String(7), nullable=False)
    expire_at = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="tokens")  # index

    __table_args__ = (Index("outstandingtoken_user_token_index","user_id","jti"),)

    def __repr__(self) -> str:
        return f"{self.user_id}_{self.jti}"
