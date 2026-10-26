"""Supported fund names, tickers, and issuer references; no certification here."""

from __future__ import annotations

import re

FUNDS = {
    "HLAL": {
        "name": "Wahed FTSE USA Shariah ETF",
        "kind": "ETF",
        "issuer": "Wahed",
        "issuer_description": "The issuer describes HLAL as a Shariah-screened US equity ETF tracking the FTSE USA Shariah Index.",
        "source_url": "https://www.wahed.com/hlal",
        "screening_basis": "FTSE USA Shariah Index methodology; current constituent-level review is not performed by this app.",
        "region": "us",
        "source_checked_on": "2026-10-25",
    },
    "SPUS": {
        "name": "SP Funds S&P 500 Sharia Industry Exclusions ETF",
        "kind": "ETF",
        "issuer": "SP Funds",
        "issuer_description": "The issuer describes SPUS as a Shariah-compliant ETF with AAOIFI-based screening.",
        "source_url": "https://www.sp-funds.com/spus/",
        "screening_basis": "Issuer's AAOIFI-based screen; current constituent-level review is not performed by this app.",
        "region": "us",
        "source_checked_on": "2026-10-25",
    },
    "AMANX": {
        "name": "Amana Income Fund",
        "kind": "Mutual fund",
        "issuer": "Saturna Capital",
        "issuer_description": "Amana Income Fund is part of Saturna's Amana Funds, which follow Islamic investment principles.",
        "source_url": "https://www.saturna.com/amana/income-fund",
        "screening_basis": "Issuer-described Islamic investment principles; current holdings and ratios are not independently checked here.",
        "region": "unknown",
        "source_checked_on": None,
    },
    "AMAGX": {
        "name": "Amana Growth Fund",
        "kind": "Mutual fund",
        "issuer": "Saturna Capital",
        "issuer_description": "Amana Growth Fund is part of Saturna's Amana Funds, which follow Islamic investment principles.",
        "source_url": "https://www.saturna.com/amana/growth-fund",
        "screening_basis": "Issuer-described Islamic investment principles; current holdings and ratios are not independently checked here.",
        "region": "unknown",
        "source_checked_on": None,
    },
    "AMDWX": {
        "name": "Amana Developing World Fund",
        "kind": "Mutual fund",
        "issuer": "Saturna Capital",
        "issuer_description": "Amana Developing World Fund is an Amana mutual fund; review its current issuer materials before drawing a screening conclusion.",
        "source_url": "https://www.saturna.com/amana/developing-world-fund",
        "screening_basis": "Issuer review pending; current holdings and ratios are not checked here.",
        "region": "international",
        "source_checked_on": None,
    },
    "AMAPX": {
        "name": "Amana Participation Fund Investor Shares",
        "kind": "Mutual fund",
        "issuer": "Saturna Capital",
        "issuer_description": "Amana Participation Fund Investor Shares are listed in USD; review current issuer materials before drawing a screening conclusion.",
        "source_url": "https://www.saturna.com/amana/participation-fund",
        "screening_basis": "Issuer review pending; current holdings and ratios are not checked here.",
        "region": "unknown",
        "source_checked_on": None,
    },
    "SPRE": {
        "name": "SP Funds S&P Global REIT Sharia ETF",
        "kind": "ETF",
        "issuer": "SP Funds",
        "issuer_description": "The issuer describes SPRE as a Shariah-oriented global REIT ETF.",
        "source_url": "https://www.sp-funds.com/spre/",
        "screening_basis": "Issuer's Shariah screen; current constituent-level review is not performed by this app.",
        "region": "global",
        "source_checked_on": "2026-10-25",
    },
    "SPSK": {
        "name": "SP Funds Dow Jones Global Sukuk ETF",
        "kind": "ETF",
        "issuer": "SP Funds",
        "issuer_description": "The issuer describes SPSK as an ETF investing in sukuk.",
        "source_url": "https://www.sp-funds.com/spsk/",
        "screening_basis": "Issuer's sukuk index methodology; current holdings are not independently checked here.",
        "region": "global",
        "source_checked_on": "2026-10-25",
    },
    "UMMA": {
        "name": "Wahed Dow Jones Islamic World ETF",
        "kind": "ETF",
        "issuer": "Wahed",
        "issuer_description": "The issuer describes UMMA as an ETF following the Dow Jones Islamic Market International Titans 100 Index.",
        "source_url": "https://www.wahed.com/umma",
        "screening_basis": "Issuer's Islamic index methodology; current constituent-level review is not performed by this app.",
        "region": "international",
        "source_checked_on": "2026-10-25",
    },
    "SPWO": {
        "name": "SP Funds S&P World (ex-US) Sharia Industry Exclusions ETF",
        "kind": "ETF",
        "issuer": "SP Funds",
        "issuer_description": "The issuer describes SPWO as a Shariah-oriented international equity ETF.",
        "source_url": "https://www.sp-funds.com/spwo/",
        "screening_basis": "Issuer's Shariah screen; current constituent-level review is not performed by this app.",
        "region": "international",
        "source_checked_on": "2026-10-25",
    },
    "SPY": {
        "name": "SPDR S&P 500 ETF Trust",
        "kind": "Market comparison ETF",
        "issuer": "State Street",
        "issuer_description": "SPY tracks the S&P 500 and is included only as a broad US market comparison, with no Shariah-screening claim.",
        "source_url": "https://www.ssga.com/us/en/individual/etfs/spdr-sp-500-etf-trust-spy",
        "screening_basis": "Market comparison only; do not treat this holding as Shariah-screened.",
        "region": "us",
        "source_checked_on": None,
        "category": "benchmark",
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "kind": "Market comparison ETF",
        "issuer": "Invesco",
        "issuer_description": "QQQ tracks the Nasdaq-100, not the Nasdaq Composite, and is included only as a market comparison with no Shariah-screening claim.",
        "source_url": "https://www.invesco.com/qqq-etf/en/home.html",
        "screening_basis": "Market comparison only; do not treat this holding as Shariah-screened.",
        "region": "us",
        "source_checked_on": None,
        "category": "benchmark",
    },
}

