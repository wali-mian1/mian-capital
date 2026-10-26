# Final project brief

Source: https://zlisto.github.io/mgt_409_fa26/project_requirements.html (read October 25, 2026)

## Deadline and submission

- **Due:** Monday, October 26, 2026, 6:00 PM Eastern, on Canvas.
- **Solo project.** The instructor's October 25 Canvas announcement supersedes the original URL-plus-files instruction. Upload **only** `report.html` and `slides.html` as files, with the public GitHub repository URL visible inside **both** HTML files. A video of the student testing the app is optional. Upload no other files to Canvas; the instructor says extras will be penalized.
- The report and slides must each be one HTML file with screenshots embedded so they can be opened directly. The slides must use reveal.js and contain no more than 10 slides.

## App and repository requirements

- Build a useful AI agent app for real people, with agents using real tools and data to produce useful results end to end.
- Include all source code, a step-by-step `README.md`, and `.env.example` with key names but no secrets.
- Make the GitHub repo public or add `zlisto` as a collaborator to a private repo.
- Teaching staff must be able to use a deployed app or start the project from a fresh clone within 10 minutes by following the README.
- For local setup, the app must find `.env` in the repository root or one folder above it. A small test dataset must be included if the full dataset is large.
- The course page says the course `PORTKEY_API_KEY` may use `gpt-6-luna` only. The user explicitly directed the chatbot to use `gpt-6-luna` on October 25, 2026, so the model choice now matches the assignment rule.

## Report: 10–15 printed letter pages, in this order

1. Title, student name, GitHub URL, live app URL if any, one-sentence description.
2. Motivation: user, current workflow, and cost or frustration.
3. What is new: named existing products and an honest comparison.
4. Agents: roles, tools, organization/diagram, models and reasons, one real run traced with screenshots.
5. Tokenomics: measured input, cached input, and output tokens; cost per run, per user/month, 100 users, and 10,000 users; cost savings and any quality tradeoff.
6. Safety: relevant attacks, wrong actions or fabricated facts, budget controls, and evidence of at least one defense working.
7. Impact: sourced time, cost, quality, or reach metrics; ideally a real user trial.
8. Limits and next steps.

## Slides: 10 maximum

Suggested story: title; problem; novelty; agent diagram; demo; cost; safety; impact; next steps. Use screenshots, diagrams, large text, and a consistent visual style.

## Grading and evidence priorities

| Component | Points | Evidence to collect |
| --- | ---: | --- |
| Idea: novelty and real-world value | 21 | A specific user/problem, named alternatives, credible difference |
| App: works | 15 | Real end-to-end run with real tools/data |
| App: teaching staff can run it | 5 | Fresh-clone setup with parent-folder `.env`, under 10 minutes |
| App: look and feel | 10 | Clear, usable screens |
| Report: motivation and novelty | 8 | Named existing products |
| Report: agent design | 10 | Traced real run with screenshots and agent diagram |
| Report: tokenomics | 8 | Actual usage logs or app screenshots, with costs and scale math |
| Report: safety | 8 | Test or screenshot of a defense stopping a real failure attempt |
| Report: impact | 5 | Real user quote or measured before/after time, with source |
| Report: design | 2 | Readable visual presentation |
| Slides: content and design | 8 | Concise story, screenshots, diagram, key numbers |

The page says unsupported report claims receive at most half the points for the corresponding evidence-based row. Generic ideas (PDF chat, trip planning, summarizers, generic study aids, and work copied from class or homework) are capped at Tier 1 for the idea unless they have a substantive new twist.

## Semester work available here

- HW4: Campus Customs React storefront, FastAPI shopping assistant, structured product cards, read-only catalogue and inventory tools, saved chat history, catalogue caching, bounded calls, audit logging, and prompt-injection rules.
- HW5: Campus Customs operations desk with Boss, Inventory, Accounting, Facilities, and Customer Service agents; MCP-backed database tools; human approval gates for payments/purchases; audit trail and dashboard.
- Earlier homework and lecture folders in this workspace are empty, so their implementations are not yet available for direct reuse.

## Chosen project

The student has an existing front-end website offering Islamic ethical and values-based investment advisory services to community members whose investments must reflect religious restrictions. The final-project addition is a working research and portfolio-analysis service, connected to that website when its source becomes available. Campus Customs is not this project.

Core features requested:

1. A PydanticAI research chatbot that can discuss a named stock, ETF, or mutual fund and explain whether it appears to satisfy a specified Shariah screen, with cited evidence and clear uncertainty.
2. A portfolio tracker that accepts a user's holdings and reports an understandable, evidence-backed alignment assessment for Shariah restrictions and the user's own values-based exclusions.

