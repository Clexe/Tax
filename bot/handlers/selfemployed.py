"""
Self-employed tax calculation ConversationHandler for NaijaTax Bot.

States:
    ASK_PERIOD          (0) — Monthly or Annual income entry
    ASK_INCOME          (1) — Income amount
    ASK_EXPENSES        (2) — Business expenses? (Yes/No)
    ASK_EXPENSES_AMOUNT (3) — Total annual expenses
    ASK_RENT_SE         (4) — Do you pay rent?
    ASK_RENT_AMOUNT_SE  (5) — Monthly rent amount
    ASK_PENSION_SE      (6) — Pension contribution opt-in

For self-employed:
  - Net income = gross income - expenses
  - Pension = 8% of net income (no qualifying emolument split)
  - NHF and NHIS are not collected (spec only covers them for salaried)
  - Rent relief applies the same formula (20% of annual rent, max ₦500k)
"""

from __future__ import annotations
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.calculators.nta import calculate_tax
from bot.calculators.reliefs import (
    calculate_chargeable_income,
    calculate_life_assurance_deduction,
    calculate_pension_selfemployed,
    calculate_rent_relief,
)
from bot.calculators.formatter import build_result_text
from bot.database import db
from bot.utils.keyboards import (
    BTN_ANNUALLY,
    BTN_MONTHLY,
    BTN_NO,
    BTN_OWN_HOME,
    BTN_YES,
    period_keyboard,
    rent_keyboard,
    result_actions_keyboard,
    yes_no_keyboard,
)
from bot.utils.messages import get_msg
from bot.utils.validators import parse_amount

logger = logging.getLogger(__name__)

# State constants
(
    ASK_PERIOD,
    ASK_INCOME,
    ASK_EXPENSES,
    ASK_EXPENSES_AMOUNT,
    ASK_RENT_SE,
    ASK_RENT_AMOUNT_SE,
    ASK_PENSION_SE,
) = range(7)


# ------------------------------------------------------------------ #
# Entry Point                                                           #
# ------------------------------------------------------------------ #

async def start_selfemployed(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Entry point — triggered by 'menu_selfemployed' callback."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    for key in ["se_period", "se_annual_income", "se_annual_expenses", "se_monthly_rent", "se_use_pension"]:
        context.user_data.pop(key, None)

    try:
        await query.message.reply_html(
            get_msg("ask_period", lang),
            reply_markup=period_keyboard(lang),
        )
    except Exception as e:
        logger.error("Error in start_selfemployed: %s", e)
        await query.message.reply_text(get_msg("error", lang))
        return ConversationHandler.END

    return ASK_PERIOD


# ------------------------------------------------------------------ #
# State Handlers                                                        #
# ------------------------------------------------------------------ #

async def handle_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    context.user_data["se_period"] = "monthly" if query.data == BTN_MONTHLY else "annually"

    msg_key = "ask_income_monthly" if query.data == BTN_MONTHLY else "ask_income_annual"
    await query.message.reply_html(get_msg(msg_key, lang))
    return ASK_INCOME


async def handle_income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_INCOME

        period = context.user_data.get("se_period", "annually")
        annual_income = amount * 12 if period == "monthly" else amount
        context.user_data["se_annual_income"] = annual_income

        await update.message.reply_html(
            get_msg("ask_expenses", lang),
            reply_markup=yes_no_keyboard(lang),
        )
        return ASK_EXPENSES
    except Exception as e:
        logger.error("Error in handle_income: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_expenses_amount", lang))
        return ASK_EXPENSES_AMOUNT
    else:
        context.user_data["se_annual_expenses"] = 0
        await query.message.reply_html(
            get_msg("ask_rent", lang),
            reply_markup=rent_keyboard(lang),
        )
        return ASK_RENT_SE


async def handle_expenses_amount(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_EXPENSES_AMOUNT

        context.user_data["se_annual_expenses"] = amount
        await update.message.reply_html(
            get_msg("ask_rent", lang),
            reply_markup=rent_keyboard(lang),
        )
        return ASK_RENT_SE
    except Exception as e:
        logger.error("Error in handle_expenses_amount: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_rent_choice_se(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_rent_amount", lang))
        return ASK_RENT_AMOUNT_SE
    else:
        context.user_data["se_monthly_rent"] = 0
        await query.message.reply_html(
            get_msg("ask_pension", lang),
            reply_markup=yes_no_keyboard(lang),
        )
        return ASK_PENSION_SE


