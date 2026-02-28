"""
Alembic environment configuration for NaijaTax Bot.

Runs migrations in 'online' mode (connected to a live database).
The database URL is read from the alembic config, which is set at runtime
by bot/database/db.py::run_migrations() before this module is invoked.
"""

from __future__ import annotations
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import our models so Alembic can detect schema changes
from bot.database.models import Base

# Alembic Config object — access to values in alembic.ini
config = context.config

# Allow overriding the URL via DATABASE_URL environment variable
# (used when running alembic CLI commands directly from the shell)
db_url = os.environ.get("DATABASE_URL")
if db_url:
    if db_url.startswith("postgres://"):
        db_url = "postgresql://" + db_url[len("postgres://"):]
    config.set_main_option("sqlalchemy.url", db_url)

# Configure logging from alembic.ini if a logging section exists
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        pass

# The target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Configures the context with a URL only (no Engine required).
    Useful for generating migration scripts without a live DB.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode (default).

    Creates an Engine and runs migrations against a live database connection.
    This is what gets called at bot startup via db.run_migrations().
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
