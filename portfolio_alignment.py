"""Transparent portfolio-level evidence tally; no religious certification."""

from __future__ import annotations

import csv
import io
import math
import re

from funds import FUNDS

REGION_LABELS = {
    "us": "US-focused",
    "international": "International-focused",
    "global": "Global mandate",
    "unknown": "Region not verified",
}

EXCLUSION_LABELS = {
    "alcohol": "Alcohol",
    "gambling": "Gambling",
    "high_debt": "High debt / leverage",
    "tobacco": "Tobacco",
    "ordnance": "Ordnance",
    "fossil_fuels": "Fossil fuels",
}

EXCLUSION_NOTES = {
    "alcohol": "Issuer Shariah strategies may exclude alcohol, but current holdings and revenue exposure were not independently checked.",
    "gambling": "Current constituent exposure to gambling was not independently checked.",
    "high_debt": "No company debt ratios were calculated. Screening standards use different denominators and thresholds, so this needs a chosen method and current financial data.",
    "tobacco": "Current constituent exposure to tobacco was not checked.",
    "ordnance": "Current constituent exposure to ordnance was not checked.",
    "fossil_fuels": "Current constituent exposure to fossil fuels was not checked.",
}


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
    region_values = {region: 0.0 for region in REGION_LABELS}
    for symbol, value in merged.items():
        fund = FUNDS.get(symbol)
        region = fund.get("region", "unknown") if fund else "unknown"
        region_values[region] += value
        if fund and fund.get("category") == "benchmark":
            status = "Market comparison · no Shariah screen established"
            unknown_value += value
            explanation = "SPY and QQQ are broad-market comparison ETFs. This app does not classify them as Shariah-compliant; review the underlying holdings against your chosen methodology."
        elif fund and fund.get("source_checked_on"):
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
            "region": region,
            "region_label": REGION_LABELS[region],
        })
    selected = [item for item in (exclusions or []) if item in EXCLUSION_LABELS]
    return {
        "total_value": round(total, 2),
        "issuer_screened_share_pct": round(100 * supported_value / total, 2),
        "needs_review_share_pct": round(100 * unknown_value / total, 2),
        "holdings": holdings,
        "region_breakdown": [
            {"region": region, "label": REGION_LABELS[region], "value": round(value, 2), "weight_pct": round(100 * value / total, 2)}
            for region, value in region_values.items() if value > 0
        ],
        "personal_exclusions": selected,
        "exclusion_checks": [
            {"key": item, "label": EXCLUSION_LABELS[item], "status": "Needs review", "detail": EXCLUSION_NOTES[item]}
            for item in selected
        ],
        "personal_exclusions_status": "Needs holdings-level review" if selected else "No extra exclusions selected",
        "method": "This percentage is the share of entered market value invested in funds whose issuer describes a Shariah-oriented screening strategy and whose issuer page was checked for this project. Geography reflects the fund's stated mandate, not a verified look-through to every underlying holding. It does not measure the compliance of every current constituent, calculate debt ratios, apply one universal Shariah standard, or certify the portfolio. Unreviewed positions remain unknown. Extra exclusions require current company or fund holdings data and are not included in the percentage.",
    }


def visible_holdings(result: dict, region: str = "all", sort_by: str = "weight") -> list[dict]:
    """Filter displayed rows without changing whole-portfolio percentages."""
    if region not in {*REGION_LABELS, "all"}:
        raise PortfolioInputError("Choose a supported geography filter.")
    if sort_by not in {"weight", "ticker", "review"}:
        raise PortfolioInputError("Choose a supported sort order.")
    rows = [item for item in result["holdings"] if region == "all" or item["region"] == region]
    if sort_by == "ticker":
        return sorted(rows, key=lambda item: item["ticker"])
    if sort_by == "review":
        return sorted(rows, key=lambda item: (item["status"] != "Needs source review", -item["market_value"]))
    return sorted(rows, key=lambda item: (-item["market_value"], item["ticker"]))
