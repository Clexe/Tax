"""
Database session factory and helper functions for NaijaTax Bot.

Uses synchronous SQLAlchemy with psycopg2 (PostgreSQL) or SQLite (local dev).
Async handlers must call these via: await asyncio.to_thread(db_func, args...)

Railway injects DATABASE_URL as "postgresql://..." — SQLAlchemy needs
"postgresql://" (not "postgres://") so we fix it here.
"""

from __future__ import annotations
import os
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Generator

from sqlalchemy import create_engine, select, func, text
from sqlalchemy.orm import Session, sessionmaker

from bot.database.models import Base, User, CalculationLog

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """
    Read DATABASE_URL from environment.
    Rewrites "postgres://" → "postgresql://" for Railway compatibility.
    Falls back to SQLite for local development when DATABASE_URL is not set.
    """
    url = os.environ.get("DATABASE_URL", "sqlite:///naijatax_local.db")
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def _create_engine_from_env():
    url = get_database_url()
    if url.startswith("sqlite"):
        # SQLite doesn't support pool_pre_ping the same way, use connect_args
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10)


engine = _create_engine_from_env()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def run_migrations() -> None:
    """
    Run Alembic migrations to upgrade the schema to 'head'.
    Called once at bot startup in main.py before the bot starts.
    """
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", get_database_url())
    try:
        command.upgrade(cfg, "head")
        logger.info("Database migrations applied successfully.")
    except Exception as e:
        logger.error("Migration failed: %s", e)
        raise


# ------------------------------------------------------------------ #
# User management                                                       #
# ------------------------------------------------------------------ #

def upsert_user(telegram_id: int, username: str | None) -> None:
    """
    Insert a new user or update last_active for an existing user.
    Called on every /start and every significant interaction.
    """
    with get_db() as session:
        user = session.get(User, telegram_id)
        now = datetime.utcnow()
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_seen=now,
                last_active=now,
            )
            session.add(user)
            logger.info("New user registered: %d", telegram_id)
        else:
            user.last_active = now
            if username is not None:
                user.username = username


def get_language(telegram_id: int) -> str:
    """Return the user's stored language preference, defaulting to 'en'."""
    with get_db() as session:
        user = session.get(User, telegram_id)
        if user is None:
            return "en"
        return user.language_preference


def set_language(telegram_id: int, lang: str) -> None:
    """Update the user's language preference in the database."""
    with get_db() as session:
        user = session.get(User, telegram_id)
        if user is not None:
            user.language_preference = lang
            user.last_active = datetime.utcnow()


# ------------------------------------------------------------------ #
# Calculation logging                                                   #
# ------------------------------------------------------------------ #

def log_calculation(
    telegram_id: int,
    calc_type: str,
    gross_annual: float,
    chargeable_income: float,
    annual_tax: float,
    effective_rate: float,
) -> None:
    """
    Log a completed tax calculation and increment the user's counter.

    Args:
        telegram_id: Telegram user ID.
        calc_type: One of "salaried", "selfemployed", "checker".
        gross_annual: Gross annual income.
        chargeable_income: Chargeable income after deductions.
        annual_tax: Annual tax payable.
        effective_rate: Effective tax rate (as percentage, e.g. 10.48).
    """
    with get_db() as session:
        log = CalculationLog(
            telegram_id=telegram_id,
            calculation_type=calc_type,
            gross_annual=gross_annual,
            chargeable_income=chargeable_income,
            annual_tax=annual_tax,
            effective_rate=effective_rate,
            created_at=datetime.utcnow(),
        )
        session.add(log)

        user = session.get(User, telegram_id)
        if user is not None:
            user.total_calculations += 1
            user.last_active = datetime.utcnow()


# ------------------------------------------------------------------ #
# Admin statistics                                                      #
# ------------------------------------------------------------------ #

def get_admin_stats() -> dict:
    """
    Return aggregated statistics for the /admin command.

    Returns:
        dict with keys: total_users, calcs_today, calcs_week, calcs_all,
                        most_used_flow.
    """
    with get_db() as session:
        total_users: int = session.scalar(
            select(func.count()).select_from(User)
        ) or 0

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)

        calcs_today: int = session.scalar(
            select(func.count())
            .select_from(CalculationLog)
            .where(CalculationLog.created_at >= today_start)
        ) or 0

        calcs_week: int = session.scalar(
            select(func.count())
            .select_from(CalculationLog)
            .where(CalculationLog.created_at >= week_start)
        ) or 0

        calcs_all: int = session.scalar(
            select(func.count()).select_from(CalculationLog)
        ) or 0

        most_used_flow: str | None = session.scalar(
            select(CalculationLog.calculation_type)
            .group_by(CalculationLog.calculation_type)
            .order_by(func.count(CalculationLog.id).desc())
            .limit(1)
        )

        return {
            "total_users": total_users,
            "calcs_today": calcs_today,
            "calcs_week": calcs_week,
            "calcs_all": calcs_all,
            "most_used_flow": most_used_flow or "N/A",
        }
