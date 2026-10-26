# Current chatbot evidence log

Observed October 25, 2026. The current chatbot uses PydanticAI with course-approved `gpt-6-luna` through Portkey, yfinance for prices, and OpenAI's native `web_search` for news. No real client portfolio or API key is stored here.

| Question | Observed tools | Input tokens | Cached input | Output tokens | Result |
| --- | --- | ---: | ---: | ---: | --- |
| “What's Amana Growth Fund's latest closing price?” | One `get_stock_price` call with `ticker=AMAGX`, `start=2026-10-11`, `stop=2026-10-26` | 10,244 | 9,722 | 117 | Returned AMAGX close of $105.66 on October 23, 2026, with Yahoo source and exclusive stop date. |
| “What recent news is there about HLAL?” | OpenAI native `web_search` three times; queries and returned URLs captured | 14,532 | 4,862 | 516 | Returned a dated MarketBeat item with a clickable source; independent verification is still needed before quoting third-party news in the final report. |
| Request to reveal `PORTKEY_API_KEY` from `.env` | `safety_guard` blocked before model call | 0 | 0 | 0 | Refused without exposing a key. |

The original browser checks confirmed Enter-to-send and raw expandable input/output panels for both tools. After user feedback on October 25, the visitor chat replaced those panels with a collapsed, plain-language source summary; raw call data remains in the internal trace and this evidence log. The new site has three service cards, custom SVG artwork, and scroll reveals; all nine reveal elements appeared when scrolled. A 390px mobile viewport had no horizontal overflow. Screenshots: `mian-capital-landing.png`, `mian-capital-mobile.png`, `mian-capital-price-tool.png`, `mian-capital-web-search-tool.png`, and `mian-capital-safety.png`.

These runs demonstrate the tools, but they do not establish representative monthly cost. Native web search is a hosted tool with a separately priced call fee; the final report uses these measured runs and published prices for an explicitly assumed usage scenario.

## About and Paper Lab browser checks

Observed October 25, 2026 in a local headless Chromium browser at `127.0.0.1:8050`:

- `/about` displayed **Wali Mian · Founder**, the updated bio, and a loaded SVG figurine. The three account setup steps and the education-only boundary appeared after scrolling. Screenshot: `mian-capital-about.png`.
- `/paper-lab` produced an HLAL historical illustration for $10,000 entered on October 25, 2021. Yahoo's latest available close was October 23, 2026. The refreshed illustrative adjusted-close value was $18,680.87, an 86.81% change, with a −23.18% maximum historical drawdown. This is one observed run, not a projected return.
- A second scenario compounded a **user-assumed** 6% annual return for ten years, from $10,000 to $17,908.48. The app labeled it as an assumption, not a forecast. Both scenarios appeared in session history; the chart rendered. Screenshot: `mian-capital-paper-lab.png`.
- At 390px width, the Paper Lab had no horizontal overflow. All six scroll reveal elements appeared when scrolled. Screenshot: `mian-capital-paper-lab-mobile.png`.

## Portfolio evidence view

Observed October 25, 2026 in a local browser. The sample `HLAL,5000`, `SPUS,3000`, `AMAGX,2000` showed 80.00% in issuer-described screened strategies whose project source was checked, and 20.00% requiring source review. Three holding cards displayed weights, explanation, and issuer links. Selecting tobacco as an extra exclusion produced a **needs holdings-level review** label rather than silently passing it. Desktop and 390px mobile layouts had no horizontal overflow. Screenshots: `mian-capital-portfolio.png` and `mian-capital-portfolio-mobile.png`.

The percentage describes evidence coverage of fund-level screening claims, not a verified compliance score. Underlying current holdings, financial ratios, and personal exclusions have not been independently screened.

## Cost and quality check

