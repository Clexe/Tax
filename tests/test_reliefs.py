"""
Tests for bot/calculators/reliefs.py — NTA 2025 relief/deduction logic.

All tests use pure functions and require no database or network access.
"""

import pytest
from bot.calculators.reliefs import (
    calculate_rent_relief,
    calculate_pension,
    calculate_pension_selfemployed,
    calculate_nhf,
    calculate_life_assurance_deduction,
    calculate_chargeable_income,
)


class TestRentRelief:
    def test_under_cap(self):
        """₦1,200,000 annual rent → 20% = ₦240,000 (below ₦500k cap)."""
        assert calculate_rent_relief(1_200_000.0) == pytest.approx(240_000.0)

    def test_exactly_at_cap_boundary(self):
        """₦2,500,000 annual rent → 20% = ₦500,000 (exactly at cap)."""
        assert calculate_rent_relief(2_500_000.0) == pytest.approx(500_000.0)

    def test_above_cap_clamped(self):
        """₦3,600,000 annual rent → 20% = ₦720,000 → capped at ₦500,000."""
        assert calculate_rent_relief(3_600_000.0) == 500_000.0

    def test_zero_rent(self):
        """No rent → zero relief."""
        assert calculate_rent_relief(0.0) == 0.0

    def test_negative_rent_treated_as_zero(self):
        """Negative annual_rent → 0.0 (guards against invalid input)."""
        assert calculate_rent_relief(-100_000.0) == 0.0

    def test_small_rent(self):
        """₦100,000 annual rent → 20% = ₦20,000."""
        assert calculate_rent_relief(100_000.0) == pytest.approx(20_000.0)

    def test_high_rent_always_capped(self):
        """Very high rent → always capped at ₦500,000."""
        assert calculate_rent_relief(10_000_000.0) == 500_000.0


class TestPension:
    def test_qualifying_emoluments_only(self):
        """Pension = 8% of (basic + housing + transport), NOT other allowances."""
        result = calculate_pension(600_000.0, 240_000.0, 120_000.0)
        expected = 0.08 * (600_000.0 + 240_000.0 + 120_000.0)
        assert result == pytest.approx(expected)

    def test_zero_inputs(self):
        """All zero emoluments → zero pension."""
        assert calculate_pension(0.0, 0.0, 0.0) == 0.0

    def test_basic_only(self):
        """Only basic salary — housing and transport zero."""
        result = calculate_pension(1_200_000.0, 0.0, 0.0)
        assert result == pytest.approx(0.08 * 1_200_000.0)

    def test_rate_is_eight_percent(self):
        """Confirm exact 8% rate."""
        result = calculate_pension(1_000_000.0, 0.0, 0.0)
        assert result == pytest.approx(80_000.0)


class TestPensionSelfEmployed:
    def test_eight_percent_of_net_income(self):
        """Self-employed pension = 8% of net income."""
        result = calculate_pension_selfemployed(2_000_000.0)
        assert result == pytest.approx(160_000.0)

    def test_zero_net_income(self):
        """Zero net income → zero pension."""
        assert calculate_pension_selfemployed(0.0) == 0.0

    def test_negative_net_income(self):
        """Negative net income (loss) → zero pension."""
        assert calculate_pension_selfemployed(-500_000.0) == 0.0


class TestNHF:
    def test_two_point_five_percent_of_basic(self):
        """NHF = 2.5% of annual basic salary only."""
        result = calculate_nhf(600_000.0)
        assert result == pytest.approx(0.025 * 600_000.0)

    def test_zero_basic(self):
        """Zero basic → zero NHF."""
        assert calculate_nhf(0.0) == 0.0

    def test_negative_basic(self):
        """Negative basic → zero NHF."""
        assert calculate_nhf(-100_000.0) == 0.0

    def test_exact_rate(self):
        """Confirm exact 2.5% rate on ₦1,200,000."""
        assert calculate_nhf(1_200_000.0) == pytest.approx(30_000.0)


class TestLifeAssurance:
    def test_under_cap(self):
        """Premium ₦50,000 → deduction ₦50,000 (below ₦100k cap)."""
        assert calculate_life_assurance_deduction(50_000.0) == 50_000.0

    def test_exactly_at_cap(self):
        """Premium ₦100,000 → deduction ₦100,000 (at cap)."""
        assert calculate_life_assurance_deduction(100_000.0) == 100_000.0

    def test_above_cap_clamped(self):
        """Premium ₦200,000 → capped at ₦100,000 under NTA 2025."""
        assert calculate_life_assurance_deduction(200_000.0) == 100_000.0

    def test_high_premium_always_capped(self):
        """Very high premium → always ₦100,000."""
        assert calculate_life_assurance_deduction(5_000_000.0) == 100_000.0

    def test_zero_premium(self):
        """No life assurance → zero deduction."""
        assert calculate_life_assurance_deduction(0.0) == 0.0

    def test_negative_premium(self):
        """Negative premium → zero deduction."""
        assert calculate_life_assurance_deduction(-50_000.0) == 0.0

    def test_small_premium(self):
        """Small premium ₦10,000 → deduction ₦10,000."""
        assert calculate_life_assurance_deduction(10_000.0) == 10_000.0


class TestChargeableIncome:
    def test_normal_case(self):
        """
        Gross ₦3,600,000 - rent ₦240,000 - pension ₦76,800 - NHF ₦15,000
        = ₦3,268,200
        """
        gross = 3_600_000.0
        rent_relief = 240_000.0
        pension = 76_800.0
        nhf = 15_000.0
        result = calculate_chargeable_income(gross, rent_relief, pension, nhf)
        assert result == pytest.approx(gross - rent_relief - pension - nhf)

    def test_floors_at_zero(self):
        """If deductions exceed gross, chargeable income = ₦0 (not negative)."""
        result = calculate_chargeable_income(100_000.0, rent_relief=500_000.0, pension=100_000.0)
        assert result == 0.0

    def test_combined_reliefs_never_negative(self):
        """Even with all reliefs maxed out, result is always >= 0."""
        result = calculate_chargeable_income(
            1_000_000.0,
            rent_relief=500_000.0,
            pension=200_000.0,
            nhf=50_000.0,
            nhis_annual=120_000.0,
            life_assurance=100_000.0,
        )
        assert result >= 0.0

    def test_no_deductions(self):
        """No reliefs → chargeable = gross."""
        gross = 5_000_000.0
        assert calculate_chargeable_income(gross) == pytest.approx(gross)

    def test_nhis_deduction(self):
        """NHIS monthly ₦5,000 × 12 = ₦60,000 annual reduces chargeable income."""
        gross = 2_400_000.0
        nhis_annual = 60_000.0
        result = calculate_chargeable_income(gross, nhis_annual=nhis_annual)
        assert result == pytest.approx(gross - nhis_annual)

    def test_all_reliefs_combined(self):
        """All five relief types reduce chargeable income correctly."""
        gross = 10_000_000.0
        rent_relief = 500_000.0
        pension = 384_000.0
        nhf = 30_000.0
        nhis_annual = 72_000.0
        life_assurance = 100_000.0
        expected = gross - rent_relief - pension - nhf - nhis_annual - life_assurance
        result = calculate_chargeable_income(
            gross, rent_relief, pension, nhf, nhis_annual, life_assurance
        )
        assert result == pytest.approx(expected)

    def test_zero_gross(self):
        """Zero gross → zero chargeable regardless of deductions passed."""
        result = calculate_chargeable_income(0.0, rent_relief=100_000.0, pension=50_000.0)
        assert result == 0.0
