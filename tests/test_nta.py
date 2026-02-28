"""
Tests for bot/calculators/nta.py — NTA 2025 tax calculation logic.

All tests use pure functions and require no database or network access.
"""

import pytest
from bot.calculators.nta import calculate_tax


class TestZeroIncome:
    def test_zero_gross_zero_chargeable(self):
        """Both inputs zero → zero tax."""
        r = calculate_tax(0.0, 0.0)
        assert r["annual_tax"] == 0.0
        assert r["monthly_paye"] == 0.0
        assert r["effective_rate"] == 0.0
        assert r["bands"] == []

    def test_zero_chargeable_nonzero_gross(self):
        """Chargeable = 0 with nonzero gross → zero tax, no minimum tax."""
        r = calculate_tax(0.0, 2_000_000.0)
        assert r["annual_tax"] == 0.0
        assert r["is_exempt"] is True


class TestExemptionThreshold:
    def test_below_threshold_small(self):
        """₦500,000 chargeable → zero tax (below ₦800k threshold)."""
        r = calculate_tax(500_000.0, 1_000_000.0)
        assert r["annual_tax"] == 0.0
        assert r["is_exempt"] is True

    def test_exactly_at_threshold(self):
        """₦800,000 chargeable → zero tax (at threshold, 0% band)."""
        r = calculate_tax(800_000.0, 1_500_000.0)
        assert r["annual_tax"] == 0.0
        assert r["is_exempt"] is True

    def test_one_naira_above_threshold(self):
        """₦800,001 chargeable → 1 Naira taxed at 15% = ₦0.15 (≈0)."""
        r = calculate_tax(800_001.0, 1_500_000.0)
        # ₦1 above threshold × 15% = ₦0.15
        assert abs(r["annual_tax"] - 0.15) < 0.01
        assert r["is_exempt"] is False


class TestTaxBands:
    def test_first_two_bands(self):
        """
        ₦3,000,000 chargeable:
        - ₦800,000 @ 0%   = ₦0
        - ₦2,200,000 @ 15% = ₦330,000
        Total = ₦330,000
        """
        r = calculate_tax(3_000_000.0, 4_000_000.0)
        assert r["annual_tax"] == pytest.approx(330_000.0)
        assert len(r["bands"]) == 2

    def test_just_above_threshold(self):
        """
        ₦1,000,000 chargeable:
        - ₦800,000 @ 0%  = ₦0
        - ₦200,000 @ 15% = ₦30,000
        Total = ₦30,000
        """
        r = calculate_tax(1_000_000.0, 2_000_000.0)
        assert r["annual_tax"] == pytest.approx(30_000.0)

    def test_three_bands(self):
        """
        ₦5,000,000 chargeable:
        - ₦800,000   @ 0%  = ₦0
        - ₦2,200,000 @ 15% = ₦330,000
        - ₦2,000,000 @ 18% = ₦360,000
        Total = ₦690,000
        """
        r = calculate_tax(5_000_000.0, 6_000_000.0)
        expected = 2_200_000 * 0.15 + 2_000_000 * 0.18
        assert r["annual_tax"] == pytest.approx(expected)
        assert len(r["bands"]) == 3

    def test_four_bands(self):
        """
        ₦10,000,000 chargeable:
        - ₦800,000   @ 0%  = ₦0
        - ₦2,200,000 @ 15% = ₦330,000
        - ₦6,000,000 @ 18% = ₦1,080,000
        - ₦1,000,000 @ 21% = ₦210,000
        Total = ₦1,620,000
        """
        r = calculate_tax(10_000_000.0, 12_000_000.0)
        expected = 2_200_000 * 0.15 + 6_000_000 * 0.18 + 1_000_000 * 0.21
        assert r["annual_tax"] == pytest.approx(expected)
        assert len(r["bands"]) == 4

    def test_five_bands(self):
        """
        ₦14,000,000 chargeable:
        - ₦800,000   @ 0%  = ₦0
        - ₦2,200,000 @ 15% = ₦330,000
        - ₦6,000,000 @ 18% = ₦1,080,000
        - ₦4,000,000 @ 21% = ₦840,000
        - ₦1,000,000 @ 23% = ₦230,000
        Total = ₦2,480,000
        """
        r = calculate_tax(14_000_000.0, 18_000_000.0)
        expected = (
            2_200_000 * 0.15
            + 6_000_000 * 0.18
            + 4_000_000 * 0.21
            + 1_000_000 * 0.23
        )
        assert r["annual_tax"] == pytest.approx(expected)
        assert len(r["bands"]) == 5

    def test_six_bands(self):
        """
        ₦30,000,000 chargeable:
        - ₦800,000    @ 0%  = ₦0
        - ₦2,200,000  @ 15% = ₦330,000
        - ₦6,000,000  @ 18% = ₦1,080,000
        - ₦4,000,000  @ 21% = ₦840,000
        - ₦12,000,000 @ 23% = ₦2,760,000
        - ₦5,000,000  @ 23% = ₦1,150,000
        Total = ₦6,160,000
        """
        r = calculate_tax(30_000_000.0, 35_000_000.0)
        expected = (
            2_200_000 * 0.15
            + 6_000_000 * 0.18
            + 4_000_000 * 0.21
            + 12_000_000 * 0.23
            + 5_000_000 * 0.23
        )
        assert r["annual_tax"] == pytest.approx(expected)
        assert len(r["bands"]) == 6

    def test_all_seven_bands(self):
        """
        ₦60,000,000 chargeable — all 7 bands including 25%:
        - ₦800,000    @ 0%  = ₦0
        - ₦2,200,000  @ 15% = ₦330,000
        - ₦6,000,000  @ 18% = ₦1,080,000
        - ₦4,000,000  @ 21% = ₦840,000
        - ₦12,000,000 @ 23% = ₦2,760,000
        - ₦25,000,000 @ 23% = ₦5,750,000
        - ₦10,000,000 @ 25% = ₦2,500,000
        Total = ₦13,260,000
        """
        r = calculate_tax(60_000_000.0, 65_000_000.0)
        expected = (
            2_200_000 * 0.15
            + 6_000_000 * 0.18
            + 4_000_000 * 0.21
            + 12_000_000 * 0.23
            + 25_000_000 * 0.23
            + 10_000_000 * 0.25
        )
        assert r["annual_tax"] == pytest.approx(expected)
        assert len(r["bands"]) == 7


