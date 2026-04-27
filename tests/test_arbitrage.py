from arbitrage import (
    american_to_decimal,
    calculate_stake_split,
    detect_arbitrage,
    implied_probability,
)


def test_american_to_decimal_positive_odds() -> None:
    assert american_to_decimal(150) == 2.5


def test_american_to_decimal_negative_odds() -> None:
    assert american_to_decimal(-200) == 1.5


def test_implied_probability() -> None:
    assert implied_probability(2.5) == 0.4


def test_detect_arbitrage_true() -> None:
    best_prices = {
        "Team A": {"decimal_odds": 2.2},
        "Team B": {"decimal_odds": 2.2},
    }
    is_arb, implied_total, edge_percent = detect_arbitrage(best_prices)

    assert is_arb is True
    assert round(implied_total, 4) == 0.9091
    assert round(edge_percent, 2) == 9.09


def test_detect_arbitrage_false() -> None:
    best_prices = {
        "Team A": {"decimal_odds": 1.8},
        "Team B": {"decimal_odds": 2.0},
    }
    is_arb, _, _ = detect_arbitrage(best_prices)
    assert is_arb is False


def test_calculate_stake_split() -> None:
    best_prices = {
        "Team A": {"decimal_odds": 2.2},
        "Team B": {"decimal_odds": 2.2},
    }
    stakes, payout, profit = calculate_stake_split(100, best_prices)

    assert stakes["Team A"] == 50.0
    assert stakes["Team B"] == 50.0
    assert payout == 110.0
    assert profit == 10.0
