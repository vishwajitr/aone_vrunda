"""
Core backtesting engine for intraday options strategies.

Iterates through index candles, calls user strategy, manages positions
and tracks P&L using synthetic Black-76 option premiums.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Callable, Protocol

from utils.logging import get_logger

from backtest.option_pricer import (
    PricerConfig,
    minutes_of_trading_day,
    quote_option,
)
from backtest.costs import FnOCosts, INDIA_FNO_DEFAULT

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Signal and position types
# ---------------------------------------------------------------------------

class Signal(Enum):
    HOLD = "hold"
    BUY_CE = "buy_ce"
    BUY_PE = "buy_pe"
    EXIT = "exit"


@dataclass
class Candle:
    """One OHLCV bar with metadata."""

    datetime: object  # pandas Timestamp or datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    date: object
    time: object
    hour: int
    minute: int
    #: Minutes elapsed since market open (for pricing)
    minutes_elapsed: float = 0.0


@dataclass
class Position:
    """An open options position."""

    side: str  # 'ce' or 'pe'
    strike: int
    entry_premium: float
    entry_spot: float
    entry_time: object
    entry_datetime: object
    quantity: int
    stop_loss: float
    target: float | None = None
    trailing_stop: float | None = None
    trailing_activated: bool = False
    best_premium: float = 0.0
    best_spot: float = 0.0
    pnl: float = 0.0
    exit_premium: float = 0.0
    exit_reason: str = ""


@dataclass
class Trade:
    """A completed trade."""

    entry_date: object
    entry_time: object
    exit_date: object
    exit_time: object
    side: str
    strike: int
    entry_spot: float
    exit_spot: float
    entry_premium: float
    exit_premium: float
    quantity: int
    gross_pnl: float
    costs: dict
    net_pnl: float
    exit_reason: str
    holding_minutes: float


@dataclass
class BacktestConfig:
    """Full backtest configuration."""

    #: Starting capital
    initial_capital: float = 100_000.0
    #: Number of lots to buy
    lots: int = 1
    #: Lot size (50 for NIFTY, 15 for BANKNIFTY)
    lot_size: int = 50
    #: Stop loss in points from entry premium
    stop_loss_points: float = 50.0
    #: Take profit in points from entry premium (0 = disabled)
    target_points: float = 0.0
    #: Trailing stop activation premium level (0 = disabled)
    trailing_activate_at: float = 0.0
    #: Trailing stop distance in points
    trailing_stop_points: float = 20.0
    #: Maximum trades per day
    max_trades_per_day: int = 2
    #: Maximum daily loss as fraction of capital (e.g. 0.10 = 10%)
    max_daily_loss_pct: float = 0.10
    #: Only trade until this time (HH:MM)
    last_entry_time: str = "15:00"
    #: Force exit all positions at this time (HH:MM)
    eod_exit_time: str = "15:25"
    #: Option pricing configuration
    pricer: PricerConfig = field(default_factory=PricerConfig)
    #: Transaction cost model
    costs: FnOCosts = field(default_factory=lambda: INDIA_FNO_DEFAULT)


class Strategy(Protocol):
    """Strategy interface. Implement on_candle()."""

    def on_candle(self, candle: Candle, position: Position | None, capital: float) -> Signal:
        ...


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class BacktestEngine:
    """
    Core backtesting loop.

    Usage:
        engine = BacktestEngine(config)
        result = engine.run(dataframe, my_strategy)
    """

    def __init__(self, config: BacktestConfig | None = None):
        self.config = config or BacktestConfig()
        self.trades: list[Trade] = []
        self.equity_curve: list[dict] = []
        self.position: Position | None = None
        self.capital = self.config.initial_capital
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.current_date = None

    def run(self, df, strategy) -> dict:
        """
        Run backtest on OHLCV DataFrame.

        Args:
            df: DataFrame with columns: open, high, low, close, volume, date, time, hour, minute
                Must have a datetime index.
            strategy: Object with on_candle(candle, position, capital) -> Signal

        Returns:
            Dictionary with trades, equity_curve, and summary metrics
        """
        from backtest.analytics import compute_metrics

        self.trades = []
        self.equity_curve = []
        self.position = None
        self.capital = self.config.initial_capital
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.current_date = None

        last_entry = self._parse_time(self.config.last_entry_time)
        eod_exit = self._parse_time(self.config.eod_exit_time)

        for idx, row in df.iterrows():
            # Build candle
            candle = self._row_to_candle(row, idx)

            # Reset daily state on new day
            if candle.date != self.current_date:
                self.current_date = candle.date
                self.trades_today = 0
                self.daily_pnl = 0.0

            # Force exit at EOD
            if self.position and candle.time >= eod_exit:
                self._close_position(candle, "EOD")
                self._record_equity(candle)

            # Skip candles outside trading hours
            if candle.minutes_elapsed < 0:
                continue

            # Check if we have a position
            if self.position:
                self._manage_position(candle)
                self._record_equity(candle)
                continue

            # Check daily limits
            if self.trades_today >= self.config.max_trades_per_day:
                self._record_equity(candle)
                continue

            capital_pct = self.daily_pnl / self.config.initial_capital if self.config.initial_capital > 0 else 0
            if capital_pct <= -self.config.max_daily_loss_pct:
                self._record_equity(candle)
                continue

            # Only allow entry until last_entry_time
            if candle.time > last_entry:
                self._record_equity(candle)
                continue

            # Call strategy
            signal = strategy.on_candle(candle, None, self.capital)

            if signal in (Signal.BUY_CE, Signal.BUY_PE):
                self._open_position(candle, signal)
                self.trades_today += 1

            self._record_equity(candle)

        # Close any remaining position
        if self.position and not df.empty:
            last_row = df.iloc[-1]
            last_candle = self._row_to_candle(last_row, df.index[-1])
            self._close_position(last_candle, "BACKTEST_END")

        metrics = compute_metrics(self.trades, self.equity_curve, self.config.initial_capital)

        return {
            "trades": [self._trade_to_dict(t) for t in self.trades],
            "equity_curve": self.equity_curve,
            "metrics": metrics,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse_time(self, time_str: str) -> time:
        h, m = map(int, time_str.split(":"))
        return time(h, m)

    def _row_to_candle(self, row, idx) -> Candle:
        dt = idx if hasattr(idx, "hour") else None
        if dt is None:
            import pandas as pd
            dt = pd.Timestamp(row.get("datetime", idx))

        # Calculate minutes elapsed from market open
        open_h = self.config.pricer.market_open_hour
        open_m = self.config.pricer.market_open_minute
        market_open_min = open_h * 60 + open_m
        candle_min = dt.hour * 60 + dt.minute
        elapsed = candle_min - market_open_min

        return Candle(
            datetime=dt,
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row.get("volume", 0)),
            date=dt.date() if hasattr(dt, "date") else dt,
            time=dt.time() if hasattr(dt, "time") else dt,
            hour=dt.hour,
            minute=dt.minute,
            minutes_elapsed=float(elapsed),
        )

    def _open_position(self, candle: Candle, signal: Signal):
        side = "ce" if signal == Signal.BUY_CE else "pe"
        flag = "c" if side == "ce" else "p"

        quote = quote_option(
            spot=candle.close,
            config=self.config.pricer,
            flag=flag,
            candle_minutes_elapsed=candle.minutes_elapsed,
        )

        quantity = self.config.lots * self.config.lot_size
        entry_premium = quote.premium
        cost = self.config.costs.calculate(entry_premium, entry_premium, quantity)

        # Stop loss: entry premium minus stop_loss_points
        sl = max(1.0, entry_premium - self.config.stop_loss_points)
        target = None
        if self.config.target_points > 0:
            target = entry_premium + self.config.target_points

        self.position = Position(
            side=side,
            strike=quote.strike,
            entry_premium=entry_premium,
            entry_spot=candle.close,
            entry_time=candle.time,
            entry_datetime=candle.datetime,
            quantity=quantity,
            stop_loss=sl,
            target=target,
            trailing_stop=None,
            trailing_activated=False,
            best_premium=entry_premium,
            best_spot=candle.close,
        )

        logger.debug(
            "OPEN %s @ %.2f, spot=%.2f, strike=%d, qty=%d, SL=%.2f",
            side.upper(), entry_premium, candle.close, quote.strike, quantity, sl,
        )

    def _manage_position(self, candle: Candle):
        if not self.position:
            return

        pos = self.position
        flag = "c" if pos.side == "ce" else "p"

        # Re-price option at current candle
        current_quote = quote_option(
            spot=candle.close,
            config=self.config.pricer,
            flag=flag,
            candle_minutes_elapsed=candle.minutes_elapsed,
        )
        current_premium = current_quote.premium

        # Update best tracking
        if current_premium > pos.best_premium:
            pos.best_premium = current_premium
            pos.best_spot = candle.close

        # Check stop loss (intraday low)
        if candle.low <= pos.stop_loss:
            self._close_position(candle, "STOP_LOSS", override_premium=pos.stop_loss)
            return

        # Check trailing stop
        if pos.trailing_activated and pos.trailing_stop is not None:
            if candle.low <= pos.trailing_stop:
                self._close_position(candle, "TRAILING_STOP", override_premium=pos.trailing_stop)
                return

        # Check target
        if pos.target and candle.high >= pos.target and not pos.trailing_activated:
            # Activate trailing stop
            pos.trailing_activated = True
            pos.trailing_stop = pos.target - self.config.trailing_stop_points
            pos.best_premium = pos.target
            pos.best_spot = candle.close
            logger.debug("TRAILING ACTIVATED at %.2f, SL=%.2f", pos.target, pos.trailing_stop)

        # Update trailing stop
        if pos.trailing_activated and pos.trailing_stop is not None:
            new_trail = pos.best_premium - self.config.trailing_stop_points
            if new_trail > pos.trailing_stop:
                pos.trailing_stop = new_trail

    def _close_position(self, candle: Candle, reason: str, override_premium: float | None = None):
        if not self.position:
            return

        pos = self.position

        if override_premium is not None:
            exit_premium = override_premium
        else:
            flag = "c" if pos.side == "ce" else "p"
            quote = quote_option(
                spot=candle.close,
                config=self.config.pricer,
                flag=flag,
                candle_minutes_elapsed=candle.minutes_elapsed,
            )
            exit_premium = quote.premium

        gross_pnl = (exit_premium - pos.entry_premium) * pos.quantity
        cost_detail = self.config.costs.calculate(pos.entry_premium, exit_premium, pos.quantity)
        net_pnl = gross_pnl - cost_detail["total"]

        # Calculate holding minutes
        entry_dt = pos.entry_datetime
        exit_dt = candle.datetime
        holding = 0.0
        if hasattr(entry_dt, "timestamp") and hasattr(exit_dt, "timestamp"):
            holding = (exit_dt.timestamp() - entry_dt.timestamp()) / 60.0

        trade = Trade(
            entry_date=pos.entry_datetime.date() if hasattr(pos.entry_datetime, "date") else pos.entry_datetime,
            entry_time=pos.entry_time,
            exit_date=candle.date,
            exit_time=candle.time,
            side=pos.side,
            strike=pos.strike,
            entry_spot=pos.entry_spot,
            exit_spot=candle.close,
            entry_premium=pos.entry_premium,
            exit_premium=exit_premium,
            quantity=pos.quantity,
            gross_pnl=round(gross_pnl, 2),
            costs=cost_detail,
            net_pnl=round(net_pnl, 2),
            exit_reason=reason,
            holding_minutes=round(holding, 1),
        )

        self.trades.append(trade)
        self.capital += net_pnl
        self.daily_pnl += net_pnl
        self.position = None

        logger.debug(
            "CLOSE %s @ %.2f, reason=%s, net_pnl=%.2f, capital=%.2f",
            pos.side.upper(), exit_premium, reason, net_pnl, self.capital,
        )

    def _record_equity(self, candle: Candle):
        # Mark-to-market if position is open
        mtm = 0.0
        if self.position:
            flag = "c" if self.position.side == "ce" else "p"
            q = quote_option(
                spot=candle.close,
                config=self.config.pricer,
                flag=flag,
                candle_minutes_elapsed=candle.minutes_elapsed,
            )
            mtm = (q.premium - self.position.entry_premium) * self.position.quantity

        self.equity_curve.append({
            "datetime": str(candle.datetime),
            "equity": round(self.capital + mtm, 2),
            "capital": round(self.capital, 2),
            "mtm": round(mtm, 2),
            "spot": candle.close,
            "date": str(candle.date),
        })

    def _trade_to_dict(self, t: Trade) -> dict:
        return {
            "entry_date": str(t.entry_date),
            "entry_time": str(t.entry_time),
            "exit_date": str(t.exit_date),
            "exit_time": str(t.exit_time),
            "side": t.side.upper(),
            "strike": t.strike,
            "entry_spot": t.entry_spot,
            "exit_spot": t.exit_spot,
            "entry_premium": t.entry_premium,
            "exit_premium": t.exit_premium,
            "quantity": t.quantity,
            "gross_pnl": t.gross_pnl,
            "costs": t.costs,
            "net_pnl": t.net_pnl,
            "exit_reason": t.exit_reason,
            "holding_minutes": t.holding_minutes,
        }
