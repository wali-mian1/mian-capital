"""Bounded yfinance price retrieval for the supported fund universe."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import yfinance as yf

from funds import ALLOWED_TICKERS


class PriceToolError(ValueError):
    pass


def get_stock_price(ticker: str, start: str, stop: str) -> dict:
    """Return historical daily closes. `stop` is exclusive, as in yfinance."""
    symbol = ticker.strip().upper()
    if symbol not in ALLOWED_TICKERS:
        raise PriceToolError("Use a supported fund ticker; do not pass a fund name to yfinance.")
    try:
        first = date.fromisoformat(start)
        last = date.fromisoformat(stop)
    except ValueError as exc:
        raise PriceToolError("start and stop must be ISO dates in YYYY-MM-DD form.") from exc
    today = datetime.now(ZoneInfo("America/New_York")).date()
    if not first < last:
        raise PriceToolError("start must be before stop.")
    if last > today + timedelta(days=1):
        raise PriceToolError("stop cannot be later than tomorrow in New York.")
    if (last - first).days > 366:
        raise PriceToolError("The maximum date range is one year per call.")
    try:
        frame = yf.Ticker(symbol).history(start=start, end=stop, auto_adjust=False, actions=False)
    except Exception as exc:
        raise PriceToolError("Yahoo Finance is temporarily unavailable.") from exc
    fallback_start = None
    if frame.empty and (last - first).days <= 5 and first >= today - timedelta(days=7):
        fallback_start = (first - timedelta(days=14)).isoformat()
        try:
            frame = yf.Ticker(symbol).history(start=fallback_start, end=stop, auto_adjust=False, actions=False)
        except Exception as exc:
            raise PriceToolError("Yahoo Finance is temporarily unavailable.") from exc
    if frame.empty or "Close" not in frame:
        raise PriceToolError("No price observations were available for that fund and date range.")
    rows = []
    for stamp, value in frame["Close"].items():
        amount = float(value)
        if math.isfinite(amount) and amount > 0:
            rows.append({"date": stamp.date().isoformat(), "close_usd": round(amount, 4)})
    # Before the 4 p.m. New York close, Yahoo's row for today is a live price, not a close.
    if rows and rows[-1]["date"] == today.isoformat() and datetime.now(ZoneInfo("America/New_York")).hour < 16:
        rows.pop()
    if not rows:
        raise PriceToolError("No valid closing prices were returned.")
    shown = rows if len(rows) <= 24 else rows[:12] + rows[-12:]
    return {
        "ticker": symbol,
        "requested_start": start,
        "requested_stop_exclusive": stop,
        "extended_start_for_latest_close": fallback_start,
        "source": "Yahoo Finance via yfinance",
        "source_url": f"https://finance.yahoo.com/quote/{symbol}/history/",
        "observations": len(rows),
        "first_date": rows[0]["date"],
        "last_date": rows[-1]["date"],
        "first_close_usd": rows[0]["close_usd"],
        "last_close_usd": rows[-1]["close_usd"],
        "change_pct": round((rows[-1]["close_usd"] / rows[0]["close_usd"] - 1) * 100, 2) if len(rows) > 1 else None,
        "prices": shown,
        "prices_sampled": len(rows) > len(shown),
        "note": "Daily raw closes; stop date is exclusive; last available close may be delayed. Change excludes distributions. If the short requested window had no trading day, the start was extended and is shown above.",
    }
