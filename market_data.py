"""Yahoo Finance historical price tools with bounded inputs and explicit calculations."""

from __future__ import annotations

import math
import time
from datetime import datetime, timezone

import requests

from funds import ALLOWED_TICKERS

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; MianCapitalResearch/1.0)"})
_CACHE: dict[tuple[str, str], tuple[float, dict]] = {}


class MarketDataError(RuntimeError):
    pass


def price_history(ticker: str, period: str = "1y") -> dict:
    symbol = ticker.strip().upper()
    if symbol not in ALLOWED_TICKERS:
        raise MarketDataError("Ticker outside the four-fund research universe.")
    if period not in {"3mo", "6mo", "1y", "2y", "5y"}:
        raise MarketDataError("Use a supported period: 3mo, 6mo, 1y, 2y, or 5y.")
    key = (symbol, period)
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < 900:
        return {**hit[1], "cache": "hit"}
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
    try:
        response = _SESSION.get(url, params={"range": period, "interval": "1d"}, timeout=12)
        response.raise_for_status()
        chart = response.json()["chart"]
        if chart.get("error") or not chart.get("result"):
            raise MarketDataError("Yahoo did not return price history for this fund.")
        raw = chart["result"][0]
        quote = raw["indicators"]["quote"][0]
        adjusted = raw["indicators"].get("adjclose", [{}])[0].get("adjclose")
        prices = adjusted or quote.get("close") or []
        points = []
        raw_points = []
        for stamp, value in zip(raw.get("timestamp", []), prices):
            if value is not None and math.isfinite(float(value)) and float(value) > 0:
                points.append({"date": datetime.fromtimestamp(stamp, timezone.utc).date().isoformat(), "close": round(float(value), 6)})
        for stamp, value in zip(raw.get("timestamp", []), quote.get("close") or []):
            if value is not None and math.isfinite(float(value)) and float(value) > 0:
                raw_points.append({"date": datetime.fromtimestamp(stamp, timezone.utc).date().isoformat(), "close": round(float(value), 6)})
        if len(points) < 2:
            raise MarketDataError("Not enough valid prices for an analysis.")
        result = {
            "ticker": symbol,
            "currency": raw.get("meta", {}).get("currency", "USD"),
            "instrument_type": raw.get("meta", {}).get("instrumentType", "unknown"),
            "price_type": "adjusted close" if adjusted else "close",
            "source": "Yahoo Finance chart API",
            "source_url": f"https://finance.yahoo.com/quote/{symbol}/history/",
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "points": points,
            "raw_points": raw_points,
        }
        _CACHE[key] = (time.time(), result)
        return {**result, "cache": "miss"}
    except requests.RequestException as exc:
        raise MarketDataError("Market prices are temporarily unavailable from Yahoo Finance.") from exc
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise MarketDataError("Yahoo returned an unexpected price format.") from exc


def _metrics(points: list[dict]) -> dict:
    if len(points) < 3:
        raise MarketDataError("At least three trading-day prices are needed for metrics.")
    values = [p["close"] for p in points]
    daily = [values[i] / values[i - 1] - 1 for i in range(1, len(values))]
    mean = sum(daily) / len(daily)
    variance = sum((x - mean) ** 2 for x in daily) / max(1, len(daily) - 1)
    volatility = math.sqrt(variance)
    start = datetime.fromisoformat(points[0]["date"]).date()
    end = datetime.fromisoformat(points[-1]["date"]).date()
    years = max((end - start).days / 365.25, 1 / 365.25)
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1)
    return {
        "start_date": points[0]["date"],
        "end_date": points[-1]["date"],
        "observations": len(points),
        "start_price": round(values[0], 4),
        "end_price": round(values[-1], 4),
        "total_return_pct": round((values[-1] / values[0] - 1) * 100, 2),
        "cagr_pct": round(((values[-1] / values[0]) ** (1 / years) - 1) * 100, 2),
        "annualized_volatility_pct": round(volatility * math.sqrt(252) * 100, 2),
        "sharpe_ratio_zero_risk_free": round(mean / volatility * math.sqrt(252), 2) if volatility else None,
        "max_drawdown_pct": round(worst * 100, 2),
        "assumptions": "Adjusted close where Yahoo provides it; 252 trading days/year; zero risk-free rate for Sharpe; historical results do not predict future returns.",
    }


def fund_metrics(ticker: str, period: str = "1y") -> dict:
    history = price_history(ticker, period)
    return {
        "ticker": history["ticker"],
        "metrics": _metrics(history["points"]),
        "source": history["source"],
        "source_url": history["source_url"],
        "fetched_at_utc": history["fetched_at_utc"],
        "price_type": history["price_type"],
        "cache": history["cache"],
    }


def portfolio_metrics(holdings: list[dict], period: str = "1y") -> dict:
    if not holdings or len(holdings) > 4:
        raise MarketDataError("Portfolio must contain between one and four supported funds.")
    shares: dict[str, float] = {}
    histories: dict[str, dict] = {}
    for item in holdings:
        symbol = str(item.get("ticker", "")).upper()
        count = float(item.get("shares", 0))
        if symbol not in ALLOWED_TICKERS or not math.isfinite(count) or count <= 0:
            raise MarketDataError("Each holding needs a supported ticker and a positive share count.")
        shares[symbol] = shares.get(symbol, 0) + count
    for symbol in shares:
        histories[symbol] = price_history(symbol, period)
    by_date = {symbol: {p["date"]: p["close"] for p in history["raw_points"]} for symbol, history in histories.items()}
    common = sorted(set.intersection(*(set(series) for series in by_date.values())))
    if len(common) < 3:
        raise MarketDataError("The funds have too few matching trading dates.")
    first_value = sum(shares[symbol] * by_date[symbol][common[0]] for symbol in shares)
    points = [{"date": date, "close": sum(shares[symbol] * by_date[symbol][date] for symbol in shares)} for date in common]
    current_value = points[-1]["close"]
    return {
        "metrics": _metrics(points),
        "holdings": [
            {"ticker": symbol, "shares": count, "last_price": round(by_date[symbol][common[-1]], 4),
             "market_value": round(count * by_date[symbol][common[-1]], 2),
             "current_weight_pct": round(count * by_date[symbol][common[-1]] / current_value * 100, 2)}
            for symbol, count in shares.items()
        ],
        "initial_value": round(first_value, 2),
        "current_value": round(current_value, 2),
        "method": "Illustrative buy-and-hold value using fixed share counts and common trading dates. Uses raw closing prices; excludes cash, dividends/distributions, fees, taxes, and contributions.",
        "source": "Yahoo Finance chart API; raw closing prices",
        "source_urls": [histories[symbol]["source_url"] for symbol in shares],
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
