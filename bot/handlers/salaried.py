"""
Salaried employee tax calculation ConversationHandler for NaijaTax Bot.

States:
    ASK_BASIC        (0) — Monthly basic salary
    ASK_HOUSING      (1) — Monthly housing allowance (optional)
    ASK_TRANSPORT    (2) — Monthly transport allowance (optional)
    ASK_OTHER        (3) — Other monthly allowances (optional)
    ASK_RENT         (4) — Do you pay rent? (Yes/No/Own home)
    ASK_RENT_AMOUNT  (5) — Monthly rent amount
    ASK_PENSION      (6) — Pension contribution opt-in
    ASK_NHF          (7) — NHF contribution opt-in
    ASK_NHIS         (8) — NHIS opt-in
    ASK_NHIS_AMOUNT  (9) — Monthly NHIS contribution
    ASK_LIFE         (10) — Life assurance opt-in
    ASK_LIFE_AMOUNT  (11) — Annual life assurance premium
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
    calculate_nhf,
    calculate_pension,
    calculate_rent_relief,
)
from bot.calculators.formatter import build_result_text
from bot.database import db
from bot.utils.keyboards import (
    BTN_NO,
    BTN_OWN_HOME,
    BTN_SKIP,
    BTN_YES,
    result_actions_keyboard,
    skip_keyboard,
    yes_no_keyboard,
    rent_keyboard,
)
from bot.utils.messages import get_msg
from bot.utils.validators import parse_amount

logger = logging.getLogger(__name__)

# State constants
(
    ASK_BASIC,
    ASK_HOUSING,
    ASK_TRANSPORT,
    ASK_OTHER,
    ASK_RENT,
    ASK_RENT_AMOUNT,
    ASK_PENSION,
    ASK_NHF,
    ASK_NHIS,
    ASK_NHIS_AMOUNT,
    ASK_LIFE,
    ASK_LIFE_AMOUNT,
) = range(12)


# ------------------------------------------------------------------ #
# Entry Point                                                           #
# ------------------------------------------------------------------ #

async def start_salaried(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — triggered by 'menu_salaried' callback."""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "en")
    # Reset any previous salaried session data
    for key in [
        "monthly_basic", "monthly_housing", "monthly_transport", "monthly_other",
        "monthly_rent", "use_pension", "use_nhf", "use_nhis", "monthly_nhis",
        "use_life", "annual_life",
    ]:
        context.user_data.pop(key, None)

    try:
        await query.message.reply_html(get_msg("ask_basic_salary", lang))
    except Exception as e:
        logger.error("Error in start_salaried: %s", e)
        await query.message.reply_text(get_msg("error", lang))
        return ConversationHandler.END

    return ASK_BASIC


# ------------------------------------------------------------------ #
# State Handlers — Income                                               #
# ------------------------------------------------------------------ #

