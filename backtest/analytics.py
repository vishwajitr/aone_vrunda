"""
Trade-level analytics for backtesting results.

Computes metrics from completed trades and equity curves.
"""

from __future__ import annotations

import math
from utils.logging import get_logger

logger = get_logger(__name__)


def compute_metrics(
    trades: list,
    equity_curve: list[dict],
    initial_capital: float,
) -> dict:
    """
    Compute comprehensive backtest metrics from trades and equity curve.

    Args:
        trades: List of Trade objects
        equity_curve: List of dicts with 'equity', 'datetime', 'spot'
        initial_capital: Starting capital

    Returns:
        Dictionary of metrics
    """
    if not trades:
        return _empty_metrics(initial_capital)

    # Basic trade stats
    total_trades = len(trades)
    winners = [t for t in trades if t.net_pnl > 0]
    losers = [t for t in trades if t.net_pnl < 0]
    breakeven = [t for t in trades if t.net_pnl == 0]

    win_count = len(winners)
    loss_count = len(losers)
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0

    total_profit = sum(t.net_pnl for t in winners)
    total_loss = abs(sum(t.net_pnl for t in losers))
    net_pnl = sum(t.net_pnl for t in trades)
    gross_pnl = sum(t.gross_pnl for t in trades)
    total_costs = sum(t.costs.get("total", 0) for t in trades)

    avg_win = total_profit / win_count if win_count > 0 else 0
    avg_loss = -total_loss / loss_count if loss_count > 0 else 0
    avg_trade = net_pnl / total_trades if total_trades > 0 else 0

    profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")
    expectancy = avg_trade
    reward_risk = abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")

    # Per-side stats
    ce_trades = [t for t in trades if t.side == "ce"]
    pe_trades = [t for t in trades if t.side == "pe"]
    ce_wins = [t for t in ce_trades if t.net_pnl > 0]
    pe_wins = [t for t in pe_trades if t.net_pnl > 0]

    # Exit reason breakdown
    exit_reasons = {}
    for t in trades:
        reason = t.exit_reason
        if reason not in exit_reasons:
            exit_reasons[reason] = {"count": 0, "total_pnl": 0.0}
        exit_reasons[reason]["count"] += 1
        exit_reasons[reason]["total_pnl"] += t.net_pnl

    # Equity curve metrics
    final_capital = initial_capital + net_pnl
    total_return_pct = (net_pnl / initial_capital * 100) if initial_capital > 0 else 0

    # Drawdown from equity curve
    max_drawdown, max_drawdown_pct = _compute_drawdown(equity_curve, initial_capital)

    # Daily P&L series for Sharpe/Sortino
    daily_pnl = _daily_pnl_series(trades)
    sharpe = _sharpe_ratio(daily_pnl)
    sortino = _sortino_ratio(daily_pnl)

    # Consecutive wins/losses
    max_consec_wins, max_consec_losses = _consecutive_streaks(trades)

    # Holding time
    avg_holding = sum(t.holding_minutes for t in trades) / total_trades if total_trades > 0 else 0

    return {
        "summary": {
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "breakeven_trades": len(breakeven),
            "win_rate": round(win_rate, 2),
            "net_pnl": round(net_pnl, 2),
            "gross_pnl": round(gross_pnl, 2),
            "total_costs": round(total_costs, 2),
            "initial_capital": initial_capital,
            "final_capital": round(final_capital, 2),
            "total_return_pct": round(total_return_pct, 2),
        },
        "pnl": {
            "total_profit": round(total_profit, 2),
            "total_loss": round(-total_loss, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "avg_trade": round(avg_trade, 2),
            "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else "inf",
            "expectancy": round(expectancy, 2),
            "reward_risk": round(reward_risk, 4) if reward_risk != float("inf") else "inf",
        },
        "risk": {
            "max_drawdown": round(max_drawdown, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "max_consec_wins": max_consec_wins,
            "max_consec_losses": max_consec_losses,
        },
        "sides": {
            "ce_trades": len(ce_trades),
            "ce_wins": len(ce_wins),
            "ce_win_rate": round(len(ce_wins) / len(ce_trades) * 100, 2) if ce_trades else 0,
            "pe_trades": len(pe_trades),
            "pe_wins": len(pe_wins),
            "pe_win_rate": round(len(pe_wins) / len(pe_trades) * 100, 2) if pe_trades else 0,
        },
        "exit_reasons": {
            reason: {
                "count": data["count"],
                "total_pnl": round(data["total_pnl"], 2),
                "pct": round(data["count"] / total_trades * 100, 2),
            }
            for reason, data in sorted(exit_reasons.items(), key=lambda x: -x[1]["count"])
        },
        "timing": {
            "avg_holding_minutes": round(avg_holding, 1),
            "trading_days": len(set(t.entry_date for t in trades)),
            "trades_per_day": round(total_trades / max(1, len(set(t.entry_date for t in trades))), 2),
        },
    }


def _empty_metrics(initial_capital: float) -> dict:
    return {
        "summary": {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "breakeven_trades": 0,
            "win_rate": 0,
            "net_pnl": 0,
            "gross_pnl": 0,
            "total_costs": 0,
            "initial_capital": initial_capital,
            "final_capital": initial_capital,
            "total_return_pct": 0,
        },
        "pnl": {
            "total_profit": 0,
            "total_loss": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "avg_trade": 0,
            "profit_factor": 0,
            "expectancy": 0,
            "reward_risk": 0,
        },
        "risk": {
            "max_drawdown": 0,
            "max_drawdown_pct": 0,
            "sharpe_ratio": 0,
            "sortino_ratio": 0,
            "max_consec_wins": 0,
            "max_consec_losses": 0,
        },
        "sides": {
            "ce_trades": 0, "ce_wins": 0, "ce_win_rate": 0,
            "pe_trades": 0, "pe_wins": 0, "pe_win_rate": 0,
        },
        "exit_reasons": {},
        "timing": {
            "avg_holding_minutes": 0,
            "trading_days": 0,
            "trades_per_day": 0,
        },
    }


def _compute_drawdown(equity_curve: list[dict], initial_capital: float) -> tuple[float, float]:
    """Compute max drawdown from equity curve."""
    if not equity_curve:
        return 0.0, 0.0

    peak = initial_capital
    max_dd = 0.0
    max_dd_pct = 0.0

    for point in equity_curve:
        equity = point.get("equity", initial_capital)
        if equity > peak:
            peak = equity
        dd = peak - equity
        dd_pct = (dd / peak * 100) if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct

    return max_dd, max_dd_pct


def _daily_pnl_series(trades: list) -> list[float]:
    """Aggregate P&L by trading day."""
    daily = {}
    for t in trades:
        day = str(t.entry_date)
        daily[day] = daily.get(day, 0.0) + t.net_pnl
    return list(daily.values())


def _sharpe_ratio(daily_pnl: list[float], risk_free_daily: float = 0.0) -> float:
    """Annualized Sharpe ratio from daily P&L series."""
    if len(daily_pnl) < 2:
        return 0.0
    mean = sum(daily_pnl) / len(daily_pnl)
    var = sum((x - mean) ** 2 for x in daily_pnl) / (len(daily_pnl) - 1)
    std = math.sqrt(var) if var > 0 else 0
    if std == 0:
        return 0.0
    excess = mean - risk_free_daily
    return (excess / std) * math.sqrt(252)


def _sortino_ratio(daily_pnl: list[float], risk_free_daily: float = 0.0) -> float:
    """Annualized Sortino ratio (downside deviation only)."""
    if len(daily_pnl) < 2:
        return 0.0
    mean = sum(daily_pnl) / len(daily_pnl)
    downside = [min(0, x - risk_free_daily) ** 2 for x in daily_pnl]
    downside_var = sum(downside) / len(downside)
    downside_std = math.sqrt(downside_var) if downside_var > 0 else 0
    if downside_std == 0:
        return 0.0
    excess = mean - risk_free_daily
    return (excess / downside_std) * math.sqrt(252)


def _consecutive_streaks(trades: list) -> tuple[int, int]:
    """Max consecutive wins and losses."""
    max_wins = 0
    max_losses = 0
    current_wins = 0
    current_losses = 0

    for t in trades:
        if t.net_pnl > 0:
            current_wins += 1
            current_losses = 0
            max_wins = max(max_wins, current_wins)
        elif t.net_pnl < 0:
            current_losses += 1
            current_wins = 0
            max_losses = max(max_losses, current_losses)
        else:
            current_wins = 0
            current_losses = 0

    return max_wins, max_losses
