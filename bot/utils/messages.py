"""
Bilingual message registry for NaijaTax Bot.

Every user-facing string lives here. Never hardcode strings in handler files.
Always call get_msg(key, lang) to retrieve a string.

Languages: "en" (English) and "pidgin" (Nigerian Pidgin).
Pidgin is written as natural, conversational Naija — not just English with
a few words swapped.
"""

from __future__ import annotations

MESSAGES: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------------ #
    # Start / Language                                                      #
    # ------------------------------------------------------------------ #
    "welcome": {
        "en": (
            "👋 Welcome to <b>NaijaTax Bot</b> 🇳🇬\n\n"
            "I help Nigerian workers understand and calculate their "
            "Personal Income Tax under the <b>Nigeria Tax Act (NTA) 2025</b> "
            "— the law that took effect on January 1, 2026.\n\n"
            "Please choose your preferred language:"
        ),
        "pidgin": (
            "👋 Welcome to <b>NaijaTax Bot</b> 🇳🇬\n\n"
            "I go help you calculate your Personal Income Tax according to "
            "the new <b>Nigeria Tax Act (NTA) 2025</b> wey don start January 1, 2026.\n\n"
            "Oya, pick the language wey you want:"
        ),
    },
    "language_set_en": {
        "en": "✅ Language set to <b>English</b>.",
        "pidgin": "✅ Language set to <b>English</b>.",
    },
    "language_set_pidgin": {
        "en": "✅ Language don change to <b>Pidgin</b>.",
        "pidgin": "✅ Language don change to <b>Pidgin</b>.",
    },
    "main_menu": {
        "en": (
            "🏠 <b>Main Menu</b>\n\n"
            "What would you like to do today?\n\n"
            "💼 <b>Salaried</b> — calculate tax on your employment income\n"
            "🧾 <b>Self-Employed</b> — calculate tax on your business income\n"
            "🔍 <b>Checker</b> — verify your employer's PAYE deductions\n"
            "❓ <b>Help</b> — learn about Nigerian tax terms\n"
            "🌍 <b>Language</b> — change your language"
        ),
        "pidgin": (
            "🏠 <b>Main Menu</b>\n\n"
            "Wetin you wan do today?\n\n"
            "💼 <b>Salaried</b> — calculate tax for salary worker\n"
            "🧾 <b>Self-Employed</b> — calculate tax for your business\n"
            "🔍 <b>Checker</b> — check whether your oga dey deduct correct PAYE\n"
            "❓ <b>Help</b> — learn wetin different tax words mean\n"
            "🌍 <b>Language</b> — change language"
        ),
    },
    # ------------------------------------------------------------------ #
    # Salaried Flow                                                         #
    # ------------------------------------------------------------------ #
    "ask_basic_salary": {
        "en": (
            "💼 <b>Step 1 — Basic Salary</b>\n\n"
            "What is your <b>monthly basic salary</b>?\n\n"
            "Enter the amount in Naira (e.g. <code>150000</code> or <code>150k</code>):"
        ),
        "pidgin": (
            "💼 <b>Step 1 — Basic Salary</b>\n\n"
            "How much your oga dey pay you as basic salary every month?\n\n"
            "Enter the amount (e.g. <code>150000</code> or <code>150k</code>):"
        ),
    },
    "ask_housing": {
        "en": (
            "🏠 <b>Step 2 — Housing Allowance</b>\n\n"
            "What is your <b>monthly housing allowance</b>?\n\n"
            "Tap <b>Skip</b> if you don't receive a housing allowance."
        ),
        "pidgin": (
            "🏠 <b>Step 2 — Housing Allowance</b>\n\n"
            "How much your oga dey give you as housing allowance every month?\n\n"
            "Tap <b>Skip</b> if you no dey collect housing allowance."
        ),
    },
    "ask_transport": {
        "en": (
            "🚗 <b>Step 3 — Transport Allowance</b>\n\n"
            "What is your <b>monthly transport allowance</b>?\n\n"
            "Tap <b>Skip</b> if you don't receive a transport allowance."
        ),
        "pidgin": (
            "🚗 <b>Step 3 — Transport Allowance</b>\n\n"
            "How much your oga dey give you for transport every month?\n\n"
            "Tap <b>Skip</b> if you no get transport allowance."
        ),
    },
    "ask_other": {
        "en": (
            "➕ <b>Step 4 — Other Allowances</b>\n\n"
            "Do you receive any other monthly allowances?\n"
            "(e.g. meal, utility, leave allowances)\n\n"
            "Enter the <b>total monthly amount</b>, or tap <b>Skip</b> if none."
        ),
        "pidgin": (
            "➕ <b>Step 4 — Other Allowances</b>\n\n"
            "Any other allowance wey your oga dey pay you every month?\n"
            "(e.g. food, light, leave allowance)\n\n"
            "Enter the total monthly amount, or tap <b>Skip</b> if you no get."
        ),
    },
    "ask_rent": {
        "en": (
            "🏡 <b>Step 5 — Rent Relief</b>\n\n"
            "Under NTA 2025, if you <b>pay rent</b>, you can deduct "
            "20% of your annual rent (up to ₦500,000).\n\n"
            "Do you pay rent for your home?"
        ),
        "pidgin": (
            "🏡 <b>Step 5 — Rent Relief</b>\n\n"
            "Under the new NTA 2025 law, if you <b>dey pay house rent</b>, "
            "you fit reduce your tax by 20% of your annual rent "
            "(maximum ₦500,000).\n\n"
            "You dey pay house rent?"
        ),
    },
    "ask_rent_amount": {
        "en": (
            "🏡 <b>Monthly Rent Amount</b>\n\n"
            "How much do you pay in rent each month?\n\n"
            "Enter the amount in Naira (e.g. <code>80000</code> or <code>80k</code>):"
        ),
        "pidgin": (
            "🏡 <b>Monthly Rent</b>\n\n"
            "How much you dey pay as rent every month?\n\n"
            "Enter the amount (e.g. <code>80000</code> or <code>80k</code>):"
        ),
    },
    "ask_pension": {
        "en": (
            "🏦 <b>Step 6 — Pension Contribution</b>\n\n"
            "Do you contribute to a pension fund (PFA)?\n\n"
            "If yes, 8% of your basic + housing + transport will be deducted."
        ),
        "pidgin": (
            "🏦 <b>Step 6 — Pension Contribution</b>\n\n"
            "You dey contribute to pension fund (PFA)?\n\n"
            "If yes, we go deduct 8% of your basic + housing + transport salary."
        ),
    },
    "ask_nhf": {
        "en": (
            "🏘️ <b>Step 7 — National Housing Fund (NHF)</b>\n\n"
            "Do you contribute to the National Housing Fund?\n\n"
            "If yes, 2.5% of your annual basic salary will be deducted."
        ),
        "pidgin": (
            "🏘️ <b>Step 7 — National Housing Fund (NHF)</b>\n\n"
            "You dey contribute to National Housing Fund?\n\n"
            "If yes, we go deduct 2.5% of your annual basic salary."
        ),
    },
    "ask_nhis": {
        "en": (
            "🏥 <b>Step 8 — NHIS (Health Insurance)</b>\n\n"
            "Do you pay into the National Health Insurance Scheme (NHIS)?"
        ),
        "pidgin": (
            "🏥 <b>Step 8 — NHIS (Health Insurance)</b>\n\n"
            "You dey pay into National Health Insurance Scheme (NHIS)?"
        ),
    },
    "ask_nhis_amount": {
        "en": (
            "🏥 <b>Monthly NHIS Contribution</b>\n\n"
            "How much do you contribute to NHIS each month?\n\n"
            "Enter the monthly amount in Naira:"
        ),
        "pidgin": (
            "🏥 <b>Monthly NHIS Contribution</b>\n\n"
            "How much you dey pay for NHIS every month?\n\n"
            "Enter the monthly amount:"
        ),
    },
    "ask_life": {
        "en": (
            "📋 <b>Step 9 — Life Assurance</b>\n\n"
            "Do you have a life assurance (life insurance) policy?\n\n"
            "Under NTA 2025, premiums up to ₦100,000 per year are deductible."
        ),
        "pidgin": (
            "📋 <b>Step 9 — Life Assurance</b>\n\n"
            "You get life assurance policy?\n\n"
            "Under NTA 2025, you fit deduct up to ₦100,000 of your annual premium."
        ),
    },
    "ask_life_amount": {
        "en": (
            "📋 <b>Annual Life Assurance Premium</b>\n\n"
            "What is your annual life assurance premium?\n\n"
            "Enter the annual amount in Naira:\n"
            "<i>(Maximum deductible: ₦100,000)</i>"
        ),
        "pidgin": (
            "📋 <b>Annual Life Assurance Premium</b>\n\n"
            "How much you dey pay for life assurance every year?\n\n"
            "Enter the annual amount:\n"
            "<i>(Maximum deductible: ₦100,000)</i>"
        ),
    },
    # ------------------------------------------------------------------ #
    # Self-Employed Flow                                                    #
    # ------------------------------------------------------------------ #
    "ask_period": {
        "en": (
            "🧾 <b>Self-Employed Tax Calculator</b>\n\n"
            "How would you like to enter your income?"
        ),
        "pidgin": (
            "🧾 <b>Self-Employed Tax Calculator</b>\n\n"
            "How you wan enter your income?"
        ),
    },
    "ask_income_monthly": {
        "en": (
            "💰 <b>Monthly Business Income</b>\n\n"
            "What is your total <b>monthly</b> business income?\n\n"
            "Enter the amount in Naira:"
        ),
        "pidgin": (
            "💰 <b>Monthly Business Income</b>\n\n"
            "How much your business dey bring in every month?\n\n"
            "Enter the amount:"
        ),
    },
    "ask_income_annual": {
        "en": (
            "💰 <b>Annual Business Income</b>\n\n"
            "What is your total <b>annual</b> business income?\n\n"
            "Enter the amount in Naira:"
        ),
        "pidgin": (
            "💰 <b>Annual Business Income</b>\n\n"
            "How much your business don bring in for this year?\n\n"
            "Enter the amount:"
        ),
    },
    "ask_expenses": {
        "en": (
            "📊 <b>Business Expenses</b>\n\n"
            "Do you have deductible business expenses?\n"
            "(e.g. rent, equipment, salaries paid to staff, transport for business)\n\n"
            "These will be subtracted from your income before tax."
        ),
        "pidgin": (
            "📊 <b>Business Expenses</b>\n\n"
            "You get business expenses wey you fit deduct?\n"
            "(e.g. rent, equipment, staff salary, business transport)\n\n"
            "We go minus them from your income before we calculate tax."
        ),
    },
    "ask_expenses_amount": {
        "en": (
            "📊 <b>Total Annual Business Expenses</b>\n\n"
            "What are your total annual business expenses?\n\n"
            "Enter the total annual amount in Naira:"
        ),
        "pidgin": (
            "📊 <b>Total Annual Business Expenses</b>\n\n"
            "How much you spend for your business in one year total?\n\n"
            "Enter the annual amount:"
        ),
    },
    # ------------------------------------------------------------------ #
    # Checker Flow                                                          #
    # ------------------------------------------------------------------ #
    "ask_employer_deduction": {
        "en": (
            "🔍 <b>Employer's PAYE Deduction</b>\n\n"
            "How much does your employer currently deduct from your salary "
            "as PAYE (tax) each month?\n\n"
            "Check your payslip and enter the monthly PAYE amount:"
        ),
        "pidgin": (
            "🔍 <b>Employer PAYE Deduction</b>\n\n"
            "How much your oga dey deduct from your salary every month as PAYE (tax)?\n\n"
            "Check your payslip, then enter the monthly PAYE amount:"
        ),
    },
    "checker_overpaying": {
        "en": (
            "⚠️ <b>POSSIBLE OVERPAYMENT DETECTED</b>\n\n"
            "Based on our calculation:\n"
            "• Your correct monthly PAYE: <b>{calculated}</b>\n"
            "• Your employer deducts: <b>{employer}</b>\n\n"
            "You may be <b>OVERPAYING by {diff} per month</b> "
            "(₦{diff_annual} per year).\n\n"
            "Speak to your HR/payroll department and request a tax reconciliation. "
            "You may be entitled to a refund."
        ),
        "pidgin": (
            "⚠️ <b>E LOOK LIKE YOU DEY OVERPAY TAX!</b>\n\n"
            "According to our calculation:\n"
            "• Correct monthly PAYE: <b>{calculated}</b>\n"
            "• Your oga dey deduct: <b>{employer}</b>\n\n"
            "You fit don dey <b>OVERPAY by {diff} every month</b> "
            "(₦{diff_annual} per year).\n\n"
            "Go meet your HR or payroll people make dem explain. "
            "You fit get refund."
        ),
    },
    "checker_underpaying": {
        "en": (
            "⚠️ <b>POSSIBLE UNDER-REMITTANCE DETECTED</b>\n\n"
            "Based on our calculation:\n"
            "• Your correct monthly PAYE: <b>{calculated}</b>\n"
            "• Your employer deducts: <b>{employer}</b>\n\n"
            "Your employer may be <b>UNDER-REMITTING by {diff} per month</b>.\n\n"
            "This is a tax compliance issue. If discovered by the tax authority, "
            "you may be held liable for underpaid taxes. "
            "Alert your payroll department."
        ),
        "pidgin": (
            "⚠️ <b>YOUR OGA FIT BE UNDER-PAYING YOUR TAX!</b>\n\n"
            "According to our calculation:\n"
            "• Correct monthly PAYE: <b>{calculated}</b>\n"
            "• Your oga dey deduct: <b>{employer}</b>\n\n"
            "Your oga fit dey <b>UNDER-REMIT by {diff} every month</b>.\n\n"
            "This na compliance problem. If tax authority catch am, "
            "you sef fit get wahala. Tell your payroll people."
        ),
    },
    "checker_correct": {
        "en": (
            "✅ <b>DEDUCTION LOOKS CORRECT</b>\n\n"
            "Based on our calculation:\n"
            "• Your correct monthly PAYE: <b>{calculated}</b>\n"
            "• Your employer deducts: <b>{employer}</b>\n\n"
            "The difference is within ₦500 — your employer's deduction "
            "appears to be correct."
        ),
        "pidgin": (
            "✅ <b>YOUR OGA DEY DEDUCT CORRECT!</b>\n\n"
            "According to our calculation:\n"
            "• Correct monthly PAYE: <b>{calculated}</b>\n"
            "• Your oga dey deduct: <b>{employer}</b>\n\n"
            "The difference dey within ₦500 — everything look correct."
        ),
    },
    # ------------------------------------------------------------------ #
    # Errors / System Messages                                              #
    # ------------------------------------------------------------------ #
    "invalid_amount": {
        "en": (
            "❌ That doesn't look like a valid amount.\n\n"
            "Please enter a number, e.g.:\n"
            "• <code>150000</code>\n"
            "• <code>150k</code>\n"
            "• <code>1.5m</code>\n"
            "• <code>₦150,000</code>"
        ),
        "pidgin": (
            "❌ Abeg enter number, I no understand wetin you write.\n\n"
            "Try am like this:\n"
            "• <code>150000</code>\n"
            "• <code>150k</code>\n"
            "• <code>1.5m</code>\n"
            "• <code>₦150,000</code>"
        ),
    },
    "calculating": {
        "en": "⏳ Calculating your tax...",
        "pidgin": "⏳ I dey calculate your tax...",
    },
    "cancelled": {
        "en": (
            "✅ No problem, we've started over.\n\n"
            "Use /start to begin again."
        ),
        "pidgin": (
            "✅ No wahala, we don start from beginning.\n\n"
            "Use /start to try again."
        ),
    },
    "error": {
        "en": (
            "😕 Something went wrong. Please try again.\n\n"
            "Use /start to restart from the beginning."
        ),
        "pidgin": (
            "😕 E get wahala. Abeg try again.\n\n"
            "Use /start to begin fresh."
        ),
    },
    # ------------------------------------------------------------------ #
    # Help Flow                                                             #
    # ------------------------------------------------------------------ #
    "help_menu": {
        "en": "❓ <b>Help & FAQs</b>\n\nWhat would you like to know about?",
        "pidgin": "❓ <b>Help & FAQs</b>\n\nWetin you wan understand?",
    },
    "help_paye_text": {
        "en": (
            "💼 <b>What is PAYE?</b>\n\n"
            "PAYE stands for <b>Pay As You Earn</b>. It is the system by which "
            "your employer deducts income tax from your salary every month and "
            "remits it to the government on your behalf.\n\n"
            "Your employer calculates your annual tax, divides it by 12, and "
            "deducts that amount from your monthly payslip. You don't have to "
            "pay it yourself — your employer does it for you.\n\n"
            "Under NTA 2025, PAYE is still the main mechanism for taxing "
            "employment income in Nigeria."
        ),
        "pidgin": (
            "💼 <b>Wetin be PAYE?</b>\n\n"
            "PAYE means <b>Pay As You Earn</b>. Na the system wey your oga "
            "dey use to deduct income tax from your salary every month and "
            "pay am go government for your behalf.\n\n"
            "Your oga go calculate your annual tax, divide am by 12, then "
            "deduct that amount from your salary every month. You no go pay "
            "am yourself — your oga go do am for you.\n\n"
            "Under NTA 2025, PAYE still dey work the same way for salary workers."
        ),
    },
    "help_chargeable_text": {
        "en": (
            "📊 <b>What is Chargeable Income?</b>\n\n"
            "Chargeable income is the portion of your income on which tax "
            "is actually calculated. It is derived by subtracting your "
            "deductions and reliefs from your gross income.\n\n"
            "<b>Formula:</b>\n"
            "Gross Annual Income\n"
            "− Rent Relief (if applicable)\n"
            "− Pension Contribution (if opted in)\n"
            "− NHF (if opted in)\n"
            "− NHIS (if opted in)\n"
            "− Life Assurance Premium (if applicable)\n"
            "= <b>Chargeable Income</b>\n\n"
            "Under NTA 2025, the first ₦800,000 of chargeable income is "
            "tax-free (taxed at 0%). So if your chargeable income is at "
            "or below ₦800,000, you owe no tax at all."
        ),
        "pidgin": (
            "📊 <b>Wetin be Chargeable Income?</b>\n\n"
            "Chargeable income na the part of your money wey dem go calculate "
            "tax on. You go minus your reliefs and deductions from your gross "
            "income to get am.\n\n"
            "<b>How to calculate am:</b>\n"
            "Gross Annual Income\n"
            "− Rent Relief (if you dey rent)\n"
            "− Pension (if you dey contribute)\n"
            "− NHF (if you dey contribute)\n"
            "− NHIS (if you dey pay)\n"
            "− Life Assurance Premium (if you get)\n"
            "= <b>Chargeable Income</b>\n\n"
            "Under NTA 2025, the first ₦800,000 no get tax (0%). So if your "
            "chargeable income no reach ₦800,000, you no go pay any tax at all."
        ),
    },
    "help_rent_relief_text": {
        "en": (
            "🏡 <b>What is Rent Relief?</b>\n\n"
            "Rent Relief is a new deduction introduced by the Nigeria Tax Act "
            "(NTA) 2025. It <b>replaces the old Consolidated Relief Allowance "
            "(CRA)</b> which has been abolished.\n\n"
            "<b>How it works:</b>\n"
            "• You can deduct <b>20% of your annual rent</b> from your "
            "taxable income.\n"
            "• The maximum deduction is <b>₦500,000 per year</b>.\n"
            "• You must actually be paying rent — this relief does not apply "
            "if you own your home or live rent-free.\n\n"
            "<b>Example:</b>\n"
            "Monthly rent = ₦100,000 → Annual = ₦1,200,000\n"
            "20% of ₦1,200,000 = ₦240,000 relief (under the ₦500,000 cap)\n\n"
            "Monthly rent = ₦300,000 → Annual = ₦3,600,000\n"
            "20% of ₦3,600,000 = ₦720,000 → Capped at ₦500,000"
        ),
        "pidgin": (
            "🏡 <b>Wetin be Rent Relief?</b>\n\n"
            "Rent Relief na new deduction wey the Nigeria Tax Act (NTA) 2025 "
            "introduce. Im <b>replace the old Consolidated Relief Allowance "
            "(CRA)</b> wey dem don abolish.\n\n"
            "<b>How im work:</b>\n"
            "• You fit deduct <b>20% of your annual rent</b> from your "
            "taxable income.\n"
            "• Maximum deduction na <b>₦500,000 per year</b>.\n"
            "• You must dey actually pay rent — this relief no work if you "
            "own your house or dey live free.\n\n"
            "<b>Example:</b>\n"
            "Monthly rent = ₦100,000 → Annual = ₦1,200,000\n"
            "20% of ₦1,200,000 = ₦240,000 relief\n\n"
            "Monthly rent = ₦300,000 → Annual = ₦3,600,000\n"
            "20% of ₦3,600,000 = ₦720,000 → Capped at ₦500,000"
        ),
    },
    "help_why_zero_text": {
        "en": (
            "🎉 <b>Why is my tax zero?</b>\n\n"
            "Under the <b>Nigeria Tax Act (NTA) 2025</b>, the first <b>₦800,000</b> "
            "of chargeable income is tax-free. This is called the <b>tax-free "
            "threshold</b>.\n\n"
            "If your chargeable income (gross income minus all your deductions) "
            "is at or below ₦800,000, your tax is <b>₦0</b>.\n\n"
            "This threshold was introduced to exempt minimum wage earners and "
            "low-income workers from paying any income tax, giving more money "
            "in the hands of those who earn the least.\n\n"
            "Note: This is the first band in the NTA 2025 tax table. It is "
            "built into the progressive tax bands, not a separate exemption."
        ),
        "pidgin": (
            "🎉 <b>Why my tax dey zero?</b>\n\n"
            "Under the new <b>Nigeria Tax Act (NTA) 2025</b>, the first "
            "<b>₦800,000</b> of chargeable income no get tax (0%). "
            "Dem call am <b>tax-free threshold</b>.\n\n"
            "If your chargeable income (your income minus all your deductions) "
            "no reach ₦800,000, your tax na <b>₦0</b>.\n\n"
            "Government introduce this one to help low-income workers and "
            "minimum wage earners — make dem no pay income tax at all.\n\n"
            "This na the first band for the NTA 2025 tax table."
        ),
    },
    "help_pay_tax_text": {
        "en": (
            "💳 <b>How do I pay my tax?</b>\n\n"
            "For most <b>employees</b>, you don't need to pay tax yourself. "
            "Your employer deducts PAYE from your salary every month and pays "
            "it to your State Internal Revenue Service (SIRS) on your behalf.\n\n"
            "For <b>self-employed persons</b>, you must:\n"
            "1. Register with your State Internal Revenue Service\n"
            "2. File an annual self-assessment tax return\n"
            "3. Pay tax in quarterly instalments\n\n"
            "The tax is paid to your <b>State Internal Revenue Service (SIRS)</b> "
            "— not directly to the NRS (Nigeria Revenue Service). Personal income "
            "tax goes to the state where you reside."
        ),
        "pidgin": (
            "💳 <b>How I go pay my tax?</b>\n\n"
            "If you be <b>salary worker</b>, you no need to pay tax yourself. "
            "Your oga go deduct PAYE from your salary every month and pay am "
            "go State Internal Revenue Service (SIRS) for your behalf.\n\n"
            "If you be <b>self-employed</b>, you must:\n"
            "1. Register with your State Internal Revenue Service\n"
            "2. File annual self-assessment tax return\n"
            "3. Pay tax every quarter\n\n"
            "The tax go to your <b>State Internal Revenue Service (SIRS)</b> "
            "— not NRS directly. Personal income tax go to the state where you dey live."
        ),
    },
    "help_nonremittance_text": {
        "en": (
            "⚠️ <b>What if my employer doesn't remit my PAYE?</b>\n\n"
            "If your employer deducts PAYE from your salary but does not remit "
            "it to the State Revenue Service, this is a <b>serious offence</b> "
            "under Nigerian tax law.\n\n"
            "<b>What you can do:</b>\n"
            "1. Request your payslips showing PAYE deductions\n"
            "2. File a complaint with your State Internal Revenue Service (SIRS)\n"
            "3. Contact the Nigeria Revenue Service (NRS): www.nrs.gov.ng\n\n"
            "As an employee, you are not personally liable for your employer's "
            "failure to remit, provided you can show tax was deducted. "
            "However, you should act promptly."
        ),
        "pidgin": (
            "⚠️ <b>Wetin if my oga no dey pay my PAYE go government?</b>\n\n"
            "If your oga dey deduct PAYE from your salary but no dey pay am "
            "go State Revenue Service, na <b>serious offence</b> under Nigerian tax law.\n\n"
            "<b>Wetin you fit do:</b>\n"
            "1. Ask for your payslips wey show PAYE deductions\n"
            "2. File complaint with your State Internal Revenue Service (SIRS)\n"
            "3. Contact Nigeria Revenue Service (NRS): www.nrs.gov.ng\n\n"
            "As employee, dem no go hold you responsible for your oga failure to "
            "remit, as long as you fit show say dem don deduct tax. But act fast."
        ),
    },
    "help_nrs_text": {
        "en": (
            "📞 <b>Contact NRS (Nigeria Revenue Service)</b>\n\n"
            "The Nigeria Revenue Service (NRS) is the federal tax authority "
            "that replaced FIRS under the NTA 2025.\n\n"
            "🌐 Website: <a href='https://www.nrs.gov.ng'>www.nrs.gov.ng</a>\n\n"
            "<i>Note: For personal income tax queries, contact your "
            "<b>State Internal Revenue Service (SIRS)</b> first — personal "
            "income tax is administered at the state level.</i>"
        ),
        "pidgin": (
            "📞 <b>Contact NRS (Nigeria Revenue Service)</b>\n\n"
            "Nigeria Revenue Service (NRS) na the federal tax authority wey "
            "replace FIRS under NTA 2025.\n\n"
            "🌐 Website: <a href='https://www.nrs.gov.ng'>www.nrs.gov.ng</a>\n\n"
            "<i>Note: For personal income tax, go your "
            "<b>State Internal Revenue Service (SIRS)</b> first — na state "
            "government dey handle personal income tax.</i>"
        ),
    },
    # ------------------------------------------------------------------ #
    # Admin                                                                 #
    # ------------------------------------------------------------------ #
    "admin_not_authorized": {
        "en": "Unknown command.",
        "pidgin": "Unknown command.",
    },
    "admin_header": {
        "en": "📊 <b>NaijaTax Bot — Admin Dashboard</b>",
        "pidgin": "📊 <b>NaijaTax Bot — Admin Dashboard</b>",
    },
}


def get_msg(key: str, lang: str) -> str:
    """
    Retrieve a message string for the given key and language.

    Falls back to 'en' if the key is missing in the requested language.
    Returns a [missing: key] placeholder if the key doesn't exist at all.

    Args:
        key: The message key (e.g. "welcome", "ask_basic_salary").
        lang: Language code — "en" or "pidgin".

    Returns:
        The message string.
    """
    entry = MESSAGES.get(key)
    if entry is None:
        return f"[missing message: {key}]"
    return entry.get(lang) or entry.get("en") or f"[missing: {key}/{lang}]"
