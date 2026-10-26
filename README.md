# Mian Capital research and paper investing lab

Public repository: https://github.com/wali-mian1/mian-capital

## Canvas submission (instructor update, October 25)

Upload exactly **two files** from the local `Canvas Upload/` folder: `report.html` and `slides.html`. The public GitHub repository URL appears in both files, so the teaching staff can clone the application. A video of you testing the app is optional; no video is included. Do not upload the repository ZIP, screenshots, README, Python source, or any other file to Canvas. Run `.venv/bin/python build_submission.py` after editing either template to refresh the two self-contained HTML files and the upload copies.

Mian Capital is an early research interface for ten Shariah-oriented or Amana funds (HLAL, SPUS, AMANX, AMAGX, AMDWX, AMAPX, SPRE, SPSK, UMMA, SPWO) and two broad-market comparison ETFs (SPY and QQQ). The two comparison ETFs are not labeled Shariah-compliant. A PydanticAI agent uses exactly two tools: `get_stock_price(ticker, start, stop)` through yfinance and OpenAI's native `web_search` through the Responses API. The Dash chat keeps tool input and output in its internal trace and shows visitors a short, expandable summary of dates and sources.

**Mian.io** is the site's free, in-house research chat. It resolves fund names, draws dated price charts, and brings public source links into one conversation. It uses recent questions from the current browser session to handle follow-ups; it does not train on visitors or build a persistent investor profile.

The chatbot provides sourced research, not independent Shariah certification or personalized investment advice. The home page speaks directly to Muslim investors who want a practical start, includes a compact compound-growth illustration, and links to a separate Learn page that teaches brokerage accounts, 401(k)s, Traditional IRAs, Roth IRAs, stocks, ETFs, and mutual funds with government source links. Mian.io also has its own page, linked from the home research teaser. Its custom SVG graphics, new monogram, and scroll reveals include reduced-motion support. The About page places founder Wali Mian’s actuarial and education background directly under its main heading and explains account setup guidance. A Testimonials page shares one anonymous tester experience as a founder-reported paraphrase shared with permission and retains two clearly labeled sample workflows. No exact quote, time saving, investment result, or trade outcome is claimed. The Paper Lab lets visitors test paper-money scenarios with historical prices or an annual return assumption. The Portfolio page reports the share of entered market value in funds with an issuer-described screening strategy whose source was checked for this project. It keeps unreviewed securities and extra personal exclusions separate. The self-contained report and slides are included in this repository.

## What works now

- Enter a supported ticker or name. The chat resolves **Amana Growth Fund** to **AMAGX**, **Amana Developing World Fund** to **AMDWX**, and **Amana Participation Fund Investor Shares** to **AMAPX** before calling yfinance. SPY is an S&P 500 comparison ETF; QQQ tracks the Nasdaq-100, not the Nasdaq Composite. A bare “Nasdaq” question is ambiguous and should be clarified.
- Ask for dated closing prices or a date range of up to one year. The price tool returns daily closes, the latest available close, data dates, and source. `stop` is exclusive, following yfinance. When more than 24 dates are returned, it shows the first and last 12 and labels the sample.
- Ask for recent fund news or public screening information. OpenAI native web search returns live source URLs; the answer should include clickable citations and publication dates.
- Open “How this answer was checked” under a reply for plain-language price dates and source links. Raw JSON and token counts are kept out of the visitor chat; measured usage remains in the local audit and report evidence.
- Price-tool replies automatically include a dated, responsive line chart. A sampled long date range shows a gap between samples rather than inventing a continuous line. Five quick-question buttons can submit common research prompts, while typed prompts still send with Enter.
- Requests for keys or hidden instructions are blocked before a model call. Model requests, local tool calls, output tokens, date range, and ticker universe are bounded. The local audit file contains tool names and usage, not raw chat messages or keys.
- Visit `/about` for Wali Mian's Yale MBA bio, account setup education, and contact email. Visit `/learn` for account basics, `/testimonials` for one permissioned anonymous tester account and clearly labeled sample workflows, and `/mianio` for the research chat. The site does not collect credentials, control accounts, or place trades.
- Visit `/paper-lab` to enter a USD-listed ticker and a paper-money amount. **Look back** uses Yahoo adjusted closes as a historical total-return proxy. **Look ahead** pre-fills the fund's historical average annual return (annualized from Yahoo adjusted closes over up to ten years; HLAL showed 16.9% over 7.3 years on October 26, 2026), which the user can change; it is not a forecast. Scenarios are saved in the browser session, with a full-width responsive chart and source link.
- Visit `/portfolio` to screen up to 20 funds or stocks with their USD values. The app fetches each fund's top ten holdings from Yahoo Finance, then a second `gpt-6-luna` agent (`holdings_screen.py`) marks every company clear, flagged, or unclear for alcohol, gambling, tobacco, weapons, and fossil fuels. Debt above 30% of market value is computed in Python. Results show each company, its share of the fund, and the user's dollars in it. The sample `HLAL 5000`, `SPUS 3000`, `AMAGX 2000` screens 15 companies (about 59% of the value) and flags ExxonMobil in SPUS for fossil fuels. Classifications are cached in `.cache/` (git-ignored), so repeat screens are instant and make no model call. AMAPX and SPSK hold sukuk, not stocks, so they have nothing to screen. This is research, not a religious ruling.

