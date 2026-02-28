"""
/start command handler and language selection for NaijaTax Bot.

Handles:
  - /start → shows welcome message + language keyboard
  - Language selection callbacks (lang_en, lang_pidgin)
  - Main menu display
  - Language change from main menu
  - /cancel (used as fallback in all ConversationHandlers)
"""

from __future__ import annotations
import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.utils.messages import get_msg
from bot.utils.keyboards import (
    lang_keyboard,
    main_menu_keyboard,
    LANG_EN,
    LANG_PIDGIN,
)
from bot.database import db

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command.

    - Upserts the user in the database.
    - Loads stored language preference.
    - Shows welcome message with language selector.

    DB calls are best-effort: if they fail or time out the welcome message
    is still sent, preventing the bot from appearing unresponsive when
    the database is slow to accept connections.
    """
    try:
        user = update.effective_user
        if user is None:
            return

        # Best-effort DB operations — welcome must always be sent even if DB
        # is temporarily slow or unavailable.
        lang = "en"
        try:
            await asyncio.wait_for(
                asyncio.to_thread(db.upsert_user, user.id, user.username),
                timeout=5.0,
            )
            lang = await asyncio.wait_for(
                asyncio.to_thread(db.get_language, user.id),
                timeout=5.0,
            )
        except Exception as db_err:
            logger.warning(
                "DB unavailable in start_command user=%s: %s",
                getattr(user, "id", "?"),
                db_err,
            )

        context.user_data["lang"] = lang

        await update.message.reply_html(
            get_msg("welcome", "en"),  # Always show welcome in English first
            reply_markup=lang_keyboard(),
        )
    except Exception as e:
        logger.error(
            "Error in start_command user=%s: %s",
            getattr(update.effective_user, "id", "?"),
            e,
            exc_info=True,
        )
        if update.message:
            await update.message.reply_text(
                "Something went wrong. Please try again."
            )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle lang_en and lang_pidgin callbacks.

    Sets the user's language preference in user_data and database,
    then shows the main menu.
    """
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    try:
        lang = "en" if query.data == LANG_EN else "pidgin"
        context.user_data["lang"] = lang

        await asyncio.to_thread(db.set_language, query.from_user.id, lang)

        await query.edit_message_text(
            get_msg("main_menu", lang),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(lang),
        )
    except Exception as e:
        logger.error(
            "Error in language_callback user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
            exc_info=True,
        )


async def change_language_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle menu_lang callback — re-show the language selection keyboard.
    """
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    try:
        await query.edit_message_text(
            get_msg("welcome", "en"),
            parse_mode="HTML",
            reply_markup=lang_keyboard(),
        )
    except Exception as e:
        logger.error(
            "Error in change_language_callback user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
            exc_info=True,
        )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send (not edit) the main menu.
    Used by cancel handler and result_again callback.
    """
    lang = context.user_data.get("lang", "en")
    msg = update.effective_message
    if msg is None:
        return
    await msg.reply_html(
        get_msg("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )


async def main_menu_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle back_main callback — edit message to show main menu.
    """
    query = update.callback_query
    if query is None:
        return
    await query.answer()

    try:
        lang = context.user_data.get("lang", "en")
        await query.edit_message_text(
            get_msg("main_menu", lang),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(lang),
        )
    except Exception as e:
        logger.error(
            "Error in main_menu_callback user=%s: %s",
            getattr(query.from_user, "id", "?"),
            e,
            exc_info=True,
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /cancel command.

    Works from any state in any ConversationHandler (registered as fallback).
    Clears user_data (preserving language preference), shows main menu,
    and ends the conversation.
    """
    try:
        lang = context.user_data.get("lang", "en")
        # Clear session data but keep language preference
        context.user_data.clear()
        context.user_data["lang"] = lang

        if update.message:
            await update.message.reply_html(
                get_msg("cancelled", lang),
                reply_markup=main_menu_keyboard(lang),
            )
    except Exception as e:
        logger.error(
            "Error in cancel user=%s: %s",
            getattr(update.effective_user, "id", "?"),
            e,
            exc_info=True,
        )

    return ConversationHandler.END
