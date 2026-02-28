"""
PAYE Checker ConversationHandler for NaijaTax Bot.

Runs the full salaried flow (12 states), then asks for the employer's
monthly PAYE deduction and compares it against the calculated amount.

States 0–11: identical to salaried.py
State 12: ASK_EMPLOYER_DEDUCTION
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
from bot.calculators.formatter import build_result_text, fmt_naira
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

# State constants — mirrors salaried + one extra
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
    ASK_EMPLOYER_DEDUCTION,
) = range(13)

TOLERANCE = 500  # ₦500 tolerance for "correct" deduction


# ------------------------------------------------------------------ #
# Entry Point                                                           #
# ------------------------------------------------------------------ #

async def start_checker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point — triggered by 'menu_checker' callback."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    for key in [
        "monthly_basic", "monthly_housing", "monthly_transport", "monthly_other",
        "monthly_rent", "use_pension", "use_nhf", "use_nhis", "monthly_nhis",
        "use_life", "annual_life", "checker_calculated_monthly",
    ]:
        context.user_data.pop(key, None)

    try:
        intro = (
            "🔍 <b>PAYE Checker</b>\n\n"
            "I'll calculate what your PAYE should be, then compare it "
            "to what your employer actually deducts.\n\n"
            "Let's start with your income details."
            if lang == "en" else
            "🔍 <b>PAYE Checker</b>\n\n"
            "I go calculate wetin your PAYE suppose be, then compare am "
            "with wetin your oga dey deduct.\n\n"
            "Oya, let's start with your income."
        )
        await query.message.reply_html(intro)
        await query.message.reply_html(get_msg("ask_basic_salary", lang))
    except Exception as e:
        logger.error("Error in start_checker: %s", e)
        return ConversationHandler.END

    return ASK_BASIC


# ------------------------------------------------------------------ #
# Shared state handlers (same logic as salaried.py)                    #
# ------------------------------------------------------------------ #

async def handle_basic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    amount = parse_amount(update.message.text)
    if amount is None:
        await update.message.reply_html(get_msg("invalid_amount", lang))
        return ASK_BASIC
    context.user_data["monthly_basic"] = amount
    await update.message.reply_html(
        get_msg("ask_housing", lang), reply_markup=skip_keyboard(lang)
    )
    return ASK_HOUSING


async def handle_housing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    amount = parse_amount(update.message.text)
    if amount is None:
        await update.message.reply_html(get_msg("invalid_amount", lang))
        return ASK_HOUSING
    context.user_data["monthly_housing"] = amount
    await update.message.reply_html(
        get_msg("ask_transport", lang), reply_markup=skip_keyboard(lang)
    )
    return ASK_TRANSPORT


async def handle_skip_housing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["monthly_housing"] = 0
    await query.message.reply_html(
        get_msg("ask_transport", lang), reply_markup=skip_keyboard(lang)
    )
    return ASK_TRANSPORT


async def handle_transport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    amount = parse_amount(update.message.text)
    if amount is None:
        await update.message.reply_html(get_msg("invalid_amount", lang))
        return ASK_TRANSPORT
    context.user_data["monthly_transport"] = amount
    await update.message.reply_html(
        get_msg("ask_other", lang), reply_markup=skip_keyboard(lang)
    )
    return ASK_OTHER


async def handle_skip_transport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["monthly_transport"] = 0
    await query.message.reply_html(
        get_msg("ask_other", lang), reply_markup=skip_keyboard(lang)
    )
    return ASK_OTHER


async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    amount = parse_amount(update.message.text)
    if amount is None:
        await update.message.reply_html(get_msg("invalid_amount", lang))
        return ASK_OTHER
    context.user_data["monthly_other"] = amount
    await update.message.reply_html(
        get_msg("ask_rent", lang), reply_markup=rent_keyboard(lang)
    )
    return ASK_RENT


async def handle_skip_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["monthly_other"] = 0
    await query.message.reply_html(
        get_msg("ask_rent", lang), reply_markup=rent_keyboard(lang)
    )
    return ASK_RENT


async def handle_rent_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_rent_amount", lang))
        return ASK_RENT_AMOUNT
    context.user_data["monthly_rent"] = 0
    await query.message.reply_html(
        get_msg("ask_pension", lang), reply_markup=yes_no_keyboard(lang)
    )
    return ASK_PENSION


async def handle_rent_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    amount = parse_amount(update.message.text)
    if amount is None:
        await update.message.reply_html(get_msg("invalid_amount", lang))
        return ASK_RENT_AMOUNT
    context.user_data["monthly_rent"] = amount
    await update.message.reply_html(
        get_msg("ask_pension", lang), reply_markup=yes_no_keyboard(lang)
    )
    return ASK_PENSION


async def handle_pension(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["use_pension"] = query.data == BTN_YES
    await query.message.reply_html(
        get_msg("ask_nhf", lang), reply_markup=yes_no_keyboard(lang)
    )
    return ASK_NHF


async def handle_nhf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    context.user_data["use_nhf"] = query.data == BTN_YES
    await query.message.reply_html(
        get_msg("ask_nhis", lang), reply_markup=yes_no_keyboard(lang)
    )
    return ASK_NHIS


async def handle_nhis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_nhis_amount", lang))
        return ASK_NHIS_AMOUNT
    context.user_data["monthly_nhis"] = 0
    await query.message.reply_html(
        get_msg("ask_life", lang), reply_markup=yes_no_keyboard(lang)
    )
    return ASK_LIFE


async def handle_nhis_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    amount = parse_amount(update.message.text)
    if amount is None:
        await update.message.reply_html(get_msg("invalid_amount", lang))
        return ASK_NHIS_AMOUNT
    context.user_data["monthly_nhis"] = amount
    await update.message.reply_html(
        get_msg("ask_life", lang), reply_markup=yes_no_keyboard(lang)
    )
    return ASK_LIFE


async def handle_life(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")
    if query.data == BTN_YES:
        await query.message.reply_html(get_msg("ask_life_amount", lang))
        return ASK_LIFE_AMOUNT
    context.user_data["annual_life"] = 0
    return await _calculate_and_ask_employer(update, context)


async def handle_life_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = context.user_data.get("lang", "en")
    amount = parse_amount(update.message.text)
    if amount is None:
        await update.message.reply_html(get_msg("invalid_amount", lang))
        return ASK_LIFE_AMOUNT
    context.user_data["annual_life"] = amount
    return await _calculate_and_ask_employer(update, context)


# ------------------------------------------------------------------ #
# Checker-specific logic                                                #
# ------------------------------------------------------------------ #

async def _calculate_and_ask_employer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Calculate tax internally and ask for employer's deduction."""
    lang = context.user_data.get("lang", "en")
    try:
        ud = context.user_data
        annual_basic = ud.get("monthly_basic", 0) * 12
        annual_housing = ud.get("monthly_housing", 0) * 12
        annual_transport = ud.get("monthly_transport", 0) * 12
        annual_other = ud.get("monthly_other", 0) * 12
        annual_rent = ud.get("monthly_rent", 0) * 12
        use_pension = ud.get("use_pension", False)
        use_nhf = ud.get("use_nhf", False)
        monthly_nhis = ud.get("monthly_nhis", 0)
        annual_life = ud.get("annual_life", 0)

        gross_annual = annual_basic + annual_housing + annual_transport + annual_other
        rent_relief = calculate_rent_relief(annual_rent)
        pension = calculate_pension(annual_basic, annual_housing, annual_transport) if use_pension else 0.0
        nhf = calculate_nhf(annual_basic) if use_nhf else 0.0
        nhis_annual = monthly_nhis * 12
        life_assurance = calculate_life_assurance_deduction(annual_life)

        chargeable_income = calculate_chargeable_income(
            gross_annual, rent_relief, pension, nhf, nhis_annual, life_assurance
        )
        tax_result = calculate_tax(chargeable_income, gross_annual)

        # Store calculated result for comparison step
        context.user_data["checker_gross"] = gross_annual
        context.user_data["checker_rent_relief"] = rent_relief
        context.user_data["checker_pension"] = pension
        context.user_data["checker_nhf"] = nhf
        context.user_data["checker_nhis_annual"] = nhis_annual
        context.user_data["checker_life"] = life_assurance
        context.user_data["checker_chargeable"] = chargeable_income
        context.user_data["checker_tax_result"] = tax_result
        context.user_data["checker_calculated_monthly"] = tax_result["monthly_paye"]

        await update.effective_message.reply_html(
            get_msg("ask_employer_deduction", lang)
        )
        return ASK_EMPLOYER_DEDUCTION

    except Exception as e:
        logger.error("Error in _calculate_and_ask_employer: %s", e, exc_info=True)
        await update.effective_message.reply_html(get_msg("error", lang))
        return ConversationHandler.END


