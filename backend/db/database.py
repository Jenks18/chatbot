from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Allow a safe local SQLite fallback for development to avoid requiring
# system-level Postgres build dependencies (libpq / OpenSSL) during local dev.
# This will not affect production if DATABASE_URL is explicitly set to a
# production Postgres URL. To enable locally set DEV_SQLITE=1 in your .env
# or export it in your shell. Alternatively, set DATABASE_URL to a sqlite
# URI (starts with "sqlite:").
USE_DEV_SQLITE = os.getenv("DEV_SQLITE", "0").lower() in ("1", "true", "yes")
env_db_url = os.getenv("DATABASE_URL")

sqlite_path = os.path.join(os.path.dirname(__file__), "../dev-data.sqlite")
sqlite_url = f"sqlite:///{os.path.abspath(sqlite_path)}"

# Choose DB URL according to explicit dev flag or explicit DATABASE_URL.
# Priority (local dev): if DEV_SQLITE is enabled we force the sqlite_url to
# avoid touching production Postgres URLs. If DATABASE_URL is explicitly set
# to a sqlite URI then we also respect that. Otherwise fall back to
# the provided DATABASE_URL or the default Postgres URI.
if USE_DEV_SQLITE:
    DATABASE_URL = sqlite_url
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif env_db_url and env_db_url.startswith("sqlite"):
    DATABASE_URL = env_db_url
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = env_db_url or "postgresql://toxgpt_user:toxgpt_pass_2025@localhost:5432/toxicology_gpt"
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
