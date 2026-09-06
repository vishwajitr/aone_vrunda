"""
Nifty Opening Range Breakout (ORB) Strategy

Backtests the ORB strategy using the generic BacktestEngine.
Entry: buy CE on upside breakout, buy PE on downside breakout of first candle range.
Exit: SL, trailing stop, or EOD.
"""

from backtest.engine import Signal, Candle, Position


class NiftyORBStrategy:
    """
    Opening Range Breakout strategy for intraday options buying.

    Logic:
    1. Wait for first 1-minute candle (9:15 AM) to establish the ORB range.
    2. BUY CE if price breaks above ORB high + buffer.
    3. BUY PE if price breaks below ORB low - buffer.
    4. Stop loss at opposite ORB level (mapped to premium via Black-76).
    """

    def __init__(
        self,
        orb_buffer: float = 3.0,
        max_entry_hour: int = 15,
        max_entry_minute: int = 0,
    ):
        self.orb_high = None
        self.orb_low = None
        self.orb_range = None
        self.orb_established = False
        self.current_date = None
        self.orb_buffer = orb_buffer
        self.max_entry_time = (max_entry_hour, max_entry_minute)

    def on_candle(self, candle: Candle, position: Position | None, capital: float) -> Signal:
        # Reset on new day
        if candle.date != self.current_date:
            self.current_date = candle.date
            self.orb_high = None
            self.orb_low = None
            self.orb_range = None
            self.orb_established = False

        # First candle: establish ORB
        if not self.orb_established:
            self.orb_high = candle.high
            self.orb_low = candle.low
            self.orb_range = candle.high - candle.low
            self.orb_established = True
            return Signal.HOLD

        # Only check for breakout within allowed time
        if (candle.hour, candle.minute) > self.max_entry_time:
            return Signal.HOLD

        # Already have a position
        if position is not None:
            return Signal.HOLD

        # Check for upside breakout
        if candle.close > self.orb_high + self.orb_buffer:
            return Signal.BUY_CE

        # Check for downside breakout
        if candle.close < self.orb_low - self.orb_buffer:
            return Signal.BUY_PE

        return Signal.HOLD


# Strategy registry for the API
STRATEGIES = {
    "nifty_orb": {
        "name": "Nifty Opening Range Breakout",
        "description": "Buy CE on upside breakout, buy PE on downside breakout of first candle range",
        "class": NiftyORBStrategy,
        "params": {
            "orb_buffer": {"type": "float", "default": 3.0, "min": 0, "max": 20, "label": "ORB Buffer (points)"},
            "max_entry_hour": {"type": "int", "default": 15, "min": 9, "max": 15, "label": "Last Entry Hour"},
            "max_entry_minute": {"type": "int", "default": 0, "min": 0, "max": 59, "label": "Last Entry Minute"},
        },
    },
}


def get_strategy(name: str, params: dict | None = None) -> object:
    """Instantiate a strategy by name with optional params."""
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGIES.keys())}")
    info = STRATEGIES[name]
    cls = info["class"]
    if params:
        return cls(**params)
    return cls()


def list_strategies() -> list[dict]:
    """List available strategies."""
    return [
        {
            "id": key,
            "name": val["name"],
            "description": val["description"],
            "params": val["params"],
        }
        for key, val in STRATEGIES.items()
    ]
