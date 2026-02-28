"""
Result formatter for NaijaTax Bot.

Builds the HTML-formatted tax summary message using <pre> tags for monospace.
Uses HTML parse_mode — avoids MarkdownV2 which requires escaping ₦, dashes, etc.

All functions are pure — no side effects, no DB calls, no bot imports.
"""

from __future__ import annotations

SEPARATOR = "─" * 33


def fmt_naira(amount: float) -> str:
    """Format a number as ₦1,234,567 (no decimal places, comma separators)."""
    return f"₦{int(round(amount)):,}"


def fmt_rate(rate: float) -> str:
    """Format a rate like 0.15 as '15%'."""
    return f"{int(round(rate * 100))}%"


def _row(label: str, value: str, width: int = 33) -> str:
    """Build a fixed-width table row."""
    label_width = width - len(value) - 1
    return f"{label:<{label_width}} {value}"


def build_result_text(
    lang: str,
    gross_annual: float,
    rent_relief: float,
    pension: float,
    nhf: float,
    nhis_annual: float,
    life_assurance: float,
    chargeable_income: float,
    tax_result: dict,
) -> str:
    """
    Build the full HTML-formatted result message.

    If chargeable_income <= 800,000 (tax = 0 due to exemption):
        Returns a celebratory "GREAT NEWS!" message.
    Otherwise:
        Returns a full monospace table with band breakdown.

    Args:
        lang: "en" or "pidgin" (used for disclaimer language).
        gross_annual: Gross annual income.
        rent_relief: Rent relief deduction (0 if not applicable).
        pension: Pension deduction (0 if not opted in).
        nhf: NHF deduction (0 if not opted in).
        nhis_annual: Annualised NHIS deduction (0 if not opted in).
        life_assurance: Life assurance deduction after cap (0 if not opted in).
        chargeable_income: Income after all deductions (floor 0).
        tax_result: Dict returned by calculate_tax().

    Returns:
        HTML string ready to send with parse_mode="HTML".
    """
    annual_tax: float = tax_result["annual_tax"]
    monthly_paye: float = tax_result["monthly_paye"]
    effective_rate: float = tax_result["effective_rate"]
    bands: list[dict] = tax_result["bands"]

    if annual_tax == 0 and chargeable_income <= 800_000:
        if lang == "pidgin":
            return (
                "🎉 <b>E DON DO!</b>\n\n"
                "Your taxable income no reach ₦800,000 so you no go\n"
                "pay any tax under the new NTA 2025 law.\n\n"
                f"Gross Annual Income: {fmt_naira(gross_annual)}\n"
                f"Chargeable Income:   {fmt_naira(chargeable_income)}\n\n"
                "💰 Tax Owed: <b>₦0</b>\n\n"
                "<i>⚠️ Estimate only. Based on NTA 2025.\n"
                "Consult a tax professional or your\n"
                "State Internal Revenue Service.</i>"
            )
        return (
            "🎉 <b>GREAT NEWS!</b>\n\n"
            "Your chargeable income is below the\n"
            "₦800,000 tax-free threshold under\n"
            "NTA 2025. You owe ZERO income tax!\n\n"
            f"Gross Annual Income: {fmt_naira(gross_annual)}\n"
            f"Chargeable Income:   {fmt_naira(chargeable_income)}\n\n"
            "💰 Tax Owed: <b>₦0</b>\n\n"
            "<i>⚠️ Estimate only. Based on NTA 2025.\n"
            "Consult a tax professional or your\n"
            "State Internal Revenue Service.</i>"
        )

    # Build monospace table
    lines: list[str] = []
    lines.append("📊 <b>YOUR TAX SUMMARY (2026)</b>")
    lines.append("<pre>")
    lines.append(SEPARATOR)

    # Income section
    lines.append(_row("Gross Annual Income:", fmt_naira(gross_annual)))

    # Deductions — only show non-zero ones
    if rent_relief > 0:
        lines.append(_row("Less: Rent Relief (20%):", f"-{fmt_naira(rent_relief)}"))
    if pension > 0:
        lines.append(_row("Less: Pension (8%):", f"-{fmt_naira(pension)}"))
    if nhf > 0:
        lines.append(_row("Less: NHF (2.5%):", f"-{fmt_naira(nhf)}"))
    if nhis_annual > 0:
        lines.append(_row("Less: NHIS:", f"-{fmt_naira(nhis_annual)}"))
    if life_assurance > 0:
        lines.append(_row("Less: Life Assurance:", f"-{fmt_naira(life_assurance)}"))

    lines.append(SEPARATOR)
    lines.append(_row("Chargeable Income:", fmt_naira(chargeable_income)))
    lines.append("")
    lines.append("TAX BREAKDOWN")
    lines.append(SEPARATOR)

    # Band breakdown — skip 0% band if it produces 0 tax and there are taxed bands
    for band in bands:
        rate_pct = int(round(band["rate"] * 100))
        row_label = f"{fmt_naira(band['amount'])} @ {rate_pct}%"
        lines.append(_row(row_label + " =", fmt_naira(band["tax"])))

    lines.append(SEPARATOR)
    lines.append(_row("💰 Annual Tax:", fmt_naira(annual_tax)))
    lines.append(_row("📅 Monthly PAYE:", fmt_naira(monthly_paye)))
    lines.append(_row("📊 Effective Rate:", f"{effective_rate:.2f}%"))
    lines.append(SEPARATOR)
    lines.append("</pre>")

    if lang == "pidgin":
        lines.append(
            "<i>⚠️ Na estimate. Based on NTA 2025.\n"
            "Consult tax professional or your\n"
            "State Internal Revenue Service.</i>"
        )
    else:
        lines.append(
            "<i>⚠️ Estimate only. Based on NTA 2025.\n"
            "Consult a tax professional or your\n"
            "State Internal Revenue Service.</i>"
        )

    return "\n".join(lines)