async def handle_basic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_BASIC

        context.user_data["monthly_basic"] = amount
        await update.message.reply_html(
            get_msg("ask_housing", lang),
            reply_markup=skip_keyboard(lang),
        )
        return ASK_HOUSING
    except Exception as e:
        logger.error("Error in handle_basic user=%s: %s", update.effective_user.id, e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_housing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_HOUSING

        context.user_data["monthly_housing"] = amount
        await update.message.reply_html(
            get_msg("ask_transport", lang),
            reply_markup=skip_keyboard(lang),
        )
        return ASK_TRANSPORT
    except Exception as e:
        logger.error("Error in handle_housing: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_skip_housing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["monthly_housing"] = 0
    await query.message.reply_html(
        get_msg("ask_transport", lang),
        reply_markup=skip_keyboard(lang),
    )
    return ASK_TRANSPORT


async def handle_transport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_TRANSPORT

        context.user_data["monthly_transport"] = amount
        await update.message.reply_html(
            get_msg("ask_other", lang),
            reply_markup=skip_keyboard(lang),
        )
        return ASK_OTHER
    except Exception as e:
        logger.error("Error in handle_transport: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_skip_transport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["monthly_transport"] = 0
    await query.message.reply_html(
        get_msg("ask_other", lang),
        reply_markup=skip_keyboard(lang),
    )
    return ASK_OTHER


async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_OTHER

        context.user_data["monthly_other"] = amount
        await update.message.reply_html(
            get_msg("ask_rent", lang),
            reply_markup=rent_keyboard(lang),
        )
        return ASK_RENT
    except Exception as e:
        logger.error("Error in handle_other: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_skip_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["monthly_other"] = 0
    await query.message.reply_html(
        get_msg("ask_rent", lang),
        reply_markup=rent_keyboard(lang),
    )
    return ASK_RENT


# ------------------------------------------------------------------ #
# State Handlers — Rent                                                 #
# ------------------------------------------------------------------ #

async def handle_rent_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Yes / No / Own home for rent question."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_rent_amount", lang))
        return ASK_RENT_AMOUNT
    else:
        # No or Own home — both mean zero rent
        context.user_data["monthly_rent"] = 0
        await query.message.reply_html(
            get_msg("ask_pension", lang),
            reply_markup=yes_no_keyboard(lang),
        )
        return ASK_PENSION


async def handle_rent_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_RENT_AMOUNT

        context.user_data["monthly_rent"] = amount
        await update.message.reply_html(
            get_msg("ask_pension", lang),
            reply_markup=yes_no_keyboard(lang),
        )
        return ASK_PENSION
    except Exception as e:
        logger.error("Error in handle_rent_amount: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


# ------------------------------------------------------------------ #
# State Handlers — Deductions                                           #
# ------------------------------------------------------------------ #

async def handle_pension(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["use_pension"] = query.data == BTN_YES
    await query.message.reply_html(
        get_msg("ask_nhf", lang),
        reply_markup=yes_no_keyboard(lang),
    )
    return ASK_NHF


async def handle_nhf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["use_nhf"] = query.data == BTN_YES
    await query.message.reply_html(
        get_msg("ask_nhis", lang),
        reply_markup=yes_no_keyboard(lang),
    )
    return ASK_NHIS


async def handle_nhis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_nhis_amount", lang))
        return ASK_NHIS_AMOUNT
    else:
        context.user_data["monthly_nhis"] = 0
        await query.message.reply_html(
            get_msg("ask_life", lang),
            reply_markup=yes_no_keyboard(lang),
        )
        return ASK_LIFE


async def handle_nhis_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_NHIS_AMOUNT

        context.user_data["monthly_nhis"] = amount
        await update.message.reply_html(
            get_msg("ask_life", lang),
            reply_markup=yes_no_keyboard(lang),
        )
        return ASK_LIFE
    except Exception as e:
        logger.error("Error in handle_nhis_amount: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_life(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_life_amount", lang))
        return ASK_LIFE_AMOUNT
    else:
        context.user_data["annual_life"] = 0
        return await _finish_salaried(update, context)


async def handle_life_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_LIFE_AMOUNT

        context.user_data["annual_life"] = amount
        return await _finish_salaried(update, context)
    except Exception as e:
        logger.error("Error in handle_life_amount: %s", e)
        await update.message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


# ------------------------------------------------------------------ #
# Calculation and Result                                                #
# ------------------------------------------------------------------ #

async def _finish_salaried(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Perform the final tax calculation and send the result.
    Called from the terminal state handlers (handle_life, handle_life_amount).
    Not a ConversationHandler state itself.
    """
    lang = context.user_data.get("lang", "en")
    try:
        await update.effective_message.reply_html(get_msg("calculating", lang))

        ud = context.user_data
        monthly_basic = ud.get("monthly_basic", 0)
        monthly_housing = ud.get("monthly_housing", 0)
        monthly_transport = ud.get("monthly_transport", 0)
        monthly_other = ud.get("monthly_other", 0)
        monthly_rent = ud.get("monthly_rent", 0)
        use_pension = ud.get("use_pension", False)
        use_nhf = ud.get("use_nhf", False)
        monthly_nhis = ud.get("monthly_nhis", 0)
        annual_life = ud.get("annual_life", 0)

        # Annualise monthly inputs
        annual_basic = monthly_basic * 12
        annual_housing = monthly_housing * 12
        annual_transport = monthly_transport * 12
        annual_other = monthly_other * 12
        annual_rent = monthly_rent * 12

        gross_annual = annual_basic + annual_housing + annual_transport + annual_other

        # Calculate deductions
        rent_relief = calculate_rent_relief(annual_rent)
        pension = calculate_pension(annual_basic, annual_housing, annual_transport) if use_pension else 0.0
        nhf = calculate_nhf(annual_basic) if use_nhf else 0.0
        nhis_annual = monthly_nhis * 12
        life_assurance = calculate_life_assurance_deduction(annual_life)

        # Calculate chargeable income and tax
        chargeable_income = calculate_chargeable_income(
            gross_annual, rent_relief, pension, nhf, nhis_annual, life_assurance
        )
        tax_result = calculate_tax(chargeable_income, gross_annual)

        # Store result for post-result action buttons
        last_result = {
            "calc_type": "salaried",
            "gross_annual": gross_annual,
            "rent_relief": rent_relief,
            "pension": pension,
            "nhf": nhf,
            "nhis_annual": nhis_annual,
            "life_assurance": life_assurance,
            "chargeable_income": chargeable_income,
            "annual_tax": tax_result["annual_tax"],
            "monthly_paye": tax_result["monthly_paye"],
            "effective_rate": tax_result["effective_rate"],
            "bands": tax_result["bands"],
            "is_exempt": tax_result["is_exempt"],
            "lang": lang,
        }
        context.user_data["last_result"] = last_result

        # Build and send result message
        result_text = build_result_text(
            lang=lang,
            gross_annual=gross_annual,
            rent_relief=rent_relief,
            pension=pension,
            nhf=nhf,
            nhis_annual=nhis_annual,
            life_assurance=life_assurance,
            chargeable_income=chargeable_income,
            tax_result=tax_result,
        )

        await update.effective_message.reply_html(
            result_text,
            reply_markup=result_actions_keyboard(lang),
        )

        # Log to database
        user = update.effective_user
        if user:
            await asyncio.to_thread(
                db.log_calculation,
                user.id,
                "salaried",
                gross_annual,
                chargeable_income,
                tax_result["annual_tax"],
                tax_result["effective_rate"],
            )

    except Exception as e:
        logger.error(
            "Error in _finish_salaried user=%s: %s",
            getattr(update.effective_user, "id", "?"),
            e,
            exc_info=True,
        )
        await update.effective_message.reply_html(get_msg("error", lang))

    return ConversationHandler.END


# ------------------------------------------------------------------ #
# ConversationHandler Factory                                           #
# ------------------------------------------------------------------ #

def build_salaried_conv() -> ConversationHandler:
    """Build and return the salaried ConversationHandler."""
    from bot.handlers.start import cancel

    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_salaried, pattern="^menu_salaried$"),
        ],
        states={
            ASK_BASIC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_basic),
            ],
            ASK_HOUSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_housing),
                CallbackQueryHandler(handle_skip_housing, pattern=f"^{BTN_SKIP}$"),
            ],
            ASK_TRANSPORT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transport),
                CallbackQueryHandler(handle_skip_transport, pattern=f"^{BTN_SKIP}$"),
            ],
            ASK_OTHER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other),
                CallbackQueryHandler(handle_skip_other, pattern=f"^{BTN_SKIP}$"),
            ],
            ASK_RENT: [
                CallbackQueryHandler(
                    handle_rent_choice,
                    pattern=f"^({BTN_YES}|{BTN_NO}|{BTN_OWN_HOME})$",
                ),
            ],
            ASK_RENT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rent_amount),
            ],
            ASK_PENSION: [
                CallbackQueryHandler(handle_pension, pattern=f"^({BTN_YES}|{BTN_NO})$"),
            ],
            ASK_NHF: [
                CallbackQueryHandler(handle_nhf, pattern=f"^({BTN_YES}|{BTN_NO})$"),
            ],
            ASK_NHIS: [
                CallbackQueryHandler(handle_nhis, pattern=f"^({BTN_YES}|{BTN_NO})$"),
            ],
            ASK_NHIS_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nhis_amount),
            ],
            ASK_LIFE: [
                CallbackQueryHandler(handle_life, pattern=f"^({BTN_YES}|{BTN_NO})$"),
            ],
            ASK_LIFE_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_life_amount),
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
