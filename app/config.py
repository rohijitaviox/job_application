import os


SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = bool(os.environ.get("DEBUG", 0))

PUBLIC_ENC_KEY = os.environ["PUBLIC_ENC_KEY"]
PRIVATE_ENC_KEY = os.environ["PRIVATE_ENC_KEY"]
ALGORITHM = os.environ.get("ALGORITHM", "RS256")

ACCESS_TOKEN_EXPIRES_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRES_MINUTES"])
REFRESH_TOKEN_EXPIRES_DAYS = int(
    os.environ["REFRESH_TOKEN_EXPIRES_DAYS"])
ROTATE_REFRESH_TOKENS = bool(int(os.environ.get("ROTATE_REFRESH_TOKENS", 0)))
AUTHENTICATE_FROM_DB = bool(int(os.environ.get("AUTHENTICATE_FROM_DB", 0)))

DB_DIALECT = os.environ.get("DB_DIALECT", "postgresql")
DB_DRIVER = os.environ.get("DB_DRIVER", "asyncpg")
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]

auth_jwt_config = {
    "ACCESS_TOKEN_EXPIRES_MINUTES": ACCESS_TOKEN_EXPIRES_MINUTES,
    "REFRESH_TOKEN_EXPIRES_DAYS": REFRESH_TOKEN_EXPIRES_DAYS,
    "PUBLIC_ENC_KEY": PUBLIC_ENC_KEY,
    "PRIVATE_ENC_KEY": PRIVATE_ENC_KEY
}
