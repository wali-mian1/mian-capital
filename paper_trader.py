"""Educational paper-money scenarios. No orders, accounts, or forecasts."""

from __future__ import annotations

import math
import re
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import yfinance as yf

_CACHE: dict[tuple[str, str, str], tuple[float, object, str]] = {}
_NY = ZoneInfo("America/New_York")


class PaperTradeError(ValueError):
    pass


def _ticker(value: str) -> str:
    symbol = (value or "").strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.\-^]{0,9}", symbol):
        raise PaperTradeError("Enter a valid ticker symbol, such as HLAL or AMAGX.")
    return symbol


def _amount(value: float | int | str) -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise PaperTradeError("Enter a paper-money amount.") from exc
    if not math.isfinite(amount) or not 100 <= amount <= 1_000_000:
        raise PaperTradeError("Use a paper-money amount from $100 to $1,000,000.")
    return amount


def _history(symbol: str, start: date, stop: date):
    key = (symbol, start.isoformat(), stop.isoformat())
    cached = _CACHE.get(key)
    if cached and time.time() - cached[0] < 900:
        return cached[1].copy(), cached[2]
    try:
        security = yf.Ticker(symbol)
        frame = security.history(start=key[1], end=key[2], auto_adjust=False, actions=False)
        currency = security.history_metadata.get("currency") or "USD"
    except Exception as exc:
        raise PaperTradeError("Historical prices are temporarily unavailable. Try again later.") from exc
    if frame.empty or "Close" not in frame:
        raise PaperTradeError("No historical prices were found for this ticker and date range.")
    if currency != "USD":
        raise PaperTradeError(f"This first version supports USD-listed securities; Yahoo reports {currency} for {symbol}.")
    _CACHE[key] = (time.time(), frame.copy(), currency)
    return frame, currency