On October 25, 2026, an HLAL price request for October 27, 2025 through October 26, 2026 returned 250 observations but passed only the first and last 12 daily closes to the model. The displayed `prices` list was 1,057 JSON bytes versus 11,033 bytes for all 250 rows, a roughly 90% smaller tool payload. The tradeoff is concrete: the April 28, 2026 close was absent from the broad output. A narrower April 28–29 tool call returned the omitted $65.76 close. This shows both the reduced context and the extra call needed to answer a middle-date question.

The temporary clean-copy setup created a new `.venv`, installed `requirements.txt`, returned HTTP 200 for `/`, `/about`, `/paper-lab`, and `/portfolio`, and found a dummy key in a parent-folder `.env`. The real Portkey key was not copied into the test folder.

After publishing `https://github.com/wali-mian1/mian-capital`, a fresh unauthenticated clone installed dependencies and returned HTTP 200 for the same four routes in about 26 seconds. A dummy parent-folder `.env` was discovered. A separate developer-run browser task asked for Amana Growth Fund's latest close; the visible `get_stock_price` trace and a correct dated AMAGX answer appeared 2.31 seconds after Enter. This is one local timing, not a real-user trial or a latency guarantee.

## Browser and filter refinement

Observed October 25, 2026 after the chart and filter update:

- A clickable **AMANX price + chart** prompt submitted one research turn. It returned the October 23, 2026 close of $79.65, a responsive dated price chart, and one expandable `get_stock_price` trace. Typed Enter-to-send still worked; a key-disclosure request was blocked before any model call. Screenshot: `mian-capital-chat-chart.png`.
- The Paper Lab now places its chart in a separate full-width panel. The historical chart measured 1,120 CSS pixels wide at a 1,440px viewport; the future chart measured 336px at a 390px viewport. Screenshots: refreshed `mian-capital-paper-lab.png` and `mian-capital-paper-lab-mobile.png`.
- The portfolio page displayed separate alcohol and high-debt **Needs review** explanations. Selecting the US-focused filter showed two of three sample holdings while leaving whole-portfolio percentages unchanged. The ticker sort worked. Screenshots: refreshed `mian-capital-portfolio.png` and `mian-capital-portfolio-mobile.png`.
- All four pages had zero horizontal overflow at 320px, 390px, 768px, 1,024px, and 1,440px. No browser page errors were observed in the live feature check.

Alcohol and high debt are review flags because no dated constituent revenue or financial-ratio data was added. The geographic labels describe a fund's stated investment focus, not audited exposure to each underlying country.

## Chat presentation correction

After the student flagged the raw JSON as confusing, the visitor chat was changed to keep each answer and chart prominent and put a plain-language date/source summary behind a collapsed “How this answer was checked” control. Raw JSON and token counters no longer appear in the visitor chat; the report retains the earlier diagnostic screenshots and measured usage as evidence. A browser check replaying the earlier observed AMAGX tool result confirmed the summary, source link, and suppression of a recovered date error. A bounded one-day stop-date correction was checked separately. A fresh live AMAGX lookup during this refinement did not yield price data from Yahoo Finance, so it was not used as new price evidence; the earlier successful AMAGX and AMANX runs remain the recorded live examples.

## Home and research-universe revision

The home page now has an explicit Home link, a compact hero, a custom monogram, a short compounding illustration, and four financial account cards linked to Investor.gov and IRS information. Browser checks found no horizontal overflow at 320, 390, 768, 1024, or 1440 pixels. At 1440 pixels, the hero was 483 pixels high and its illustration 320 pixels wide; at 390 pixels, the hero was 680 pixels high and its illustration 190 pixels wide. The Home, About, and Learn links navigated in Chromium. Updated screenshots are `mian-capital-landing.png`, `mian-capital-mobile.png`, `mian-capital-about.png`, and `mian-capital-learn.png`.

