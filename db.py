from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuration - change these if your MySQL user/host/db differ
DB_USER = "root"
DB_PASSWORD = ""  # empty password
DB_HOST = "localhost"
DB_NAME = "fastapi_db"

# Try to create the database if it doesn't exist (use root connection without DB)
ROOT_DATABASE_URL = f"mysql+pymysql://{DB_USER}{(':' + DB_PASSWORD) if DB_PASSWORD else ''}@{DB_HOST}/"
try:
    root_engine = create_engine(ROOT_DATABASE_URL, future=True)
    with root_engine.connect() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.commit()
    root_engine.dispose()
except Exception:
    # If creation fails (e.g., server not running or permission denied), we'll
    # let the regular engine connection raise a clear error later.
    pass

DATABASE_URL = f"mysql+pymysql://{DB_USER}{(':' + DB_PASSWORD) if DB_PASSWORD else ''}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    # Import models so they are registered with Base before creating tables
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