ALLOWED_TICKERS = frozenset(FUNDS)
BENCHMARK_TICKERS = frozenset(ticker for ticker, fund in FUNDS.items() if fund.get("category") == "benchmark")
SHARIAH_RESEARCH_TICKERS = ALLOWED_TICKERS - BENCHMARK_TICKERS

ALIASES = {
    "HLAL": ("wahed ftse usa shariah etf", "wahed usa shariah etf", "wahed ftse usa shariah"),
    "SPUS": ("sp funds s p 500 sharia industry exclusions etf", "sp funds s p 500 sharia etf"),
    "AMANX": ("amana income fund", "amana income"),
    "AMAGX": ("amana growth fund", "amana growth"),
    "AMDWX": ("amana developing world fund", "amana developing world"),
    "AMAPX": ("amana participation fund", "amana participation", "amana participation fund investor shares"),
    "SPRE": ("sp funds s p global reit sharia etf", "sp funds global reit sharia etf"),
    "SPSK": ("sp funds dow jones global sukuk etf", "dow jones global sukuk etf"),
    "UMMA": ("wahed dow jones islamic world etf", "wahed islamic world etf"),
    "SPWO": ("sp funds s p world ex us sharia industry exclusions etf", "sp funds world ex us sharia etf"),
    "SPY": ("spdr s p 500 etf trust", "s p 500 etf", "spdr spy"),
    "QQQ": ("invesco qqq trust", "nasdaq 100 etf", "nasdaq 100", "invesco qqq"),
}


def resolve_fund_mentions(text: str) -> dict[str, str]:
    """Find unambiguous public fund names and symbols in a user's wording."""
    normalized = " " + re.sub(r"[^a-z0-9]+", " ", text.lower()).strip() + " "
    found = {}
    for ticker, aliases in ALIASES.items():
        for alias in aliases:
            if f" {alias} " in normalized:
                found[alias] = ticker
                break
    for ticker in ALLOWED_TICKERS:
        if f" {ticker.lower()} " in normalized:
            found[ticker] = ticker
    return found


def fund_profile(ticker: str) -> dict:
    symbol = ticker.strip().upper()
    if symbol not in FUNDS:
        return {
            "ticker": symbol,
            "status": "outside_current_universe",
            "message": "This ticker is outside the current research list. No compliance conclusion is available.",
        }
    return {
        "ticker": symbol,
        **FUNDS[symbol],
        "status": "market_comparison_only" if symbol in BENCHMARK_TICKERS else ("issuer_described_only" if FUNDS[symbol]["source_checked_on"] else "needs_source_review"),
        "finding": (
            "This is a broad-market comparison, not a Shariah-screened holding."
            if symbol in BENCHMARK_TICKERS
            else ("Issuer describes an Islamic or Shariah-oriented strategy; this app has not independently certified compliance."
                  if FUNDS[symbol]["source_checked_on"]
                  else "This Amana fund needs a current official-source review before any screening claim is relied on.")
        ),
    }
