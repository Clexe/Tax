"""
SQLAlchemy 2.0 database models for NaijaTax Bot.

Uses the new DeclarativeBase / Mapped / mapped_column API (SQLAlchemy 2.0+).
"""

from __future__ import annotations
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Stores per-user metadata for NaijaTax Bot.

    Primary key is the Telegram user ID (BigInteger — Telegram IDs exceed 32-bit range).
    Language preference is stored here for persistence across bot restarts.
    """

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language_preference: Mapped[str] = mapped_column(String(10), default="en")
    first_seen: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    total_calculations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    logs: Mapped[list[CalculationLog]] = relationship(
        "CalculationLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.telegram_id} lang={self.language_preference}>"


class CalculationLog(Base):
    """
    Stores aggregated results of each tax calculation.

    Only aggregated totals are stored — no individual salary components
    to respect user privacy.

    calculation_type: "salaried", "selfemployed", or "checker"
    """

    __tablename__ = "calculation_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False
    )
    calculation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    gross_annual: Mapped[float] = mapped_column(Float, nullable=False)
    chargeable_income: Mapped[float] = mapped_column(Float, nullable=False)
    annual_tax: Mapped[float] = mapped_column(Float, nullable=False)
    effective_rate: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="logs")

    def __repr__(self) -> str:
        return (
            f"<CalculationLog id={self.id} user={self.telegram_id} "
            f"type={self.calculation_type} tax={self.annual_tax}>"
        )