def build_exempt_text(lang: str, gross_annual: float, chargeable_income: float) -> str:
    """Standalone exempt message (chargeable <= ₦800,000)."""
    if lang == "pidgin":
        return (
            "🎉 <b>E DON DO!</b>\n\n"
            "Your taxable income no reach ₦800,000 so you no go\n"
            "pay any tax under the new NTA 2025 law.\n\n"
            f"Gross Annual Income: {fmt_naira(gross_annual)}\n"
            f"Chargeable Income:   {fmt_naira(chargeable_income)}\n\n"
            "💰 Tax Owed: <b>₦0</b>\n\n"
            "<i>⚠️ Estimate only. Based on NTA 2025.</i>"
        )
    return (
        "🎉 <b>GREAT NEWS!</b>\n\n"
        "Your chargeable income is below the\n"
        "₦800,000 tax-free threshold under\n"
        "NTA 2025. You owe ZERO income tax!\n\n"
        f"Gross Annual Income: {fmt_naira(gross_annual)}\n"
        f"Chargeable Income:   {fmt_naira(chargeable_income)}\n\n"
        "💰 Tax Owed: <b>₦0</b>\n\n"
        "<i>⚠️ Estimate only. Based on NTA 2025.</i>"
    )


def build_explanation_text(lang: str, result: dict) -> str:
    """
    Build a plain-English walkthrough of each line in the result.
    result is context.user_data["last_result"].
    """
    gross = result["gross_annual"]
    rent_relief = result["rent_relief"]
    pension = result["pension"]
    nhf = result["nhf"]
    nhis_annual = result["nhis_annual"]
    life_assurance = result["life_assurance"]
    chargeable = result["chargeable_income"]
    annual_tax = result["annual_tax"]
    monthly_paye = result["monthly_paye"]
    effective_rate = result["effective_rate"]
    bands = result["bands"]

    if lang == "pidgin":
        lines = [
            "🔍 <b>HOW WE CALCULATE YOUR TAX:</b>\n",
            f"<b>1. Gross Annual Income: {fmt_naira(gross)}</b>",
            "   Na all your salary components multiplied by 12.",
        ]
        if rent_relief > 0:
            lines += [
                f"\n<b>2. Rent Relief: -{fmt_naira(rent_relief)}</b>",
                "   20% of your annual rent, maximum ₦500,000.",
                "   This na new relief under NTA 2025 (replace the old CRA).",
            ]
        if pension > 0:
            lines += [
                f"\n<b>Pension: -{fmt_naira(pension)}</b>",
                "   8% of your basic + housing + transport.",
            ]
        if nhf > 0:
            lines += [
                f"\n<b>NHF: -{fmt_naira(nhf)}</b>",
                "   2.5% of your annual basic salary.",
            ]
        if nhis_annual > 0:
            lines += [
                f"\n<b>NHIS: -{fmt_naira(nhis_annual)}</b>",
                "   Your annual NHIS contribution.",
            ]
        if life_assurance > 0:
            lines += [
                f"\n<b>Life Assurance: -{fmt_naira(life_assurance)}</b>",
                "   Your annual premium (max ₦100,000 allowed).",
            ]
        lines += [
            f"\n<b>Chargeable Income: {fmt_naira(chargeable)}</b>",
            "   Na the amount wey dem go tax.",
        ]
        if annual_tax == 0:
            lines += [
                "\n<b>Tax: ₦0</b>",
                "   Your income no reach the ₦800,000 taxable threshold.",
            ]
        else:
            lines.append("\n<b>Tax Bands:</b>")
            for band in bands:
                rate_pct = int(round(band["rate"] * 100))
                lines.append(
                    f"   {fmt_naira(band['amount'])} taxed at {rate_pct}% = {fmt_naira(band['tax'])}"
                )
            lines += [
                f"\n<b>Annual Tax: {fmt_naira(annual_tax)}</b>",
                f"<b>Monthly PAYE: {fmt_naira(monthly_paye)}</b>",
                f"<b>Effective Rate: {effective_rate:.2f}%</b>",
            ]
    else:
        lines = [
            "🔍 <b>EXPLAINING YOUR TAX CALCULATION:</b>\n",
            f"<b>1. Gross Annual Income: {fmt_naira(gross)}</b>",
            "   This is all your income components added together and",
            "   multiplied by 12 (annualised from monthly figures).",
        ]
        if rent_relief > 0:
            lines += [
                f"\n<b>2. Rent Relief: -{fmt_naira(rent_relief)}</b>",
                "   Under NTA 2025, you can deduct 20% of your annual rent,",
                "   up to a maximum of ₦500,000. This replaces the old CRA.",
            ]
        if pension > 0:
            lines += [
                f"\n<b>Pension Contribution: -{fmt_naira(pension)}</b>",
                "   8% of your basic salary + housing + transport allowances.",
            ]
        if nhf > 0:
            lines += [
                f"\n<b>NHF Contribution: -{fmt_naira(nhf)}</b>",
                "   2.5% of your annual basic salary paid to the",
                "   National Housing Fund.",
            ]
        if nhis_annual > 0:
            lines += [
                f"\n<b>NHIS Contribution: -{fmt_naira(nhis_annual)}</b>",
                "   Your annual contribution to the National Health",
                "   Insurance Scheme.",
            ]
        if life_assurance > 0:
            lines += [
                f"\n<b>Life Assurance Premium: -{fmt_naira(life_assurance)}</b>",
                "   Actual premium paid, capped at ₦100,000 under NTA 2025.",
            ]
        lines += [
            f"\n<b>Chargeable Income: {fmt_naira(chargeable)}</b>",
            "   This is your taxable income after all deductions.",
        ]
        if annual_tax == 0:
            lines += [
                "\n<b>Tax: ₦0</b>",
                "   Your chargeable income is at or below the ₦800,000",
                "   tax-free threshold under NTA 2025. No tax is owed.",
            ]
        else:
            lines.append(
                "\n<b>Tax Bands:</b>\n"
                "   Under NTA 2025, the first ₦800,000 is always tax-free (0%).\n"
                "   The remaining income is taxed at increasing rates:"
            )
            for band in bands:
                rate_pct = int(round(band["rate"] * 100))
                lines.append(
                    f"   • {fmt_naira(band['amount'])} @ {rate_pct}% = {fmt_naira(band['tax'])}"
                )
            lines += [
                f"\n<b>Annual Tax: {fmt_naira(annual_tax)}</b>",
                f"<b>Monthly PAYE: {fmt_naira(monthly_paye)}</b>",
                f"   (Annual Tax ÷ 12 months)",
                f"<b>Effective Rate: {effective_rate:.2f}%</b>",
                f"   (Annual Tax ÷ Gross Income × 100)",
            ]

    return "\n".join(lines)


