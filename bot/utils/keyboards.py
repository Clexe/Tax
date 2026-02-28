"""
Inline keyboard builders for NaijaTax Bot.

All keyboard functions return InlineKeyboardMarkup objects.
Callback data constants are defined here and imported throughout the project.
"""

from __future__ import annotations
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ------------------------------------------------------------------ #
# Callback Data Constants                                               #
# ------------------------------------------------------------------ #

# Language selection
LANG_EN = "lang_en"
LANG_PIDGIN = "lang_pidgin"

# Main menu
MENU_SALARIED = "menu_salaried"
MENU_SELFEMPLOYED = "menu_selfemployed"
MENU_CHECKER = "menu_checker"
MENU_HELP = "menu_help"
MENU_LANG = "menu_lang"

# Yes / No
BTN_YES = "yn_yes"
BTN_NO = "yn_no"

# Skip (optional fields)
BTN_SKIP = "skip"

# Rent options
BTN_OWN_HOME = "own_home"

# Income period
BTN_MONTHLY = "period_monthly"
BTN_ANNUALLY = "period_annually"

# Post-result actions
RESULT_REDUCE = "result_reduce"
RESULT_EXPLAIN = "result_explain"
RESULT_AGAIN = "result_again"
RESULT_SHARE = "result_share"

# Help topics
HELP_PAYE = "help_paye"
HELP_CHARGEABLE = "help_chargeable"
HELP_RENT_RELIEF = "help_rent_relief"
HELP_WHY_ZERO = "help_why_zero"
HELP_PAY_TAX = "help_pay_tax"
HELP_NONREMITTANCE = "help_nonremittance"
HELP_NRS = "help_nrs"

# Navigation
BACK_MAIN = "back_main"


# ------------------------------------------------------------------ #
# Keyboard Builders                                                     #
# ------------------------------------------------------------------ #

def lang_keyboard() -> InlineKeyboardMarkup:
    """Language selection: English or Pidgin."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English", callback_data=LANG_EN),
            InlineKeyboardButton("🗣️ Pidgin", callback_data=LANG_PIDGIN),
        ]
    ])


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Main menu with 5 options."""
    if lang == "pidgin":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💼 Calculate tax (Salary Worker)", callback_data=MENU_SALARIED)],
            [InlineKeyboardButton("🧾 Calculate tax (Self-Employed)", callback_data=MENU_SELFEMPLOYED)],
            [InlineKeyboardButton("🔍 Check my employer's deduction", callback_data=MENU_CHECKER)],
            [InlineKeyboardButton("❓ Help & FAQs", callback_data=MENU_HELP)],
            [InlineKeyboardButton("🌍 Change language", callback_data=MENU_LANG)],
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 Calculate my tax (Salaried)", callback_data=MENU_SALARIED)],
        [InlineKeyboardButton("🧾 Calculate my tax (Self-Employed)", callback_data=MENU_SELFEMPLOYED)],
        [InlineKeyboardButton("🔍 Check my employer's deduction", callback_data=MENU_CHECKER)],
        [InlineKeyboardButton("❓ Help & FAQs", callback_data=MENU_HELP)],
        [InlineKeyboardButton("🌍 Change language", callback_data=MENU_LANG)],
    ])


def yes_no_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Yes / No inline keyboard."""
    if lang == "pidgin":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=BTN_YES),
                InlineKeyboardButton("❌ No", callback_data=BTN_NO),
            ]
        ])
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes", callback_data=BTN_YES),
            InlineKeyboardButton("❌ No", callback_data=BTN_NO),
        ]
    ])


def skip_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Skip button for optional fields."""
    label = "Skip ⏭️" if lang == "en" else "Skip ⏭️"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=BTN_SKIP)]
    ])


def rent_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Three-option keyboard for rent question."""
    if lang == "pidgin":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, I dey pay rent", callback_data=BTN_YES)],
            [InlineKeyboardButton("❌ No, I no dey pay rent", callback_data=BTN_NO)],
            [InlineKeyboardButton("🏠 I own my house", callback_data=BTN_OWN_HOME)],
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, I pay rent", callback_data=BTN_YES)],
        [InlineKeyboardButton("❌ No, I don't pay rent", callback_data=BTN_NO)],
        [InlineKeyboardButton("🏠 I own my home", callback_data=BTN_OWN_HOME)],
    ])


def period_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Monthly or Annually income entry."""
    if lang == "pidgin":
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📅 Monthly", callback_data=BTN_MONTHLY),
                InlineKeyboardButton("📆 Per Year", callback_data=BTN_ANNUALLY),
            ]
        ])
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 Monthly", callback_data=BTN_MONTHLY),
            InlineKeyboardButton("📆 Annually", callback_data=BTN_ANNUALLY),
        ]
    ])


def result_actions_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Action buttons shown after a tax result."""
    if lang == "pidgin":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📉 How to reduce my tax", callback_data=RESULT_REDUCE)],
            [InlineKeyboardButton("🔍 Explain this result", callback_data=RESULT_EXPLAIN)],
            [InlineKeyboardButton("🔄 Calculate again", callback_data=RESULT_AGAIN)],
            [InlineKeyboardButton("📤 Share this result", callback_data=RESULT_SHARE)],
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📉 How to reduce my tax", callback_data=RESULT_REDUCE)],
        [InlineKeyboardButton("🔍 Explain this result", callback_data=RESULT_EXPLAIN)],
        [InlineKeyboardButton("🔄 Calculate again", callback_data=RESULT_AGAIN)],
        [InlineKeyboardButton("📤 Share this result", callback_data=RESULT_SHARE)],
    ])


def help_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Help topics keyboard."""
    if lang == "pidgin":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💼 Wetin be PAYE?", callback_data=HELP_PAYE)],
            [InlineKeyboardButton("📊 Wetin be Chargeable Income?", callback_data=HELP_CHARGEABLE)],
            [InlineKeyboardButton("🏡 Wetin be Rent Relief?", callback_data=HELP_RENT_RELIEF)],
            [InlineKeyboardButton("🎉 Why my tax dey zero?", callback_data=HELP_WHY_ZERO)],
            [InlineKeyboardButton("💳 How I go pay my tax?", callback_data=HELP_PAY_TAX)],
            [InlineKeyboardButton("⚠️ My oga no dey remit PAYE", callback_data=HELP_NONREMITTANCE)],
            [InlineKeyboardButton("📞 Contact NRS", callback_data=HELP_NRS)],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data=BACK_MAIN)],
        ])
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 What is PAYE?", callback_data=HELP_PAYE)],
        [InlineKeyboardButton("📊 What is Chargeable Income?", callback_data=HELP_CHARGEABLE)],
        [InlineKeyboardButton("🏡 What is Rent Relief?", callback_data=HELP_RENT_RELIEF)],
        [InlineKeyboardButton("🎉 Why is my tax zero?", callback_data=HELP_WHY_ZERO)],
        [InlineKeyboardButton("💳 How do I pay my tax?", callback_data=HELP_PAY_TAX)],
        [InlineKeyboardButton("⚠️ Employer not remitting PAYE", callback_data=HELP_NONREMITTANCE)],
        [InlineKeyboardButton("📞 Contact NRS", callback_data=HELP_NRS)],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data=BACK_MAIN)],
    ])


def back_to_help_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Single back button returning to help menu."""
    label = "🔙 Back to Help" if lang == "en" else "🔙 Back to Help"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=MENU_HELP)]
    ])
