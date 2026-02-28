"""
Tests for bot/utils/validators.py — parse_amount() input parsing.

All tests are pure unit tests requiring no database or network access.
"""

import pytest
from bot.utils.validators import parse_amount


class TestValidAmounts:
    @pytest.mark.parametrize("text,expected", [
        ("150000", 150_000),
        ("150,000", 150_000),
        ("150k", 150_000),
        ("150K", 150_000),
        ("1.5m", 1_500_000),
        ("1.5M", 1_500_000),
        ("₦150,000", 150_000),
        ("₦1.5m", 1_500_000),
        ("0", 0),
        ("150000.99", 150_000),      # floor to int
        ("1000000000", 1_000_000_000),  # exactly at limit
        ("1m", 1_000_000),
        ("0.5m", 500_000),
        ("500k", 500_000),
        ("₦500k", 500_000),
        ("₦0", 0),
        ("1,200,000", 1_200_000),
        ("2500", 2_500),
        ("100", 100),
        ("999k", 999_000),
        ("1.25m", 1_250_000),
    ])
    def test_valid_formats(self, text, expected):
        assert parse_amount(text) == expected


class TestInvalidAmounts:
    @pytest.mark.parametrize("text", [
        "-150000",
        "abc",
        "",
        "  ",
        "2000000000",       # over ₦1 billion
        "1001m",            # > 1 billion (1,001,000,000)
        "hello",
        "150,000abc",
        "1.5.5m",
        "k150",
        "m",
        "k",
        "1e6",              # scientific notation not supported
        "--100",
        "one million",
    ])
    def test_invalid_formats(self, text):
        assert parse_amount(text) is None

    def test_none_input(self):
        assert parse_amount(None) is None


class TestEdgeCases:
    def test_whitespace_around_valid(self):
        """Leading/trailing whitespace is stripped."""
        assert parse_amount("  150000  ") == 150_000

    def test_floor_behavior(self):
        """Decimal part is floored, not rounded."""
        assert parse_amount("1000.9") == 1_000
        assert parse_amount("999.1") == 999

    def test_naira_symbol_prefix(self):
        """₦ symbol is stripped before parsing."""
        assert parse_amount("₦300,000") == 300_000
        assert parse_amount("₦2.5m") == 2_500_000

    def test_exactly_one_billion(self):
        """₦1,000,000,000 is the maximum allowed value."""
        assert parse_amount("1000000000") == 1_000_000_000
        assert parse_amount("1000m") == 1_000_000_000

    def test_one_above_limit(self):
        """₦1,000,000,001 exceeds limit → None."""
        assert parse_amount("1000000001") is None

    def test_k_suffix_case_insensitive(self):
        assert parse_amount("100k") == parse_amount("100K") == 100_000

    def test_m_suffix_case_insensitive(self):
        assert parse_amount("2m") == parse_amount("2M") == 2_000_000

    def test_zero_is_valid(self):
        """Zero is a valid amount (user may enter ₦0 for optional fields)."""
        assert parse_amount("0") == 0
        assert parse_amount("0.0") == 0
        assert parse_amount("0k") == 0