async def handle_employer_deduction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    lang = context.user_data.get("lang", "en")
    try:
        amount = parse_amount(update.message.text)
        if amount is None:
            await update.message.reply_html(get_msg("invalid_amount", lang))
            return ASK_EMPLOYER_DEDUCTION

        employer_monthly = float(amount)
        calculated_monthly = context.user_data.get("checker_calculated_monthly", 0.0)

        diff = employer_monthly - calculated_monthly
        abs_diff = abs(diff)
        annual_diff = abs_diff * 12

        # Build comparison message
        if abs_diff <= TOLERANCE:
            msg_key = "checker_correct"
        elif diff > TOLERANCE:
            msg_key = "checker_overpaying"
        else:
            msg_key = "checker_underpaying"

        comparison_text = get_msg(msg_key, lang).format(
            calculated=fmt_naira(calculated_monthly),
            employer=fmt_naira(employer_monthly),
            diff=fmt_naira(abs_diff),
            diff_annual=f"{int(annual_diff):,}",
        )

        # Also build the full tax summary
        ud = context.user_data
        tax_result = ud.get("checker_tax_result", {})
        result_text = build_result_text(
            lang=lang,
            gross_annual=ud.get("checker_gross", 0),
            rent_relief=ud.get("checker_rent_relief", 0),
            pension=ud.get("checker_pension", 0),
            nhf=ud.get("checker_nhf", 0),
            nhis_annual=ud.get("checker_nhis_annual", 0),
            life_assurance=ud.get("checker_life", 0),
            chargeable_income=ud.get("checker_chargeable", 0),
            tax_result=tax_result,
        )

        # Store for action buttons
        context.user_data["last_result"] = {
            "calc_type": "checker",
            "gross_annual": ud.get("checker_gross", 0),
            "rent_relief": ud.get("checker_rent_relief", 0),
            "pension": ud.get("checker_pension", 0),
            "nhf": ud.get("checker_nhf", 0),
            "nhis_annual": ud.get("checker_nhis_annual", 0),
            "life_assurance": ud.get("checker_life", 0),
            "chargeable_income": ud.get("checker_chargeable", 0),
            "annual_tax": tax_result.get("annual_tax", 0),
            "monthly_paye": tax_result.get("monthly_paye", 0),
            "effective_rate": tax_result.get("effective_rate", 0),
            "bands": tax_result.get("bands", []),
            "is_exempt": tax_result.get("is_exempt", False),
            "lang": lang,
        }

        # Send result then comparison
        await update.message.reply_html(result_text)
        await update.message.reply_html(
            comparison_text,
            reply_markup=result_actions_keyboard(lang),
        )

        # Log calculation
        user = update.effective_user
        if user:
            await asyncio.to_thread(
                db.log_calculation,
                user.id,
                "checker",
                ud.get("checker_gross", 0),
                ud.get("checker_chargeable", 0),
                tax_result.get("annual_tax", 0),
                tax_result.get("effective_rate", 0),
            )

    except Exception as e:
        logger.error(
            "Error in handle_employer_deduction user=%s: %s",
            getattr(update.effective_user, "id", "?"),
            e,
            exc_info=True,
        )
        await update.message.reply_html(get_msg("error", lang))

    return ConversationHandler.END


# ------------------------------------------------------------------ #
# ConversationHandler Factory                                           #
# ------------------------------------------------------------------ #

def build_checker_conv() -> ConversationHandler:
    """Build and return the PAYE checker ConversationHandler."""
    from bot.handlers.start import cancel

    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_checker, pattern="^menu_checker$"),
        ],
        states={
            ASK_BASIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_basic)],
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
            ASK_EMPLOYER_DEDUCTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_employer_deduction
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_message=False,
        per_chat=True,
        per_user=True,
    )