def build_reduce_tax_text(lang: str) -> str:
    """Advice on how to reduce tax liability under NTA 2025."""
    if lang == "pidgin":
        return (
            "📉 <b>HOW TO REDUCE YOUR TAX UNDER NTA 2025:</b>\n\n"
            "1. <b>Pay Rent and Claim Rent Relief</b>\n"
            "   If you dey rent house, you fit deduct 20% of your\n"
            "   annual rent (maximum ₦500,000). Na the biggest relief\n"
            "   wey dey under NTA 2025.\n\n"
            "2. <b>Maximize Pension Contributions</b>\n"
            "   Your 8% employee pension contribution dey reduce\n"
            "   your taxable income.\n\n"
            "3. <b>Join NHF</b>\n"
            "   National Housing Fund contribution (2.5% of basic)\n"
            "   dey also reduce your tax.\n\n"
            "4. <b>Get Life Assurance Policy</b>\n"
            "   Premium wey you pay dey reduce your income by\n"
            "   up to ₦100,000 per year.\n\n"
            "5. <b>Enroll in NHIS</b>\n"
            "   Your NHIS contribution dey reduce your taxable income.\n\n"
            "<i>Consult a tax professional for advice specific to your situation.</i>"
        )
    return (
        "📉 <b>HOW TO REDUCE YOUR TAX UNDER NTA 2025:</b>\n\n"
        "1. <b>Claim Rent Relief</b>\n"
        "   If you pay rent, you can deduct 20% of your annual\n"
        "   rent, up to ₦500,000. This is the largest available\n"
        "   relief under NTA 2025 (replaces old CRA).\n\n"
        "2. <b>Maximize Pension Contributions</b>\n"
        "   Your 8% employee pension contribution reduces your\n"
        "   taxable income directly.\n\n"
        "3. <b>Enroll in NHF</b>\n"
        "   National Housing Fund (2.5% of basic salary) also\n"
        "   reduces your taxable income.\n\n"
        "4. <b>Get a Life Assurance Policy</b>\n"
        "   Premiums paid are deductible up to ₦100,000 per year.\n\n"
        "5. <b>Enroll in NHIS</b>\n"
        "   Your health insurance contributions reduce\n"
        "   your taxable income.\n\n"
        "<i>Consult a qualified tax professional for advice\n"
        "tailored to your specific circumstances.</i>"
    )