Chatbot implementation started October 25, 2026. `app.py`, `agent.py`, `price_tools.py`, and `funds.py` now provide a two-tool `gpt-6-luna` chatbot for ten Shariah-oriented or Amana funds plus SPY and QQQ as explicitly unscreened market comparisons. The tools are yfinance `get_stock_price(ticker,start,stop)` and OpenAI native web search. The UI shows each tool's real input/output; name resolution sends `AMAGX` for “Amana Growth Fund.” The landing page has custom financial artwork, three service cards, and scroll reveals. The About page names Wali Mian and gives his Yale SOM, UT Austin, and actuarial background as supplied by the student. It offers account setup guidance only; it omits the unverified market-beating claim and does not offer execution of client trades. The Paper Lab provides dated historical illustrations and user-assumed future compounding, with source and method notes. The Portfolio page now weighs entered position values by issuer-described Shariah strategies with a checked source, leaves unreviewed positions unknown, and flags optional personal exclusions for constituent-level review. It does not certify compliance. See `README.md` and `output/CHATBOT_EVIDENCE.md`. The standalone `report.html` and `slides.html` were checked as 11 printed pages and ten reveal.js slides. A clean-copy dependency install and route check passed. The public GitHub repository was created and fresh-cloned successfully. A real-user trial and final review of submission claims are still required.

The backend can be built in `Final Project/` with an API and demo UI before the existing frontend is supplied. Obtain the frontend source via a local folder/ZIP or GitHub repo, inspect it, then integrate the API. Preserve the existing site's source and visual identity.

## Product decisions to confirm

- Which Shariah-screening authority or methodology should the app follow? Sector exclusions alone do not establish compliance; financial-ratio criteria and differing standards matter. The product should show the rule used and avoid presenting one method as universal.
- Which sources will provide current stock fundamentals and fund holdings? A fund cannot be assessed confidently without coverage of its underlying holdings. Missing or stale data should be labeled unknown, never silently counted as compliant.
- Is the app framed as educational research, advisor-assisted analysis, or personalized advice? Confirm the student's credentials and intended review workflow before writing financial recommendations or marketing claims.
- What portfolio inputs should be accepted first (manual tickers and weights, CSV upload, brokerage connection)? Manual entry is the fastest reliable first version; a brokerage connection would require additional credentials and privacy work.

## Evidence and product additions that support Tier 3

- Use a real user from the target community to try a specific task; record their baseline process and time, their app task time, and one candid quote with permission.
- Show sources, dates, rule-level explanations, and data coverage for each security; include a visible "needs review" outcome for conflicting or incomplete evidence.
- Keep Shariah screening distinct from optional user values exclusions, so an alignment score has a clear meaning.
- Record real agent/tool traces, input/cached/output token usage, cost, and a redacted audit trail for the report.
- Add a tested safety case: prompt injection in external text, an unsupported fund, or a request for a definitive buy recommendation should trigger a visible defense.
- Compare honestly against named existing products and explain the distinctive value of the user's service plus transparent, personalized portfolio review.

## October 25 interface refinement

The user requested a better browser experience. Price-tool chat replies now render responsive line charts, four quick-question chips can submit prompts, and the Paper Lab chart occupies a full-width panel. The portfolio view adds alcohol and high-debt review flags, fund-mandate geography summaries and filters, and sorting. These flags do not calculate constituent-level revenue or financial ratios; the current evidence-coverage percentage is unchanged. Browser checks across 320–1,440px found no horizontal overflow. The refreshed screenshots and details are in `output/CHATBOT_EVIDENCE.md`.

The home page was revised to speak directly to new Muslim investors, with a smaller graphic, a 6% assumed compounding example, a custom Mian Capital monogram, and concise account education backed by Investor.gov and IRS links. SPY and QQQ are comparison ETFs only; AMDWX and AMAPX were added as Amana funds needing issuer-source review. The app never counts the two benchmarks as screened in portfolio evidence.

The visitor chat is branded **Mian.io**. Its three public benefits are fund-name resolution, dated price charts with sources, and clear screening-evidence limits. Follow-up context lasts for the current browser session; the product does not claim persistent learning. The About page has Wali Mian's Yale SOM, UT Austin, and actuarial background directly under the opening headline, without the former personal-investing sentence or qualification pills. The dark-green navigation places About just before Mian.io. The latest Canvas copies still contain only `report.html` and `slides.html`.

## October 26 final interface and submission check

Learn and Mian.io now have their own routes (`/learn`, `/mianio`); Home retains a basics CTA and a fund-research teaser. Portfolio Screening uses paired ticker and USD value fields and six personal exclusion flags, adding gambling and renaming weapons to ordnance. About states Wali Mian is an MBA student at Yale School of Management, explains his goal of helping community members begin investing, and offers `wali.mian@yale.edu` as a contact link. The standalone report and slides were rebuilt and browser-checked after these edits. Local Chromium checks covered all five requested routes at desktop and mobile widths, with no horizontal overflow. The official requirements page was re-read October 26; the separate October 25 instructor Canvas announcement recorded above still controls the upload format. Tier 2 evidence is substantial; Tier 3 remains unproven because no target-community user has tried the app and no before/after task evidence or permissioned quote exists.
