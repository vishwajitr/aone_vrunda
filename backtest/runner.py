#!/usr/bin/env python3
"""
CLI runner for options backtesting.

Usage:
    uv run python -m backtest.runner --strategy nifty_orb --symbol NIFTY --start 2025-01-01 --end 2025-03-31
"""

import argparse
import json
import sys

from backtest.engine import BacktestConfig, BacktestEngine
from backtest.option_pricer import PricerConfig
from backtest.data_loader import load_index_data
from backtest.strategies import get_strategy, list_strategies
from backtest.costs import INDIA_FNO_DEFAULT


def print_report(result: dict):
    """Print formatted backtest report to console."""
    metrics = result["metrics"]
    trades = result["trades"]

    s = metrics["summary"]
    p = metrics["pnl"]
    r = metrics["risk"]
    side = metrics["sides"]
    exit_r = metrics["exit_reasons"]
    timing = metrics["timing"]

    print()
    print("=" * 60)
    print("  OPTIONS BACKTEST RESULTS")
    print("=" * 60)

    print(f"\n  TRADE STATISTICS")
    print(f"    Total Trades:        {s['total_trades']}")
    print(f"    Winning:             {s['winning_trades']}")
    print(f"    Losing:              {s['losing_trades']}")
    print(f"    Win Rate:            {s['win_rate']}%")

    print(f"\n  PROFIT & LOSS")
    print(f"    Gross P&L:           {s['gross_pnl']:>12,.2f}")
    print(f"    Total Costs:         {s['total_costs']:>12,.2f}")
    print(f"    Net P&L:             {s['net_pnl']:>12,.2f}")
    print(f"    Profit Factor:       {p['profit_factor']}")
    print(f"    Avg Win:             {p['avg_win']:>12,.2f}")
    print(f"    Avg Loss:            {p['avg_loss']:>12,.2f}")
    print(f"    Expectancy:          {p['expectancy']:>12,.2f}")

    print(f"\n  CAPITAL")
    print(f"    Initial:             {s['initial_capital']:>12,.2f}")
    print(f"    Final:               {s['final_capital']:>12,.2f}")
    print(f"    Return:              {s['total_return_pct']:>11}%")

    print(f"\n  RISK")
    print(f"    Max Drawdown:        {r['max_drawdown']:>12,.2f} ({r['max_drawdown_pct']}%)")
    print(f"    Sharpe Ratio:        {r['sharpe_ratio']}")
    print(f"    Sortino Ratio:       {r['sortino_ratio']}")
    print(f"    Max Consec Wins:     {r['max_consec_wins']}")
    print(f"    Max Consec Losses:   {r['max_consec_losses']}")

    print(f"\n  BY SIDE")
    print(f"    CE: {side['ce_trades']} trades, {side['ce_win_rate']}% win rate")
    print(f"    PE: {side['pe_trades']} trades, {side['pe_win_rate']}% win rate")

    print(f"\n  EXIT REASONS")
    for reason, data in exit_r.items():
        print(f"    {reason:20s} {data['count']:>4d} ({data['pct']}%)  P&L: {data['total_pnl']:>12,.2f}")

    print(f"\n  TIMING")
    print(f"    Trading Days:        {timing['trading_days']}")
    print(f"    Trades/Day:          {timing['trades_per_day']}")
    print(f"    Avg Holding:         {timing['avg_holding_minutes']} min")

    print()
    print("=" * 60)

    # Print trade log
    if trades:
        print(f"\n  {'#':>3s}  {'Date':>12s}  {'Side':>4s}  {'Strike':>6s}  {'Entry':>8s}  {'Exit':>8s}  {'P&L':>10s}  {'Reason':>16s}")
        print("  " + "-" * 80)
        for i, t in enumerate(trades, 1):
            print(
                f"  {i:>3d}  {t['entry_date']:>12s}  {t['side']:>4s}  "
                f"{t['strike']:>6d}  {t['entry_premium']:>8.2f}  "
                f"{t['exit_premium']:>8.2f}  {t['net_pnl']:>10.2f}  "
                f"{t['exit_reason']:>16s}"
            )
        print()


def main():
    parser = argparse.ArgumentParser(description="Options Backtester")
    parser.add_argument("--strategy", default="nifty_orb", help="Strategy name")
    parser.add_argument("--list", action="store_true", help="List available strategies")
    parser.add_argument("--symbol", default="NIFTY", help="Index symbol (default: NIFTY)")
    parser.add_argument("--exchange", default="NSE_INDEX", help="Exchange (default: NSE_INDEX)")
    parser.add_argument("--interval", default="1m", help="Candle interval (default: 1m)")
    parser.add_argument("--start", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", help="End date YYYY-MM-DD")
    parser.add_argument("--capital", type=float, default=100000, help="Starting capital")
    parser.add_argument("--lots", type=int, default=1, help="Number of lots")
    parser.add_argument("--lot-size", type=int, default=50, help="Lot size")
    parser.add_argument("--sl", type=float, default=50, help="Stop loss points")
    parser.add_argument("--tp", type=float, default=0, help="Target points (0=disabled)")
    parser.add_argument("--trail", type=float, default=20, help="Trailing stop points")
    parser.add_argument("--iv", type=float, default=0.18, help="Implied volatility")
    parser.add_argument("--max-trades", type=int, default=2, help="Max trades per day")
    parser.add_argument("--max-loss-pct", type=float, default=0.10, help="Max daily loss %")
    parser.add_argument("--output", help="Export trades to CSV")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--params", help="Strategy params as JSON string")

    args = parser.parse_args()

    if args.list:
        for s in list_strategies():
            print(f"  {s['id']:20s}  {s['name']}")
            print(f"  {'':20s}  {s['description']}")
            if s["params"]:
                for k, v in s["params"].items():
                    print(f"  {'':20s}    {k}: {v['default']} ({v['min']}-{v['max']})")
            print()
        return

    strategy_params = json.loads(args.params) if args.params else {}

    config = BacktestConfig(
        initial_capital=args.capital,
        lots=args.lots,
        lot_size=args.lot_size,
        stop_loss_points=args.sl,
        target_points=args.tp,
        trailing_stop_points=args.trail,
        max_trades_per_day=args.max_trades,
        max_daily_loss_pct=args.max_loss_pct,
        pricer=PricerConfig(iv=args.iv),
        costs=INDIA_FNO_DEFAULT,
    )

    df = load_index_data(
        symbol=args.symbol,
        exchange=args.exchange,
        interval=args.interval,
        start_date=args.start,
        end_date=args.end,
    )

    if df.empty:
        print(f"\nNo data found for {args.symbol}:{args.exchange}:{args.interval}")
        print("Download data first: go to Historify in the dashboard.")
        sys.exit(1)

    strategy = get_strategy(args.strategy, strategy_params)
    engine = BacktestEngine(config)
    result = engine.run(df, strategy)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_report(result)

    if args.output:
        import csv
        with open(args.output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=result["trades"][0].keys() if result["trades"] else [])
            writer.writeheader()
            writer.writerows(result["trades"])
        print(f"Trades exported to {args.output}")


if __name__ == "__main__":
    main()
