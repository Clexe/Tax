"""
NaijaTax Bot — Main Entry Point.

Startup sequence:
  1. Load environment variables (.env in dev).
  2. Configure logging.
  3. Run Alembic migrations (upgrades DB schema to latest).
  4. Build the PTB Application with all handlers registered.
  5. Start in webhook mode (production) or polling mode (local dev).

Webhook mode (WEBHOOK_URL is set):
  - Creates an aiohttp web server (no Flask/FastAPI).
  - GET /          → health check endpoint.
  - POST /{TOKEN}  → receives Telegram webhook updates.
  - PTB lifecycle: initialize() → start() → process_update() per request.

Polling mode (WEBHOOK_URL not set):
  - Uses PTB's built-in run_polling() which manages its own lifecycle.

Run with: python -m bot.main
"""

from __future__ import annotations
import asyncio
import logging
import os
import sys
import warnings

from dotenv import load_dotenv

load_dotenv()

# Suppress PTBUserWarning raised when ConversationHandler uses per_message=False
# with CallbackQueryHandlers.  The default (per_message=False) is intentional
# here because every flow mixes MessageHandlers and CallbackQueryHandlers;
# per_message=True would break the text-input states.
warnings.filterwarnings(
    "ignore",
    message="If 'per_message=False'",
    category=UserWarning,
)

# ------------------------------------------------------------------ #
# Logging setup (must be done before any other imports that log)       #
# ------------------------------------------------------------------ #

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Application builder                                                   #
# ------------------------------------------------------------------ #

def build_application():
    """
    Create and configure the PTB Application with all handlers.

    Handler registration order matters in PTB:
    ConversationHandlers must be registered before generic CallbackQueryHandlers
    to ensure their entry point patterns are matched first.
    """
    from telegram.ext import Application, CallbackQueryHandler, CommandHandler

    from bot.handlers.start import (
        cancel,
        change_language_callback,
        language_callback,
        main_menu_callback,
        start_command,
    )
    from bot.handlers.salaried import build_salaried_conv
    from bot.handlers.selfemployed import build_selfemployed_conv
    from bot.handlers.checker import build_checker_conv
    from bot.handlers.help import help_entry, help_topic
    from bot.handlers.admin import admin_command
    from bot.handlers.actions import (
        result_explain,
        result_again,
        result_reduce,
        result_share,
    )

    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN environment variable is not set.")
        sys.exit(1)

    app = Application.builder().token(bot_token).build()

    # Core commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("admin", admin_command))

    # Language selection (from /start welcome message)
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_(en|pidgin)$"))

    # Change language from main menu
    app.add_handler(CallbackQueryHandler(change_language_callback, pattern="^menu_lang$"))

    # Back to main menu
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^back_main$"))

    # ConversationHandlers — registered before generic callback handlers
    # to ensure their entry point patterns are matched first.
    app.add_handler(build_salaried_conv())
    app.add_handler(build_selfemployed_conv())
    app.add_handler(build_checker_conv())

    # Help flow (stateless callbacks)
    app.add_handler(CallbackQueryHandler(help_entry, pattern="^menu_help$"))
    app.add_handler(CallbackQueryHandler(help_topic, pattern="^help_"))

    # Post-result action buttons (outside ConversationHandlers)
    app.add_handler(CallbackQueryHandler(result_reduce, pattern="^result_reduce$"))
    app.add_handler(CallbackQueryHandler(result_explain, pattern="^result_explain$"))
    app.add_handler(CallbackQueryHandler(result_again, pattern="^result_again$"))
    app.add_handler(CallbackQueryHandler(result_share, pattern="^result_share$"))

    # Global error handler
    app.add_error_handler(_error_handler)

    return app


async def _error_handler(update, context) -> None:
    """
    Global error handler — catches exceptions from all handlers.

    Logs the error with context and sends a friendly message to the user.
    Never exposes raw Python tracebacks.
    """
    from bot.utils.messages import get_msg

    logger.error(
        "Unhandled exception | user=%s | update_id=%s | error=%s",
        getattr(update.effective_user, "id", "unknown") if update else "unknown",
        getattr(update, "update_id", "N/A") if update else "N/A",
        context.error,
        exc_info=context.error,
    )

    if update and update.effective_message:
        try:
            lang = "en"
            if context.user_data:
                lang = context.user_data.get("lang", "en")
            await update.effective_message.reply_html(get_msg("error", lang))
        except Exception:
            pass  # Don't recurse on error handler failures


# ------------------------------------------------------------------ #
# Production Webhook Mode                                               #
# ------------------------------------------------------------------ #

async def run_webhook(app) -> None:
    """
    Run the bot in webhook mode using aiohttp.

    Serves:
      GET  /         → health check, returns "NaijaTax Bot is running"
      POST /{TOKEN}  → webhook endpoint for Telegram updates
    """
    from aiohttp import web
    from telegram import Update

    bot_token = os.environ["BOT_TOKEN"]
    webhook_url = os.environ["WEBHOOK_URL"]
    port = int(os.environ.get("PORT", 8443))
    webhook_path = f"/{bot_token}"

    # Initialise PTB (sets up internal state, job queue, etc.)
    await app.initialize()
    await app.start()

    # Register webhook with Telegram
    await app.bot.set_webhook(
        url=f"{webhook_url}{webhook_path}",
        allowed_updates=Update.ALL_TYPES,
    )
    logger.info("Webhook registered at %s%s", webhook_url, webhook_path)

    # Health check handler
    async def health(request: web.Request) -> web.Response:
        return web.Response(text="NaijaTax Bot is running")

    # Telegram update handler
    async def handle_update(request: web.Request) -> web.Response:
        try:
            data = await request.json()
            update = Update.de_json(data, app.bot)
            if update is not None:
                await app.process_update(update)
        except Exception as exc:
            logger.error("Error processing webhook update: %s", exc, exc_info=True)
        return web.Response(status=200, text="OK")

    # Build aiohttp web app
    web_app = web.Application()
    web_app.router.add_get("/", health)
    web_app.router.add_post(webhook_path, handle_update)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("NaijaTax Bot webhook server started on port %d", port)

    try:
        # Block forever until process is killed
        await asyncio.Event().wait()
    finally:
        logger.info("Shutting down...")
        await app.stop()
        await app.shutdown()
        await runner.cleanup()


# ------------------------------------------------------------------ #
# Development Polling Mode                                              #
# ------------------------------------------------------------------ #

async def run_polling(app) -> None:
    """
    Run the bot in polling mode for local development.

    PTB's run_polling() manages the full lifecycle (init/start/stop/shutdown)
    internally. Do NOT call app.initialize() or app.start() before this.
    """
    logger.info("Starting NaijaTax Bot in polling mode (development)...")
    await app.run_polling(
        drop_pending_updates=True,
    )


# ------------------------------------------------------------------ #
# Main                                                                  #
# ------------------------------------------------------------------ #

async def main() -> None:
    """
    Main async entry point.

    1. Run Alembic migrations.
    2. Build the PTB Application.
    3. Start in webhook or polling mode based on WEBHOOK_URL env var.
    """
    # Run database migrations before starting the bot
    logger.info("Running database migrations...")
    try:
        from bot.database.db import run_migrations
        run_migrations()
        logger.info("Database migrations complete.")
    except Exception as e:
        logger.error("Migration error: %s", e, exc_info=True)
        # Continue — migrations may fail on first run if DB isn't available yet.
        # The bot will still start; Railway restarts on failure.

    app = build_application()

    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        await run_webhook(app)
    else:
        await run_polling(app)


if __name__ == "__main__":
    asyncio.run(main())
