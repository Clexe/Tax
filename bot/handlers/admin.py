"""
Admin command handler for NaijaTax Bot.

/admin is restricted to ADMIN_TELEGRAM_ID from the environment.
All other users are silently ignored.

Shows:
  - Total registered users
  - Calculations today / this week / all time
  - Most used flow (salaried/selfemployed/checker)
  - Bot uptime
"""

from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import ContextTypes

from bot.database import db

logger = logging.getLogger(__name__)

# Module-level start time — set when this module is first imported.
# This gives the uptime from when the bot started (handlers imported = bot starting).
BOT_START_TIME: datetime = datetime.now(tz=timezone.utc)


def _get_admin_id() -> int:
    """Return the configured admin Telegram ID, or 0 if not set."""
    try:
        return int(os.environ.get("ADMIN_TELEGRAM_ID", "0"))
    except (ValueError, TypeError):
        return 0


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /admin command.

    Silently ignores non-admin users (returns without response).
    Shows statistics panel to the admin.
    """
    if update.effective_user is None or update.message is None:
        return

    admin_id = _get_admin_id()
    if admin_id == 0 or update.effective_user.id != admin_id:
        # Silently ignore — do not reveal that this command exists
        return

    try:
        stats = await asyncio.to_thread(db.get_admin_stats)

        now = datetime.now(tz=timezone.utc)
        uptime = now - BOT_START_TIME
        total_seconds = int(uptime.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes = remainder // 60

        uptime_str = ""
        if days > 0:
            uptime_str += f"{days}d "
        uptime_str += f"{hours}h {minutes}m"

        text = (
            "📊 <b>NaijaTax Bot — Admin Dashboard</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 <b>Total Users:</b> {stats['total_users']:,}\n\n"
            f"📈 <b>Calculations</b>\n"
            f"   Today:     {stats['calcs_today']:,}\n"
            f"   This week: {stats['calcs_week']:,}\n"
            f"   All time:  {stats['calcs_all']:,}\n\n"
            f"🔝 <b>Most Used Flow:</b> {stats['most_used_flow']}\n\n"
            f"⏱️ <b>Bot Uptime:</b> {uptime_str}\n"
            f"🕐 <b>Started:</b> {BOT_START_TIME.strftime('%Y-%m-%d %H:%M UTC')}"
        )

        await update.message.reply_html(text)

    except Exception as e:
        logger.error("Error in admin_command: %s", e, exc_info=True)
        await update.message.reply_text("Error fetching admin stats.")
