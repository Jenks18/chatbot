from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Only load .env if it exists (local dev), skip on serverless
try:
    load_dotenv()
except:
    pass

# Check if we have PostgreSQL support
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    print("⚠️  psycopg2 not available - PostgreSQL support disabled")

# Allow a safe local SQLite fallback for development to avoid requiring
# system-level Postgres build dependencies (libpq / OpenSSL) during local dev.
# This will not affect production if DATABASE_URL is explicitly set to a
# production Postgres URL. To enable locally set DEV_SQLITE=1 in your .env
# or export it in your shell. Alternatively, set DATABASE_URL to a sqlite
# URI (starts with "sqlite:").
USE_DEV_SQLITE = os.getenv("DEV_SQLITE", "0").lower() in ("1", "true", "yes")
env_db_url = os.getenv("DATABASE_URL")

# Vercel Postgres uses postgres:// but SQLAlchemy needs postgresql://
if env_db_url and env_db_url.startswith("postgres://"):
    env_db_url = env_db_url.replace("postgres://", "postgresql://", 1)

sqlite_path = os.path.join(os.path.dirname(__file__), "../dev-data.sqlite")
sqlite_url = f"sqlite:///{os.path.abspath(sqlite_path)}"

# Choose DB URL according to explicit dev flag or explicit DATABASE_URL.
# If psycopg2 is not available and we're trying to use postgres, fall back to SQLite
if USE_DEV_SQLITE:
    DATABASE_URL = sqlite_url
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif env_db_url and env_db_url.startswith("sqlite"):
    DATABASE_URL = env_db_url
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif env_db_url and env_db_url.startswith("postgresql") and not HAS_POSTGRES:
    # PostgreSQL URL but no psycopg2 - use in-memory SQLite
    print("⚠️  PostgreSQL requested but psycopg2 not available - using in-memory SQLite")
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = env_db_url or "postgresql://toxgpt_user:toxgpt_pass_2025@localhost:5432/toxicology_gpt"
    # Add pool_pre_ping for serverless environments to handle stale connections
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 5}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
