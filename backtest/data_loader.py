"""
Data loader for backtesting.

Fetches index OHLCV from the local DuckDB historify database.
"""

import pandas as pd
from datetime import datetime

from utils.logging import get_logger

logger = get_logger(__name__)


def load_index_data(
    symbol: str = "NIFTY",
    exchange: str = "NSE_INDEX",
    interval: str = "1m",
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Load index OHLCV data from DuckDB for backtesting.

    Args:
        symbol: Index symbol (e.g. NIFTY, BANKNIFTY, SENSEX)
        exchange: Exchange code (NSE_INDEX, BSE_INDEX)
        interval: Candle interval (1m, 5m, 15m, 30m, 1h)
        start_date: Start date string (YYYY-MM-DD), None for all data
        end_date: End date string (YYYY-MM-DD), None for all data

    Returns:
        DataFrame with columns: datetime, open, high, low, close, volume
        Sorted by datetime ascending, with datetime as the index.
    """
    from database.historify_db import get_ohlcv

    start_ts = None
    end_ts = None

    if start_date:
        dt = datetime.strptime(start_date, "%Y-%m-%d")
        start_ts = int(dt.timestamp())
    if end_date:
        dt = datetime.strptime(end_date, "%Y-%m-%d")
        end_ts = int(dt.timestamp()) + 86399

    df = get_ohlcv(
        symbol=symbol.upper(),
        exchange=exchange.upper(),
        interval=interval,
        start_timestamp=start_ts,
        end_timestamp=end_ts,
    )

    if df.empty:
        logger.warning(
            "No data found for %s:%s:%s (%s to %s)",
            symbol, exchange, interval, start_date, end_date,
        )
        return df

    # Convert epoch to datetime
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    df.set_index("datetime", inplace=True)
    df.drop(columns=["timestamp"], inplace=True)

    # Add helper columns for intraday filtering
    df["date"] = df.index.date
    df["time"] = df.index.time
    df["hour"] = df.index.hour
    df["minute"] = df.index.minute

    logger.info(
        "Loaded %d candles for %s:%s:%s (%s to %s)",
        len(df), symbol, exchange, interval,
        df.index.min(), df.index.max(),
    )

    return df


def load_csv_data(filepath: str) -> pd.DataFrame:
    """
    Load OHLCV data from a CSV file.

    Expected columns: datetime (or date/time), open, high, low, close, volume
    """
    df = pd.read_csv(filepath)

    # Try to find datetime column
    datetime_col = None
    for col in ["datetime", "date", "Date", "Datetime", "timestamp"]:
        if col in df.columns:
            datetime_col = col
            break

    if datetime_col is None:
        raise ValueError(f"No datetime column found in {filepath}")

    df["datetime"] = pd.to_datetime(df[datetime_col])
    df.set_index("datetime", inplace=True)

    if datetime_col != "datetime":
        df.drop(columns=[datetime_col], inplace=True)

    # Normalize column names
    col_map = {}
    for col in df.columns:
        lower = col.lower()
        if lower in ("open", "high", "low", "close", "volume"):
            col_map[col] = lower.capitalize()
    if col_map:
        df.rename(columns=col_map, inplace=True)

    # Add helper columns
    df["date"] = df.index.date
    df["time"] = df.index.time
    df["hour"] = df.index.hour
    df["minute"] = df.index.minute

    df.sort_index(inplace=True)

    logger.info("Loaded %d candles from %s", len(df), filepath)
    return df


def get_available_data_info(
    symbol: str = "NIFTY",
    exchange: str = "NSE_INDEX",
) -> dict:
    """Check what data is available in DuckDB for a symbol."""
    from database.historify_db import get_data_range

    ranges = {}
    for interval in ["1m", "5m", "15m", "D"]:
        info = get_data_range(symbol, exchange, interval)
        if info:
            ranges[interval] = info

    return {
        "symbol": symbol,
        "exchange": exchange,
        "available_intervals": ranges,
    }
