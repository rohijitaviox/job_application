from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import SessionLocal


def get_db() -> AsyncSession:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