async def handle_rent_amount_se(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_RENT_AMOUNT_SE

        context.user_data["se_monthly_rent"] = amount
        await update.message.reply_html(
            get_msg("ask_pension", lang),
            reply_markup=yes_no_keyboard(lang),
        )
        return ASK_PENSION_SE
    except Exception as e:
        logger.error("Error in handle_rent_amount_se: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_pension_se(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["se_use_pension"] = query.data == BTN_YES
    return await _finish_selfemployed(update, context)


# ------------------------------------------------------------------ #
# Calculation and Result                                                #
# ------------------------------------------------------------------ #

async def _finish_selfemployed(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Perform final self-employed tax calculation and send result."""
    lang = context.user_data.get("lang", "en")
    try:
        await update.effective_message.reply_html(get_msg("calculating", lang))

        ud = context.user_data
        annual_income = ud.get("se_annual_income", 0)
        annual_expenses = ud.get("se_annual_expenses", 0)
        monthly_rent = ud.get("se_monthly_rent", 0)
        use_pension = ud.get("se_use_pension", False)

        # Net income (gross - expenses) is the base
        net_income = max(0, annual_income - annual_expenses)

        annual_rent = monthly_rent * 12
        rent_relief = calculate_rent_relief(annual_rent)
        pension = calculate_pension_selfemployed(net_income) if use_pension else 0.0

        chargeable_income = calculate_chargeable_income(
            net_income,
            rent_relief=rent_relief,
            pension=pension,
        )
        tax_result = calculate_tax(chargeable_income, net_income)

        last_result = {
            "calc_type": "selfemployed",
            "gross_annual": net_income,
            "rent_relief": rent_relief,
            "pension": pension,
            "nhf": 0.0,
            "nhis_annual": 0.0,
            "life_assurance": 0.0,
            "chargeable_income": chargeable_income,
            "annual_tax": tax_result["annual_tax"],
            "monthly_paye": tax_result["monthly_paye"],
            "effective_rate": tax_result["effective_rate"],
            "bands": tax_result["bands"],
            "is_exempt": tax_result["is_exempt"],
            "lang": lang,
        }
        context.user_data["last_result"] = last_result

        result_text = build_result_text(
            lang=lang,
            gross_annual=net_income,
            rent_relief=rent_relief,
            pension=pension,
            nhf=0.0,
            nhis_annual=0.0,
            life_assurance=0.0,
            chargeable_income=chargeable_income,
            tax_result=tax_result,
        )

        await update.effective_message.reply_html(
            result_text,
            reply_markup=result_actions_keyboard(lang),
        )

        user = update.effective_user
        if user:
            await asyncio.to_thread(
                db.log_calculation,
                user.id,
                "selfemployed",
                net_income,
                chargeable_income,
                tax_result["annual_tax"],
                tax_result["effective_rate"],
            )

    except Exception as e:
        logger.error(
            "Error in _finish_selfemployed user=%s: %s",
            getattr(update.effective_user, "id", "?"),
            e,
            exc_info=True,
        )
        await update.effective_message.reply_html(get_msg("error", lang))

    return ConversationHandler.END


# ------------------------------------------------------------------ #
# ConversationHandler Factory                                           #
# ------------------------------------------------------------------ #

def build_selfemployed_conv() -> ConversationHandler:
    """Build and return the self-employed ConversationHandler."""
    from bot.handlers.start import cancel

    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_selfemployed, pattern="^menu_selfemployed$"),
        ],
        states={
            ASK_PERIOD: [
                CallbackQueryHandler(
                    handle_period, pattern=f"^({BTN_MONTHLY}|{BTN_ANNUALLY})$"
                ),
            ],
            ASK_INCOME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_income),
            ],
            ASK_EXPENSES: [
                CallbackQueryHandler(handle_expenses, pattern=f"^({BTN_YES}|{BTN_NO})$"),
            ],
            ASK_EXPENSES_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expenses_amount),
            ],
            ASK_RENT_SE: [
                CallbackQueryHandler(
                    handle_rent_choice_se,
                    pattern=f"^({BTN_YES}|{BTN_NO}|{BTN_OWN_HOME})$",
                ),
            ],
            ASK_RENT_AMOUNT_SE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rent_amount_se),
            ],
            ASK_PENSION_SE: [
                CallbackQueryHandler(
                    handle_pension_se, pattern=f"^({BTN_YES}|{BTN_NO})$"
                ),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
        ],
        allow_reentry=True,
        per_message=False,
        per_chat=True,
        per_user=True,
    )