class TestNoMinimumTax:
    def test_no_minimum_tax_applies(self):
        """
        Under NTA 2025, there is no minimum tax.
        A tiny chargeable income below threshold → tax is simply 0.
        """
        r = calculate_tax(100_000.0, 5_000_000.0)
        # Old PITA: min tax = 1% of 5M = 50,000
        # NTA 2025: no minimum tax, chargeable < 800k → 0
        assert r["annual_tax"] == 0.0

    def test_no_minimum_tax_above_threshold(self):
        """
        Even above the threshold, no minimum tax is applied.
        Tax is purely from the progressive bands.
        """
        r = calculate_tax(900_000.0, 100_000_000.0)
        # 100k above threshold × 15% = ₦15,000
        # Old PITA would apply min tax = 1% of 100M = ₦1,000,000
        # NTA 2025: no minimum tax, result is ₦15,000
        assert r["annual_tax"] == pytest.approx(15_000.0)


class TestEffectiveRate:
    def test_effective_rate_calculation(self):
        """Effective rate = (annual_tax / gross_annual) × 100, rounded to 2dp."""
        gross = 4_000_000.0
        r = calculate_tax(3_000_000.0, gross)
        expected_rate = round((r["annual_tax"] / gross) * 100, 2)
        assert r["effective_rate"] == expected_rate

    def test_effective_rate_zero_when_exempt(self):
        """Effective rate is 0 when tax is 0."""
        r = calculate_tax(500_000.0, 1_000_000.0)
        assert r["effective_rate"] == 0.0

    def test_zero_gross_no_division(self):
        """Does not divide by zero when gross_annual = 0."""
        r = calculate_tax(0.0, 0.0)
        assert r["effective_rate"] == 0.0


class TestMonthlyPAYE:
    def test_monthly_paye_is_annual_divided_by_12(self):
        """Monthly PAYE = annual tax ÷ 12."""
        r = calculate_tax(3_000_000.0, 4_000_000.0)
        assert r["monthly_paye"] == pytest.approx(r["annual_tax"] / 12)

    def test_monthly_paye_zero_when_exempt(self):
        r = calculate_tax(800_000.0, 1_500_000.0)
        assert r["monthly_paye"] == 0.0


class TestBandDetails:
    def test_band_detail_structure(self):
        """Each band dict has required keys: label, amount, rate, tax."""
        r = calculate_tax(3_000_000.0, 4_000_000.0)
        for band in r["bands"]:
            assert "label" in band
            assert "amount" in band
            assert "rate" in band
            assert "tax" in band

    def test_band_amounts_sum_to_chargeable(self):
        """Band amounts should sum to the full chargeable income."""
        chargeable = 5_000_000.0
        r = calculate_tax(chargeable, 6_000_000.0)
        total = sum(b["amount"] for b in r["bands"])
        assert total == pytest.approx(chargeable)

    def test_band_taxes_sum_to_annual_tax(self):
        """Band tax amounts should sum to annual_tax."""
        r = calculate_tax(10_000_000.0, 12_000_000.0)
        total = sum(b["tax"] for b in r["bands"])
        assert total == pytest.approx(r["annual_tax"])
