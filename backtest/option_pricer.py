"""
Black-76 option pricing for synthesizing historical option premiums.

Black-76 is the standard model for European options on futures/forwards,
which is the correct model for Indian F&O markets (NFO, BFO, MCX, CDS).
"""

import math
from dataclasses import dataclass

from utils.logging import get_logger

logger = get_logger(__name__)


# Standard normal CDF approximation (Abramowitz & Stegun)
def _norm_cdf(x: float) -> float:
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1.0 if x >= 0 else -1.0
    x = abs(x) / math.sqrt(2.0)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return 0.5 * (1.0 + sign * y)


def black76_price(
    F: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    flag: str,
) -> float:
    """
    Black-76 European option price.

    Args:
        F: Forward/futures price (index level)
        K: Strike price
        T: Time to expiry in years (e.g. 1/365 for 1 day)
        r: Risk-free interest rate (annualized, decimal, e.g. 0.065)
        sigma: Implied volatility (annualized, decimal, e.g. 0.18)
        flag: 'c' for call, 'p' for put

    Returns:
        Option premium (per unit)
    """
    if T <= 0 or sigma <= 0:
        if flag == "c":
            return max(0.0, F - K)
        return max(0.0, K - F)

    df = math.exp(-r * T)
    sqrt_T = math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * sigma * sigma * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    Nd1 = _norm_cdf(d1)
    Nd2 = _norm_cdf(d2)

    if flag == "c":
        return df * (F * Nd1 - K * Nd2)
    return df * (K * _norm_cdf(-d2) - F * _norm_cdf(-d1))


@dataclass(frozen=True)
class OptionQuote:
    """Synthetic option quote for a given moment."""

    strike: int
    flag: str  # 'c' or 'p'
    spot: float
    premium: float
    delta: float
    iv: float
    time_to_expiry_days: float


@dataclass(frozen=True)
class PricerConfig:
    """Configuration for the option pricer."""

    #: Annualized implied volatility (decimal, e.g. 0.18 for 18%)
    iv: float = 0.18
    #: Risk-free rate (annualized decimal, e.g. 0.065 for 6.5%)
    risk_free_rate: float = 0.065
    #: Strike distance from ATM (in points). 0 = exact ATM.
    strike_offset: int = 0
    #: Strike rounding. 50 for NIFTY, 100 for BANKNIFTY.
    strike_rounding: int = 50
    #: Trading days per year (for time calculations)
    trading_days_per_year: int = 252
    #: Market open time (hour, minute) in IST
    market_open_hour: int = 9
    market_open_minute: int = 15
    #: Market close time (hour, minute) in IST
    market_close_hour: int = 15
    market_close_minute: int = 30
    #: Minutes remaining at market close (for EOD premium)
    eod_minutes: int = 0
    #: Expiry days to use (for weekly options, typically 0-7 days)
    expiry_days: int = 1


def get_atm_strike(spot: float, rounding: int = 50, offset: int = 0) -> int:
    """Round spot to nearest ATM strike."""
    return round(spot / rounding) * rounding + offset


def minutes_of_trading_day(
    ts_hour: int,
    ts_minute: int,
    config: PricerConfig,
) -> float:
    """
    Minutes elapsed since market open for a given IST time.
    Returns negative if before market open.
    """
    market_open = config.market_open_hour * 60 + config.market_open_minute
    current = ts_hour * 60 + ts_minute
    return current - market_open


def total_trading_minutes(config: PricerConfig) -> float:
    """Total minutes in a trading day."""
    open_min = config.market_open_hour * 60 + config.market_open_minute
    close_min = config.market_close_hour * 60 + config.market_close_minute
    return close_min - open_min


def time_to_expiry_years(
    candle_minutes_elapsed: float,
    config: PricerConfig,
) -> float:
    """
    Calculate time to expiry in years for an intraday option.

    At market open: T = 1 trading day
    At market close: T = 0
    Linear interpolation through the day.
    """
    total = total_trading_minutes(config)
    remaining_minutes = max(0.0, total - candle_minutes_elapsed)
    trading_days_left = remaining_minutes / total if total > 0 else 0
    # Add expiry_days for the expiry day itself
    days = config.expiry_days + trading_days_left
    return days / config.trading_days_per_year


def quote_option(
    spot: float,
    config: PricerConfig,
    flag: str = "c",
    candle_minutes_elapsed: float = 0.0,
) -> OptionQuote:
    """
    Generate a synthetic option quote for a given spot price and time.

    Args:
        spot: Current index/futures level
        config: Pricer configuration
        flag: 'c' for call, 'p' for put
        candle_minutes_elapsed: Minutes elapsed since market open

    Returns:
        OptionQuote with premium, delta, etc.
    """
    strike = get_atm_strike(spot, config.strike_rounding, config.strike_offset)
    T = time_to_expiry_years(candle_minutes_elapsed, config)
    premium = black76_price(spot, strike, T, config.risk_free_rate, config.iv, flag)

    # Delta approximation (Black-76 delta)
    sqrt_T = math.sqrt(T) if T > 0 else 1e-10
    d1 = (
        math.log(spot / strike) + 0.5 * config.iv * config.iv * T
    ) / (config.iv * sqrt_T)

    if flag == "c":
        delta = _norm_cdf(d1)
    else:
        delta = _norm_cdf(d1) - 1.0

    time_to_expiry_days = T * config.trading_days_per_year

    return OptionQuote(
        strike=strike,
        flag=flag,
        spot=spot,
        premium=max(0.01, premium),
        delta=delta,
        iv=config.iv,
        time_to_expiry_days=time_to_expiry_days,
    )


def estimate_premium_at_exit(
    entry_premium: float,
    entry_spot: float,
    exit_spot: float,
    strike: int,
    flag: str,
    entry_minutes_elapsed: float,
    exit_minutes_elapsed: float,
    config: PricerConfig,
) -> float:
    """
    Estimate option premium at exit based on spot change and time decay.

    Uses Black-76 with the same IV, recalculating time to expiry.
    This gives a realistic premium change from both delta and theta.
    """
    entry_T = time_to_expiry_years(entry_minutes_elapsed, config)
    exit_T = time_to_expiry_years(exit_minutes_elapsed, config)

    # Use Black-76 for both entry and exit
    entry_calc = black76_price(entry_spot, strike, entry_T, config.risk_free_rate, config.iv, flag)
    exit_calc = black76_price(exit_spot, strike, exit_T, config.risk_free_rate, config.iv, flag)

    # If entry premium was from a quote (might have rounding), scale proportionally
    if entry_calc > 0:
        ratio = exit_calc / entry_calc
        return max(0.01, entry_premium * ratio)

    return max(0.01, exit_calc)
