"""Transparent portfolio-level evidence tally; no religious certification."""

from __future__ import annotations

import csv
import io
import math
import re

from funds import FUNDS


class PortfolioInputError(ValueError):
    pass


def analyze_portfolio(text: str, exclusions: list[str] | None = None) -> dict:
    """Accept TICKER,USD market value rows and separate evidence from unknowns."""
    if not text or len(text) > 4000:
        raise PortfolioInputError("Enter up to 20 holdings as TICKER,market value in USD.")
    rows = list(csv.reader(io.StringIO(text.strip())))
    if rows and len(rows[0]) == 2 and rows[0][0].strip().lower() in {"ticker", "symbol"}:
        rows = rows[1:]
    if not 1 <= len(rows) <= 20:
        raise PortfolioInputError("Enter between 1 and 20 holdings.")
    merged: dict[str, float] = {}
    for row in rows:
        if len(row) != 2:
            raise PortfolioInputError("Use one holding per line: TICKER,market value. Example: HLAL,5000")
        symbol = row[0].strip().upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", symbol):
            raise PortfolioInputError(f"Invalid ticker: {row[0].strip() or '(blank)'}")
        try:
            value = float(row[1].strip().replace("$", "").replace(",", ""))
        except ValueError as exc:
            raise PortfolioInputError(f"Enter a numeric USD market value for {symbol}.") from exc
        if not math.isfinite(value) or value <= 0 or value > 10_000_000:
            raise PortfolioInputError(f"Use a positive USD market value up to $10 million for {symbol}.")
        merged[symbol] = merged.get(symbol, 0) + value
    total = sum(merged.values())
    holdings = []
    supported_value = 0.0
    unknown_value = 0.0
    for symbol, value in merged.items():
        fund = FUNDS.get(symbol)
        if fund and fund.get("source_checked_on"):
            status = "Issuer-described screened strategy"
            supported_value += value
            explanation = fund["screening_basis"]
        else:
            status = "Needs source review"
            unknown_value += value
            explanation = (
                "An issuer page is listed, but it was not verified in this project session."
                if fund else "No current screening evidence is available in this project for this ticker."
            )
        holdings.append({
            "ticker": symbol,
            "name": fund["name"] if fund else "Unreviewed security",
            "market_value": round(value, 2),
            "weight_pct": round(100 * value / total, 2),
            "status": status,
            "explanation": explanation,
            "source_url": fund["source_url"] if fund else None,
            "source_checked_on": fund.get("source_checked_on") if fund else None,
        })
    allowed_exclusions = {"tobacco", "weapons", "fossil_fuels"}
    selected = [item for item in (exclusions or []) if item in allowed_exclusions]
    return {
        "total_value": round(total, 2),
        "issuer_screened_share_pct": round(100 * supported_value / total, 2),
        "needs_review_share_pct": round(100 * unknown_value / total, 2),
        "holdings": holdings,
        "personal_exclusions": selected,
        "personal_exclusions_status": "Needs holdings-level review" if selected else "No extra exclusions selected",
        "method": "This percentage is the share of entered market value invested in funds whose issuer describes a Shariah-oriented screening strategy and whose issuer page was checked for this project. It does not measure the compliance of every current constituent, apply one universal Shariah standard, or certify the portfolio. Unreviewed positions remain unknown. Extra personal exclusions require current constituent-level data and are not included in the percentage.",
    }
