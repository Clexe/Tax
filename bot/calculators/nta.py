"""
Nigeria Tax Act (NTA) 2025 — Core Tax Calculation Logic.
Effective January 1, 2026. Replaces PITA completely.

All functions are pure — no side effects, no DB calls, no bot imports.
"""

from __future__ import annotations

# NTA 2025 progressive tax bands.
# Each tuple: (band_size, rate)
# Applied sequentially to chargeable income.
TAX_BANDS: list[tuple[float, float]] = [
    (800_000.0,       0.00),   # First ₦800,000 @ 0%  (tax-free threshold)
    (2_200_000.0,     0.15),   # Next  ₦2,200,000 @ 15%
    (6_000_000.0,     0.18),   # Next  ₦6,000,000 @ 18%
    (4_000_000.0,     0.21),   # Next  ₦4,000,000 @ 21%
    (12_000_000.0,    0.23),   # Next  ₦12,000,000 @ 23%
    (25_000_000.0,    0.23),   # Next  ₦25,000,000 @ 23%
    (float("inf"),    0.25),   # Above ₦50,000,000 @ 25%
]

BAND_LABELS: list[str] = [
    "First ₦800,000",
    "Next ₦2,200,000",
    "Next ₦6,000,000",
    "Next ₦4,000,000",
    "Next ₦12,000,000",
    "Next ₦25,000,000",
    "Above ₦50,000,000",
]

# Cumulative upper boundary of each band (for label reference)
BAND_CUMULATIVE_UPPER: list[float] = [
    800_000.0,
    3_000_000.0,
    9_000_000.0,
    13_000_000.0,
    25_000_000.0,
    50_000_000.0,
    float("inf"),
]


def calculate_tax(chargeable_income: float, gross_annual: float) -> dict:
    """
    Apply NTA 2025 progressive bands to chargeable income.

    No minimum tax under NTA 2025.
    The 0% first band (₦800,000) ensures incomes at or below the threshold
    naturally produce zero tax — no special-casing needed.

    Args:
        chargeable_income: Income after all reliefs/deductions. Floor at 0.
        gross_annual: Total gross annual income (used for effective rate only).

    Returns a dict with:
        annual_tax (float): Total annual tax payable.
        monthly_paye (float): annual_tax / 12.
        effective_rate (float): (annual_tax / gross_annual) * 100, rounded to 2 dp.
        bands (list[dict]): Each used band — {label, amount, rate, tax}.
        is_exempt (bool): True if chargeable_income <= 800,000 (tax = 0 due to 0% band).
    """
    if gross_annual <= 0 or chargeable_income <= 0:
        return {
            "annual_tax": 0.0,
            "monthly_paye": 0.0,
            "effective_rate": 0.0,
            "bands": [],
            "is_exempt": True,
        }

    annual_tax = 0.0
    bands_used: list[dict] = []
    remaining = chargeable_income

    for (band_size, rate), label in zip(TAX_BANDS, BAND_LABELS):
        if remaining <= 0:
            break
        taxable = min(remaining, band_size)
        band_tax = taxable * rate
        annual_tax += band_tax
        bands_used.append({
            "label": label,
            "amount": taxable,
            "rate": rate,
            "tax": band_tax,
        })
        remaining -= taxable

    is_exempt = chargeable_income <= 800_000.0

    effective_rate = 0.0
    if gross_annual > 0:
        effective_rate = round((annual_tax / gross_annual) * 100, 2)

    return {
        "annual_tax": annual_tax,
        "monthly_paye": annual_tax / 12.0,
        "effective_rate": effective_rate,
        "bands": bands_used,
        "is_exempt": is_exempt,
    }