## Run locally

Python 3.11 or newer is required. The `.venv` must be created inside this project before installing dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Open http://127.0.0.1:8050/ . On Windows, use `.venv\Scripts\python` instead of `.venv/bin/python`.

The app reads `OPENAI_API_KEY` from the process environment, then `.env` in this repository, then `.env` one folder above it. The teaching staff can place `.env` next to the cloned repo. The key name is listed in `.env.example`; never commit a real value. The chatbot calls `gpt-6-luna` directly through OpenAI's Responses API. (Earlier development runs in the evidence log were routed through Portkey; that key's usage allowance ran out on October 26, 2026, so the app no longer uses it.)

Both yfinance and native web search require internet access. Yahoo Finance may throttle requests, and market prices may be delayed. The app returns an error rather than inventing a quote when no price is available.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Dash chat UI, Enter-to-send, conversation state, tool display |
| `agent.py` | PydanticAI, OpenAI Responses model (`gpt-6-luna`), native web search, tool tracing, guardrails |
| `price_tools.py` | yfinance `get_stock_price` implementation |
| `funds.py` | Supported tickers, name aliases, issuer references |
| `paper_trader.py` | Bounded historical and hypothetical paper-money calculations using Yahoo prices |
| `charts.py` | Responsive paper and chat price charts, including safe gaps for sampled price data |
| `holdings_screen.py` | Fund look-through, debt ratio, and the holdings screening agent |
| `portfolio_alignment.py` | Deterministic portfolio evidence weights, input validation, and unknown handling |
| `assets/style.css` | Chat page styles |
| `assets/reveal.js`, `assets/*.svg` | Accessible scroll reveals, site graphics, and founder figurine |
| `portfolio.json`, `market_data.py` | Illustrative portfolio and earlier metric code, reserved for the planned tracker |

## Interpretation limits

Public issuer or screening websites may describe a fund as Shariah-oriented. The chatbot does not independently inspect each current holding or issue a religious ruling. News search can surface third-party pages of varying quality, so check the cited primary source before relying on a claim. Chatbot closing-price change excludes distributions, fees, and taxes. The Paper Lab uses Yahoo adjusted closes, which can reflect distributions and splits, but it still omits fees, taxes, inflation, and cash flows. A 0% cash line is an illustrative assumption, not a claim about actual checking accounts. Past results do not forecast future returns. If a user asks the chatbot for an unsupported stock, its restricted universe does not support a price or compliance conclusion.

The repo includes `report.html` (11 printed letter pages) and `slides.html` (ten reveal.js slides), each with embedded screenshots. To rebuild them after changing screenshots, run `.venv/bin/python build_submission.py`; the reveal.js assets and license are in `vendor/`.

A fresh clone of the published commit was tested October 26, 2026: a new `.venv` installed `requirements.txt`, all six then-current routes returned HTTP 200; the new Testimonials route was browser-checked at desktop and mobile widths, and a dummy parent-folder `.env` was discovered. Clone, install, and route check took about 25 seconds of command runtime. The live API call was tested in the working project, not repeated in the clean clone. Current constituent-level data for a stronger portfolio screen and a timed user comparison are still needed to support stronger impact claims.
