"""
Help & FAQs handler for NaijaTax Bot.

Not a ConversationHandler — uses stateless CallbackQueryHandlers.
Each help topic returns a detailed explanation with a back button.
"""

from __future__ import annotations
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.keyboards import (
    HELP_CHARGEABLE,
    HELP_NRS,
    HELP_PAYE,
    HELP_PAY_TAX,
    HELP_NONREMITTANCE,
    HELP_RENT_RELIEF,
    HELP_WHY_ZERO,
    back_to_help_keyboard,
    help_menu_keyboard,
)
from bot.utils.messages import get_msg

logger = logging.getLogger(__name__)

# Map callback data → message key
TOPIC_MAP: dict[str, str] = {
    HELP_PAYE: "help_paye_text",
    HELP_CHARGEABLE: "help_chargeable_text",
    HELP_RENT_RELIEF: "help_rent_relief_text",
    HELP_WHY_ZERO: "help_why_zero_text",
    HELP_PAY_TAX: "help_pay_tax_text",
    HELP_NONREMITTANCE: "help_nonremittance_text",
    HELP_NRS: "help_nrs_text",
}


async def help_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu_help callback — show help topics keyboard."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    lang = context.user_data.get("lang", "en")
    try:
        await query.edit_message_text(
            get_msg("help_menu", lang),
            parse_mode="HTML",
            reply_markup=help_menu_keyboard(lang),
        )
    except Exception as e:
        logger.error(
            "Error in help_entry user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
        )


async def help_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle all help topic callbacks (help_paye, help_cra, etc.).
    Routes to the correct message key and shows a back button.
    """
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    lang = context.user_data.get("lang", "en")
    topic_key = query.data  # e.g. "help_paye"

    msg_key = TOPIC_MAP.get(topic_key, "help_menu")
    text = get_msg(msg_key, lang)

    try:
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=back_to_help_keyboard(lang),
            disable_web_page_preview=True,
        )
    except Exception as e:
        logger.error(
            "Error in help_topic user=%s topic=%s: %s",
            getattr(query.from_user, "id", "?"),
            topic_key,
            e,
        )
