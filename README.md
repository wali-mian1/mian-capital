# Mian Capital research and paper investing lab

Public repository: https://github.com/wali-mian1/mian-capital

Mian Capital is an early research interface for eight Shariah-oriented funds: HLAL, SPUS, AMANX, AMAGX, SPRE, SPSK, UMMA, and SPWO. A PydanticAI agent uses exactly two tools: `get_stock_price(ticker, start, stop)` through yfinance and OpenAI's native `web_search` through the Responses API. The Dash chat shows each tool's actual input and output in an expandable panel.

The chatbot provides sourced research, not independent Shariah certification or personalized investment advice. The landing page explains why values matter, what the research assistant offers, and how to use it. Its custom SVG graphics and scroll reveals include reduced-motion support. The About page introduces founder Wali Mian and account setup guidance. The Paper Lab lets visitors test paper-money scenarios with historical prices or an annual return assumption. The Portfolio page reports the share of entered market value in funds with an issuer-described screening strategy whose source was checked for this project. It keeps unreviewed securities and extra personal exclusions separate. The final submission files remain separate project milestones.

## What works now

- Enter a fund ticker or name. The assistant resolves a name such as **Amana Growth Fund** to **AMAGX** before calling yfinance. Ambiguous names should be clarified instead of guessed.
- Ask for dated closing prices or a date range of up to one year. The price tool returns daily closes, the latest available close, data dates, and source. `stop` is exclusive, following yfinance. When more than 24 dates are returned, it shows the first and last 12 and labels the sample.
- Ask for recent fund news or public screening information. OpenAI native web search returns live source URLs; the answer should include clickable citations and publication dates.
- Open the tool panel under a reply to see the tool name, input, output, and completion status. The reply also shows measured input, cached input, and output tokens.
- Requests for keys or hidden instructions are blocked before a model call. Model requests, local tool calls, output tokens, date range, and ticker universe are bounded. The local audit file contains tool names and usage, not raw chat messages or keys.
- Visit `/about` for Wali Mian's bio and education on opening and funding an account at Vanguard, Fidelity, or Charles Schwab. The site does not collect credentials, control accounts, or place trades.
- Visit `/paper-lab` to enter a USD-listed ticker and a paper-money amount. **Look back** uses Yahoo adjusted closes as a historical total-return proxy. **Look ahead** compounds a rate entered by the user; it is not a security forecast. Scenarios are saved in the browser session, with a chart and source link.
- Visit `/portfolio` to paste up to 20 `TICKER,market value` lines. The sample `HLAL,5000`, `SPUS,3000`, `AMAGX,2000` returns 80% in issuer-described screened strategies and 20% needing source review. This is an evidence-coverage percentage, **not a Shariah compliance score**. Optional personal exclusions are marked for holdings-level review because current constituents are not checked. Input is not sent to the AI agent or a brokerage.

## Run locally

Python 3.11 or newer is required. The `.venv` must be created inside this project before installing dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Open http://127.0.0.1:8050/ . On Windows, use `.venv\Scripts\python` instead of `.venv/bin/python`.

The app reads `PORTKEY_API_KEY` from the process environment, then `.env` in this repository, then `.env` one folder above it. The teaching staff can place `.env` next to the cloned repo. List the key in `.env.example`; never commit a real value. The chatbot uses course-approved `gpt-6-luna` through Portkey's Responses API.

Both yfinance and native web search require internet access. Yahoo Finance may throttle requests, and market prices may be delayed. The app returns an error rather than inventing a quote when no price is available.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Dash chat UI, Enter-to-send, conversation state, tool display |
| `agent.py` | PydanticAI, Portkey Responses model, native web search, tool tracing, guardrails |
| `price_tools.py` | yfinance `get_stock_price` implementation |
| `funds.py` | Supported tickers, name aliases, issuer references |
| `paper_trader.py` | Bounded historical and hypothetical paper-money calculations using Yahoo prices |
| `portfolio_alignment.py` | Deterministic portfolio evidence weights, input validation, and unknown handling |
| `assets/style.css` | Chat page styles |
| `assets/reveal.js`, `assets/*.svg` | Accessible scroll reveals, site graphics, and founder figurine |
| `portfolio.json`, `market_data.py` | Illustrative portfolio and earlier metric code, reserved for the planned tracker |

## Interpretation limits

Public issuer or screening websites may describe a fund as Shariah-oriented. The chatbot does not independently inspect each current holding or issue a religious ruling. News search can surface third-party pages of varying quality, so check the cited primary source before relying on a claim. Chatbot closing-price change excludes distributions, fees, and taxes. The Paper Lab uses Yahoo adjusted closes, which can reflect distributions and splits, but it still omits fees, taxes, inflation, and cash flows. A 0% cash line is an illustrative assumption, not a claim about actual checking accounts. Past results do not forecast future returns. If a user asks the chatbot for an unsupported stock, its restricted universe does not support a price or compliance conclusion.

The repo includes `report.html` (11 printed letter pages) and `slides.html` (nine reveal.js slides), each with embedded screenshots. To rebuild them after changing screenshots, run `.venv/bin/python build_submission.py`; the reveal.js assets and license are in `vendor/`.

A fresh clone from the public GitHub repository was tested October 25, 2026: a new `.venv` installed `requirements.txt`, all four page routes returned HTTP 200, and a dummy parent-folder `.env` was discovered in about 26 seconds. The live API call was tested in the working project, not repeated in the clean clone. Current constituent-level data for a stronger portfolio screen and a real-user impact trial are still needed to support stronger claims.
