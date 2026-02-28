"""
NTA 2025 Relief and Deduction Calculations.

Key changes from old PITA:
- CRA (Consolidated Relief Allowance) is ABOLISHED. Do not implement.
- Rent Relief replaces CRA: 20% of annual rent, capped at ₦500,000.
- Life Assurance deduction capped at ₦100,000.

All functions are pure — no side effects, no DB calls, no bot imports.
"""

from __future__ import annotations

RENT_RELIEF_RATE = 0.20
RENT_RELIEF_CAP = 500_000.0

PENSION_RATE = 0.08
NHF_RATE = 0.025
LIFE_ASSURANCE_CAP = 100_000.0


def calculate_rent_relief(annual_rent: float) -> float:
    """
    Rent Relief = 20% of annual rent actually paid, capped at ₦500,000.
    Returns 0.0 if annual_rent == 0 (user owns home or does not pay rent).
    """
    if annual_rent <= 0:
        return 0.0
    return min(annual_rent * RENT_RELIEF_RATE, RENT_RELIEF_CAP)


def calculate_pension(
    annual_basic: float,
    annual_housing: float,
    annual_transport: float,
) -> float:
    """
    Employee pension contribution = 8% of qualifying emoluments.
    Qualifying emoluments = basic + housing + transport (NOT other allowances).
    Based on Pension Reform Act.
    """
    return PENSION_RATE * (annual_basic + annual_housing + annual_transport)


def calculate_pension_selfemployed(net_income: float) -> float:
    """
    Self-employed pension contribution = 8% of net income.
    No qualifying emolument split for self-employed persons.
    """
    if net_income <= 0:
        return 0.0
    return PENSION_RATE * net_income


def calculate_nhf(annual_basic: float) -> float:
    """
    National Housing Fund contribution = 2.5% of annual basic salary ONLY.
    NHF is calculated on basic salary, not on total emoluments.
    """
    if annual_basic <= 0:
        return 0.0
    return NHF_RATE * annual_basic


def calculate_life_assurance_deduction(annual_premium: float) -> float:
    """
    Life assurance premium deduction, capped at ₦100,000 under NTA 2025.
    Returns min(annual_premium, 100_000).
    """
    if annual_premium <= 0:
        return 0.0
    return min(annual_premium, LIFE_ASSURANCE_CAP)


def calculate_chargeable_income(
    gross_annual: float,
    rent_relief: float = 0.0,
    pension: float = 0.0,
    nhf: float = 0.0,
    nhis_annual: float = 0.0,
    life_assurance: float = 0.0,
) -> float:
    """
    Chargeable Income = Gross Annual Income - all reliefs and deductions.
    Floors at ₦0 — never negative.

    Order of deduction (as per NTA 2025):
      1. Rent Relief
      2. Pension Contribution
      3. NHF Contribution
      4. NHIS Contribution
      5. Life Assurance Premium (capped at ₦100,000)
    """
    total_deductions = rent_relief + pension + nhf + nhis_annual + life_assurance
    return max(0.0, gross_annual - total_deductions)