Nasdaq's public mutual-fund quote endpoint identified AMDWX as Amana Developing World Fund and AMAPX as Amana Participation Fund Investor Shares, both USD. These were added as research candidates with issuer-source review still pending. SPY and QQQ were added as broad-market comparison ETFs; the app explicitly says QQQ tracks the Nasdaq-100, and the portfolio calculator counts neither benchmark as Shariah-screened. A direct portfolio check with equal SPY and HLAL values returned 50% issuer-described screened strategy coverage and labeled SPY as a market comparison without an established Shariah screen. The $100-per-month, 20-year illustration was checked arithmetically at $46,204.09 using a 6% nominal annual rate compounded monthly and is displayed rounded to $46,200.

## Mian.io branding and About revision

After feedback from the student, the navigation uses **Mian.io** for the free research chat and puts **About** immediately before it. The header uses a deep-green background, larger monogram and wordmark, and hover and press states. The About page puts Wali Mian's Yale SOM, UT Austin, and four-year actuarial background directly under its first-step headline. The prior personal-investing sentence and qualification-pill row are absent. The home copy describes inflation as a possible loss of purchasing power when it outpaces checking interest. The chat greeting no longer begins with a religious salutation, including for old browser sessions whose stored welcome text is rendered with the current version. Mian.io's intro describes three concrete functions and says follow-up context is limited to the current browser session; no persistent learning claim is made.

Chromium checks found the navigation order Home, Learn, Paper Lab, Portfolio, About, Mian.io and zero horizontal overflow at 320, 390, 768, and 1440 pixels. The About page had no qualification pills or old investing sentence. Refreshed screenshots: `mian-capital-landing.png`, `mian-capital-mobile.png`, `mian-capital-about.png`, `mian-capital-about-mobile.png`, and `mian-capital-mianio.png`.

The slide deck's AMANX chart image is `mian-capital-observed-amanx-chart.png`, a direct crop of the chart area in the earlier real browser screenshot `mian-capital-chat-chart.png`. This keeps the observed chart and its dates visible in the deck without displaying the old greeting or diagnostic panel. The report still retains the original trace screenshots for grading evidence.

## October 26 route and portfolio refinement

Home now links to separate `/learn` and `/mianio` pages; it retains the compact fund-research invitation. About includes Wali Mian's Yale MBA status, a revised founder bio, and a mailto contact link. Portfolio Screening now accepts ticker and USD value in paired fields, with up to 20 rows. Its six optional review flags are alcohol, gambling, high debt, tobacco, ordnance, and fossil fuels; none changes the evidence-coverage percentage or asserts current constituent compliance.

A local Chromium check on October 26 confirmed exactly one visible page on `/`, `/learn`, `/mianio`, `/about`, and `/portfolio`; the Learn page displayed four account cards; Mian.io displayed the chat composer only on its route; About displayed the Yale MBA bio and email link. The portfolio form added a fifth row, accepted its three sample holdings, and returned the expected 80%/20% evidence split. No horizontal overflow was found on those routes at 1440px or 390px. Screenshots refreshed: `mian-capital-landing.png`, `mian-capital-learn.png`, `mian-capital-mianio.png`, `mian-capital-about.png`, and `mian-capital-portfolio.png`. The two standalone Canvas HTML files were rebuilt from these images and passed the 11-page, ten-slide, embedded-image, GitHub-link, and slide-fit checks.

## October 26 Stories page

The `/stories` route contains two illustrative, internally consistent walkthroughs and a feedback invitation, explicitly distinguished from customer testimonials. The portfolio scenario uses the existing $5,000 HLAL, $3,000 SPUS, $2,000 AMAGX sample (80% issuer-described strategy evidence, 20% source review). The research scenario describes an on-demand SPUS news quick question and optional dated price follow-up, without claiming a daily automated briefing. Chromium checks confirmed the Stories tab immediately precedes Mian.io, its links lead to Portfolio Screening and Mian.io, its mailto link opens the founder address, and no horizontal overflow at 1440px or 390px. Screenshot: `mian-capital-stories.png`. No real-user quote or outcome was collected.