def build_share_text(result: dict) -> str:
    """
    Build a clean, plain-text shareable version of the result
    (no HTML, suitable for forwarding or screenshotting).
    """
    gross = result["gross_annual"]
    rent_relief = result["rent_relief"]
    pension = result["pension"]
    nhf = result["nhf"]
    nhis_annual = result["nhis_annual"]
    life_assurance = result["life_assurance"]
    chargeable = result["chargeable_income"]
    annual_tax = result["annual_tax"]
    monthly_paye = result["monthly_paye"]
    effective_rate = result["effective_rate"]

    sep = "=" * 35
    lines = [
        "NaijaTax Bot — Tax Summary (NTA 2025)",
        sep,
        f"Gross Annual Income:   {fmt_naira(gross)}",
    ]
    if rent_relief > 0:
        lines.append(f"Less: Rent Relief:     -{fmt_naira(rent_relief)}")
    if pension > 0:
        lines.append(f"Less: Pension (8%):    -{fmt_naira(pension)}")
    if nhf > 0:
        lines.append(f"Less: NHF (2.5%):      -{fmt_naira(nhf)}")
    if nhis_annual > 0:
        lines.append(f"Less: NHIS:            -{fmt_naira(nhis_annual)}")
    if life_assurance > 0:
        lines.append(f"Less: Life Assurance:  -{fmt_naira(life_assurance)}")
    lines += [
        sep,
        f"Chargeable Income:    {fmt_naira(chargeable)}",
        sep,
        f"Annual Tax:           {fmt_naira(annual_tax)}",
        f"Monthly PAYE:         {fmt_naira(monthly_paye)}",
        f"Effective Rate:       {effective_rate:.2f}%",
        sep,
        "Calculated by NaijaTax Bot (@NaijaTaxBot)",
        "Estimate only. Consult a tax professional.",
    ]
    return "\n".join(lines)