def _points(series, amount: float) -> list[dict]:
    values = [(stamp.date().isoformat(), float(value)) for stamp, value in series.items() if math.isfinite(float(value)) and float(value) > 0]
    if not values:
        raise PaperTradeError("Yahoo returned no valid prices for this scenario.")
    first = values[0][1]
    step = max(1, len(values) // 180)
    sampled = values[::step]
    if sampled[-1] != values[-1]:
        sampled.append(values[-1])
    return [{"date": day, "investment_value": round(amount * value / first, 2), "cash_at_zero_interest": round(amount, 2)} for day, value in sampled]


def simulate_historical(ticker: str, amount: float, purchase_date: str) -> dict:
    symbol = _ticker(ticker)
    principal = _amount(amount)
    try:
        requested = date.fromisoformat(purchase_date)
    except (TypeError, ValueError) as exc:
        raise PaperTradeError("Choose a purchase date in YYYY-MM-DD form.") from exc
    today = datetime.now(_NY).date()
    if requested > today:
        raise PaperTradeError("A historical purchase date cannot be in the future.")
    if requested < today - timedelta(days=3653):
        raise PaperTradeError("Choose a date within the last ten years.")
    frame, currency = _history(symbol, requested, today + timedelta(days=1))
    raw = frame["Close"].dropna()
    adjusted = frame["Adj Close"].dropna() if "Adj Close" in frame else raw
    common = raw.index.intersection(adjusted.index)
    if len(common) > 1 and common[-1].date() == today and datetime.now(_NY).hour < 16:
        common = common[:-1]  # today's row is a live price until the 4 p.m. close
    raw = raw.loc[common]
    adjusted = adjusted.loc[common]
    if len(common) < 1:
        raise PaperTradeError("No valid trading-day prices were found.")
    first_date = common[0].date()
    if first_date > requested + timedelta(days=7):
        raise PaperTradeError(f"No trading price was available near {requested.isoformat()}; this security may not have existed then.")
    first_close = float(raw.iloc[0])
    last_close = float(raw.iloc[-1])
    first_adjusted = float(adjusted.iloc[0])
    last_adjusted = float(adjusted.iloc[-1])
    if not all(math.isfinite(x) and x > 0 for x in (first_close, last_close, first_adjusted, last_adjusted)):
        raise PaperTradeError("Yahoo returned an invalid price for this scenario.")
    ending = principal * last_adjusted / first_adjusted
    years = (common[-1].date() - first_date).days / 365.25
    cagr = ((ending / principal) ** (1 / years) - 1) * 100 if years >= 30 / 365.25 else None
    peak = float(adjusted.iloc[0])
    worst = 0.0
    for value in adjusted:
        peak = max(peak, float(value))
        worst = min(worst, float(value) / peak - 1)
    return {
        "mode": "historical",
        "ticker": symbol,
        "currency": currency,
        "requested_purchase_date": requested.isoformat(),
        "actual_purchase_date": first_date.isoformat(),
        "last_price_date": common[-1].date().isoformat(),
        "initial_amount": round(principal, 2),
        "initial_close": round(first_close, 4),
        "latest_close": round(last_close, 4),
        "illustrative_shares": round(principal / first_close, 4),
        "ending_value": round(ending, 2),
        "gain_loss": round(ending - principal, 2),
        "total_return_pct": round((ending / principal - 1) * 100, 2),
        "annualized_return_pct": round(cagr, 2) if cagr is not None else None,
        "max_drawdown_pct": round(worst * 100, 2),
        "series": _points(adjusted, principal),
        "source_url": f"https://finance.yahoo.com/quote/{symbol}/history/",
        "method": "Historical illustration using Yahoo adjusted close as a total-return proxy, with dividends assumed reinvested where Yahoo supplies adjustment data. Fractional shares allowed. No fees, taxes, inflation, or real trades. Cash line assumes 0% interest.",
    }


def simulate_future(ticker: str, amount: float, years: int, assumed_annual_return_pct: float) -> dict:
    symbol = _ticker(ticker)
    principal = _amount(amount)
    try:
        horizon = int(years)
        rate = float(assumed_annual_return_pct)
    except (TypeError, ValueError) as exc:
        raise PaperTradeError("Enter a whole-year horizon and an assumed annual return.") from exc
    if not 1 <= horizon <= 30:
        raise PaperTradeError("Use a horizon from 1 to 30 years.")
    if not math.isfinite(rate) or not -30 <= rate <= 30:
        raise PaperTradeError("Use an assumed annual return between -30% and 30%.")
    today = datetime.now(_NY).date()
    frame, currency = _history(symbol, today - timedelta(days=21), today + timedelta(days=1))
    raw = frame["Close"].dropna()
    # Before the 4 p.m. New York close, Yahoo's row for today is a live price, not a close.
    if len(raw) > 1 and raw.index[-1].date() == today and datetime.now(_NY).hour < 16:
        raw = raw.iloc[:-1]
    if raw.empty or not math.isfinite(float(raw.iloc[-1])) or float(raw.iloc[-1]) <= 0:
        raise PaperTradeError("The latest price is unavailable for this ticker.")
    latest_close = float(raw.iloc[-1])
    series = [{"year": year, "investment_value": round(principal * (1 + rate / 100) ** year, 2), "cash_at_zero_interest": round(principal, 2)} for year in range(horizon + 1)]
    ending = series[-1]["investment_value"]
    return {
        "mode": "future",
        "ticker": symbol,
        "currency": currency,
        "last_price_date": raw.index[-1].date().isoformat(),
        "latest_close": round(latest_close, 4),
        "initial_amount": round(principal, 2),
        "illustrative_shares": round(principal / latest_close, 4),
        "horizon_years": horizon,
        "assumed_annual_return_pct": round(rate, 2),
        "ending_value": round(ending, 2),
        "gain_loss": round(ending - principal, 2),
        "total_return_pct": round((ending / principal - 1) * 100, 2),
        "series": series,
        "source_url": f"https://finance.yahoo.com/quote/{symbol}/history/",
        "method": "Illustration of compound growth using the rate you selected. This is not a forecast for the ticker. Cash line assumes 0% interest. No contributions, fees, taxes, or inflation; no real trades.",
    }


def average_annual_return(ticker: str, max_years: int = 10) -> dict:
    """Annualized total return from Yahoo adjusted closes over up to `max_years` (or since listing)."""
    symbol = _ticker(ticker)
    today = datetime.now(_NY).date()
    frame, _ = _history(symbol, today - timedelta(days=round(365.25 * max_years) + 7), today + timedelta(days=1))
    adjusted = frame["Adj Close"] if "Adj Close" in frame else frame["Close"]
    series = adjusted.dropna()
    series = series[series > 0]
    if len(series) < 2:
        raise PaperTradeError("Not enough price history to calculate an average return.")
    first_day, last_day = series.index[0].date(), series.index[-1].date()
    years = (last_day - first_day).days / 365.25
    if years < 1:
        raise PaperTradeError("This ticker has less than a year of price history.")
    rate = (float(series.iloc[-1]) / float(series.iloc[0])) ** (1 / years) - 1
    return {
        "ticker": symbol,
        "average_annual_return_pct": round(rate * 100, 2),
        "years": round(years, 1),
        "start": first_day.isoformat(),
        "end": last_day.isoformat(),
        "source_url": f"https://finance.yahoo.com/quote/{symbol}/history/",
    }
