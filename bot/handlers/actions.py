"""
Post-result action button handlers for NaijaTax Bot.

These are global CallbackQueryHandlers registered outside ConversationHandlers.
They access context.user_data["last_result"] which was stored before
ConversationHandler.END in the salaried/selfemployed/checker flows.

Buttons:
    result_reduce  — How to reduce your tax under NTA 2025
    result_explain — Step-by-step walkthrough of the result
    result_again   — Clear session and return to main menu
    result_share   — Shareable plain-text version of the result
"""

from __future__ import annotations
import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.calculators.formatter import (
    build_explanation_text,
    build_reduce_tax_text,
    build_share_text,
)
from bot.utils.keyboards import main_menu_keyboard
from bot.utils.messages import get_msg

logger = logging.getLogger(__name__)


async def result_reduce(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show advice on reducing tax liability under NTA 2025."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    lang = context.user_data.get("lang", "en")
    try:
        await query.message.reply_html(build_reduce_tax_text(lang))
    except Exception as e:
        logger.error(
            "Error in result_reduce user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
        )
        await query.message.reply_html(get_msg("error", lang))


async def result_explain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Walk through the last result line by line in plain English."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    lang = context.user_data.get("lang", "en")
    last_result = context.user_data.get("last_result")

    try:
        if last_result is None:
            if lang == "pidgin":
                await query.message.reply_html(
                    "⚠️ I no fit find your previous result. Abeg calculate again."
                )
            else:
                await query.message.reply_html(
                    "⚠️ I couldn't find your previous result. Please calculate again."
                )
            return

        explanation = build_explanation_text(lang, last_result)
        await query.message.reply_html(explanation)
    except Exception as e:
        logger.error(
            "Error in result_explain user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
            exc_info=True,
        )
        await query.message.reply_html(get_msg("error", lang))


async def result_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear last_result and return to main menu."""
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    lang = context.user_data.get("lang", "en")
    context.user_data.pop("last_result", None)

    try:
        await query.message.reply_html(
            get_msg("main_menu", lang),
            reply_markup=main_menu_keyboard(lang),
        )
    except Exception as e:
        logger.error(
            "Error in result_again user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
        )


async def result_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a clean plain-text version of the result that the user can forward.
    Telegram does not support bot-initiated forwarding, so we send the text
    as a new message and show an alert explaining how to share it.
    """
    query = update.callback_query
    if query is None:
        return
    await query.answer(
        "Your result is below — copy and share it! 📤",
        show_alert=False,
    )

    lang = context.user_data.get("lang", "en")
    last_result = context.user_data.get("last_result")

    try:
        if last_result is None:
            if lang == "pidgin":
                await query.message.reply_text(
                    "⚠️ I no fit find your result. Abeg calculate again."
                )
            else:
                await query.message.reply_text(
                    "⚠️ No result found. Please calculate again."
                )
            return

        share_text = build_share_text(last_result)
        await query.message.reply_text(share_text)
    except Exception as e:
        logger.error(
            "Error in result_share user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
        )
        await query.message.reply_html(get_msg("error", lang))
