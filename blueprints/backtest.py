"""
Backtest Blueprint
REST API endpoints for running options backtests.
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from utils.logging import get_logger

logger = get_logger(__name__)

backtest_bp = Blueprint("backtest_bp", __name__, url_prefix="/backtest")


@backtest_bp.route("/api/strategies", methods=["GET"])
@cross_origin()
def list_strategies():
    """List available backtesting strategies."""
    from backtest.strategies import list_strategies as _list
    return jsonify({"status": "success", "strategies": _list()})


@backtest_bp.route("/api/data", methods=["POST"])
@cross_origin()
def check_data():
    """Check available data for a symbol in DuckDB."""
    from backtest.data_loader import get_available_data_info

    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol", "NIFTY").upper()
    exchange = data.get("exchange", "NSE_INDEX").upper()

    info = get_available_data_info(symbol, exchange)
    return jsonify({"status": "success", "data": info})


@backtest_bp.route("/api/run", methods=["POST"])
@cross_origin()
def run_backtest():
    """
    Run a backtest.

    Request JSON:
    {
        "strategy": "nifty_orb",
        "strategy_params": {"orb_buffer": 3.0},
        "symbol": "NIFTY",
        "exchange": "NSE_INDEX",
        "interval": "1m",
        "start_date": "2025-01-01",
        "end_date": "2025-03-31",
        "config": {
            "initial_capital": 100000,
            "lots": 1,
            "lot_size": 50,
            "stop_loss_points": 50,
            "trailing_stop_points": 20,
            "max_trades_per_day": 2,
            "max_daily_loss_pct": 0.10,
            "iv": 0.18,
            "risk_free_rate": 0.065
        }
    }
    """
    try:
        data = request.get_json(silent=True) or {}

        strategy_name = data.get("strategy", "nifty_orb")
        strategy_params = data.get("strategy_params", {})
        symbol = data.get("symbol", "NIFTY").upper()
        exchange = data.get("exchange", "NSE_INDEX").upper()
        interval = data.get("interval", "1m")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        # Build backtest config
        from backtest.engine import BacktestConfig
        from backtest.option_pricer import PricerConfig
        from backtest.costs import INDIA_FNO_DEFAULT

        cfg = data.get("config", {})

        pricer = PricerConfig(
            iv=cfg.get("iv", 0.18),
            risk_free_rate=cfg.get("risk_free_rate", 0.065),
            strike_rounding=cfg.get("strike_rounding", 50),
        )

        config = BacktestConfig(
            initial_capital=cfg.get("initial_capital", 100_000.0),
            lots=cfg.get("lots", 1),
            lot_size=cfg.get("lot_size", 50),
            stop_loss_points=cfg.get("stop_loss_points", 50.0),
            target_points=cfg.get("target_points", 0.0),
            trailing_activate_at=cfg.get("trailing_activate_at", 0.0),
            trailing_stop_points=cfg.get("trailing_stop_points", 20.0),
            max_trades_per_day=cfg.get("max_trades_per_day", 2),
            max_daily_loss_pct=cfg.get("max_daily_loss_pct", 0.10),
            last_entry_time=cfg.get("last_entry_time", "15:00"),
            eod_exit_time=cfg.get("eod_exit_time", "15:25"),
            pricer=pricer,
            costs=INDIA_FNO_DEFAULT,
        )

        # Load data
        from backtest.data_loader import load_index_data

        df = load_index_data(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )

        if df.empty:
            return jsonify({
                "status": "error",
                "message": f"No data found for {symbol}:{exchange}. Download data first via Historify.",
            }), 400

        # Instantiate strategy
        from backtest.strategies import get_strategy

        strategy = get_strategy(strategy_name, strategy_params)

        # Run backtest
        from backtest.engine import BacktestEngine

        engine = BacktestEngine(config)
        result = engine.run(df, strategy)

        return jsonify({"status": "success", "result": result})

    except Exception as e:
        logger.exception("Backtest failed: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@backtest_bp.route("/api/pricer/quote", methods=["POST"])
@cross_origin()
def get_option_quote():
    """
    Get a synthetic option quote for a given spot price.

    Useful for previewing what premium the pricer generates.
    """
    from backtest.option_pricer import PricerConfig, quote_option

    data = request.get_json(silent=True) or {}
    spot = data.get("spot", 0)
    flag = data.get("flag", "c")
    iv = data.get("iv", 0.18)
    risk_free_rate = data.get("risk_free_rate", 0.065)
    strike_rounding = data.get("strike_rounding", 50)
    minutes_elapsed = data.get("minutes_elapsed", 0)

    if spot <= 0:
        return jsonify({"status": "error", "message": "spot must be > 0"}), 400

    config = PricerConfig(
        iv=iv,
        risk_free_rate=risk_free_rate,
        strike_rounding=strike_rounding,
    )

    quote = quote_option(spot, config, flag, minutes_elapsed)

    return jsonify({
        "status": "success",
        "quote": {
            "strike": quote.strike,
            "flag": quote.flag,
            "spot": quote.spot,
            "premium": round(quote.premium, 2),
            "delta": round(quote.delta, 4),
            "iv": quote.iv,
            "time_to_expiry_days": round(quote.time_to_expiry_days, 2),
        },
    })
