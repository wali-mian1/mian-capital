"""Mian Capital Dash chat shell. Run: python app.py, then open http://127.0.0.1:8050."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from dash import ALL, Dash, Input, Output, State, ctx, dcc, html, no_update, clientside_callback
import plotly.graph_objects as go

from agent import run_agent
from charts import paper_figure, price_figure
from paper_trader import PaperTradeError, average_annual_return, simulate_future, simulate_historical
from holdings_screen import screen_portfolio
from portfolio_alignment import PortfolioInputError, analyze_portfolio

HERE = Path(__file__).resolve().parent
PORTFOLIO_PATH = HERE / "portfolio.json"
app = Dash(__name__, title="Mian Capital | Mian.io")
server = app.server

WELCOME = (
    "Welcome to Mian.io. Tell me which fund you're curious about, or ask for a dated price, recent news, or a public screening source. "
    "I can also compare SPY and QQQ as broad-market examples; they are **not** Shariah-screened recommendations. "
    "I use earlier questions from this browser session to understand follow-ups. Open ‘How this answer was checked’ for dates and sources."
)

QUICK_QUESTIONS = (
    ("AMANX price + chart", "What was AMANX's latest close, and how did its price change over the last month? Show a chart."),
    ("AMAGX price + chart", "What was AMAGX's latest close, and how did its price change over the last month? Show a chart."),
    ("HLAL last month", "How did HLAL's closing price change over the last month? Show a chart."),
    ("SPUS news", "What recent news is there about SPUS? Include dated sources."),
    ("SPUS vs SPY", "Compare SPUS and SPY closing-price changes over the last month. Show charts and explain that SPY is a broad-market comparison, not a Shariah-screened fund."),
)


def feature_card(number: str, icon: str, title: str, copy: str, foot: str, href: str, delay: str) -> html.Article:
    return html.Article(
        [
            html.Div([html.Img(src=app.get_asset_url(icon), alt="", className="feature-icon"), html.Span(number, className="feature-number")], className="feature-top"),
            html.H3(title),
            html.P(copy),
            html.A([foot, html.Span(" →", **{"aria-hidden": "true"})], href=href, className="feature-foot"),
        ],
        className=f"feature-card reveal {delay}",
    )


def holding_row(index: int, ticker: str = "", value: str = "") -> html.Div:
    return html.Div([
        html.Div(html.Label(["Ticker", dcc.Input(id={"type": "holding-ticker", "index": index}, value=ticker, placeholder="e.g. HLAL", type="text", className="holding-input")]), className="holding-field"),
        html.Div(html.Label(["Current value (USD)", dcc.Input(id={"type": "holding-value", "index": index}, value=value, placeholder="e.g. 5000", type="number", min=0, className="holding-input")]), className="holding-field"),
    ], className="holding-row")

app.layout = html.Div(
    [
        dcc.Store(id="chat-history", storage_type="session", data=[{"role": "assistant", "content": WELCOME}]),
        dcc.Store(id="pending-request", data=None),
        dcc.Store(id="paper-positions", storage_type="session", data=[]),
        dcc.Location(id="site-location", refresh=False),
        dcc.Interval(id="agent-poll", interval=250, n_intervals=0, max_intervals=0, disabled=True),
        html.Div(id="scroll-signal", style={"display": "none"}),
        html.Header(html.Div([
            html.A([html.Img(src=app.get_asset_url("mian-mark.svg"), alt="", className="brand-mark"), html.Div([html.Div("MIAN CAPITAL", className="brand"), html.Div("Values, money, and a plan", className="brand-sub")])], href="/", className="brand-lockup", **{"aria-label": "Mian Capital, home"}),
            html.Nav([html.A("Home", href="/"), html.A("Learn", href="/learn"), html.A("Paper Lab", href="/paper-lab"), html.A("Portfolio Screening", href="/portfolio"), html.A("About", href="/about"), html.A("Testimonials", href="/testimonials"), html.A("Mian.io", href="/mianio", className="nav-cta")], className="top-nav", **{"aria-label": "Main navigation"}),
        ], className="topbar-inner"), className="topbar"),
        html.Main([
            html.Section([
                html.Div([
                    html.Div([html.Span(className="eyebrow-line"), "FOR PEOPLE READY TO BEGIN"], className="eyebrow"),
                    html.H1(["Cash in a checking account can lose value to ", html.Em("inflation.")], className="hero-title"),
                    html.P("A dollar today may buy less tomorrow when prices rise faster than the interest it earns. If investing feels unfamiliar, we'll help you learn the accounts and look at funds through the lens of your faith and values before you take the next step.", className="hero-copy"),
                    html.Div([html.A(["Start with the basics", html.Span("↗", **{"aria-hidden": "true"})], href="/learn", className="primary-cta"), html.A("Try Mian.io", href="/mianio", className="text-cta")], className="hero-actions"),
                ], className="hero-content reveal"),
                html.Div([
                    html.Img(src=app.get_asset_url("hero-wealth.svg"), alt="Illustration of a gold coin, rising bars, and a leaf inside an arch", className="hero-image"),
                    html.Div([html.Span("MIAN CAPITAL", className="art-index"), html.Span("A clearer first step", className="art-caption")], className="hero-art-foot"),
                ], className="hero-art reveal delay-1"),
            ], id="top", className="hero-section"),
            html.Section([
                html.Div([html.Div("WHY STARTING EARLIER MATTERS", className="eyebrow"), html.H2("Give time a chance to work for you."), html.P("You don't have to guess the perfect day to get started. Put aside $100 a month for 20 years and you contribute $24,000. At an assumed 6% annual return, compounded monthly, that would grow to about $46,200."), html.P("Illustration only. Actual investments can lose value.", className="fine-print fine-print-dark")], className="time-copy"),
                html.Div([html.Div([html.Span("YOUR CONTRIBUTIONS"), html.Strong("$24,000")], className="time-metric"), html.Div([html.Span("ILLUSTRATIVE END VALUE"), html.Strong("$46,200")], className="time-metric time-metric-highlight"), html.A("Try your own numbers in Paper Lab ↗", href="/paper-lab", className="time-link")], className="time-metrics"),
            ], className="time-section reveal"),
            html.Section([
                html.Div([html.Div("WHAT WE CAN HELP WITH", className="eyebrow"), html.H2("Start with the question you actually have."), html.P("Which account should I open? What does this fund actually own? Does it match my faith or values? Mian Capital gives you three tools to work through those questions, without pretending every answer is simple.")], className="section-heading reveal"),
                html.Div([
                    feature_card("01", "icon-values.svg", "Invest in line with your values", "Whether your faith or your own principles rule out alcohol, gambling, tobacco, weapons, fossil fuels, or heavy debt, Portfolio Screening opens each fund you own, checks its top holdings against all six, and shows your exposure in dollars.", "Screen a portfolio", "/portfolio", "delay-1"),
                    feature_card("02", "icon-research.svg", "Research a fund in plain English", "Ask Mian.io for a fund's latest close, a one-month chart, recent news, or a side-by-side comparison such as SPUS vs. SPY. Every answer is dated and links to its source.", "Ask Mian.io", "/mianio", "delay-2"),
                    feature_card("03", "icon-journey.svg", "Learn, then practice with paper money", "Learn how brokerage accounts, 401(k)s, and IRAs work. Then use Paper Lab to replay a past purchase or project a fund's growth at its historical average return before you risk a real dollar.", "Open Paper Lab", "/paper-lab", "delay-3"),
                ], className="feature-grid"),
            ], id="approach", className="approach-section"),
            html.Section([
                html.Div([html.Div("MIAN.IO · OUR PROPRIETARY AI RESEARCH ASSISTANT", className="eyebrow"), html.H2("Meet Mian.io: fund research at the speed of a conversation."), html.P("Mian.io is our proprietary research assistant. It pairs advanced AI models with live market data and real-time web search, so you can ask about a fund in your own words and get an answer in seconds: the latest close, a dated price chart, recent news, or a side-by-side comparison of two funds. Every answer shows its sources, and follow-up questions pick up where you left off."), html.Div([html.Div([html.Strong("Live prices"), html.Span("Dated closes and charts from Yahoo Finance")], className="mianio-pill"), html.Div([html.Strong("Real-time search"), html.Span("Recent news with clickable sources")], className="mianio-pill"), html.Div([html.Strong("Side by side"), html.Span("Compare two funds in one question")], className="mianio-pill")], className="mianio-pills"), html.A("Open Mian.io ↗", href="/mianio", className="primary-cta"), html.P("Free to use. Research only; not personal investment advice.", className="fine-print")], className="mianio-intro reveal"),
            ], className="research-section"),
        ], id="home-page", className="page-content"),
        html.Main([
            html.Section([
                html.Div([html.Div("MONEY BASICS", className="eyebrow"), html.H2("First, know the account. Then, choose what goes inside."), html.P("A brokerage or retirement account is a container. Stocks, ETFs, and mutual funds are investments you might put in it. Knowing the difference makes the next step much less intimidating.")], className="section-heading reveal"),
                html.Div([
                    html.Article([html.Span("01 / EVERYDAY INVESTING", className="learn-kicker"), html.H3("Brokerage account"), html.P("An account at a firm such as Fidelity, Schwab, or Vanguard where you can buy investments. A regular taxable account has no special retirement tax break."), html.A("Investor.gov account basics ↗", href="https://www.investor.gov/introduction-investing/investing-basics/investment-accounts/brokerage-accounts", target="_blank", rel="noopener noreferrer")], className="learn-card reveal delay-1"),
                    html.Article([html.Span("02 / THROUGH WORK", className="learn-kicker"), html.H3("401(k) plan"), html.P("A retirement account offered by an employer. Money can come from your paycheck, and some employers add a match. Traditional and Roth tax options may be available."), html.A("IRS 401(k) overview ↗", href="https://www.irs.gov/retirement-plans/plan-sponsor/401k-plan-overview", target="_blank", rel="noopener noreferrer")], className="learn-card reveal delay-2"),
                    html.Article([html.Span("03 / ON YOUR OWN", className="learn-kicker"), html.H3("Traditional IRA"), html.P("An individual retirement account. Contributions may be deductible depending on your situation; withdrawals are generally taxable. Annual rules and limits apply."), html.A("IRS IRA basics ↗", href="https://www.irs.gov/retirement-plans/traditional-and-roth-iras", target="_blank", rel="noopener noreferrer")], className="learn-card reveal delay-1"),
                    html.Article([html.Span("04 / ON YOUR OWN", className="learn-kicker"), html.H3("Roth IRA"), html.P("You contribute money after tax. Qualified withdrawals can be tax-free later. Income eligibility and contribution rules apply; a Roth 401(k) is a separate workplace option."), html.A("IRS Roth IRA basics ↗", href="https://www.irs.gov/retirement-plans/traditional-and-roth-iras", target="_blank", rel="noopener noreferrer")], className="learn-card reveal delay-2"),
                    html.Article([html.Span("05 / TAX BASICS", className="learn-kicker"), html.H3("Pre-tax contributions"), html.P("Money goes in before income tax is taken out, as with a traditional 401(k) or a deductible Traditional IRA. It lowers your taxable income today, and you pay income tax when you withdraw the money in retirement."), html.A("IRS Roth vs. traditional chart ↗", href="https://www.irs.gov/retirement-plans/roth-comparison-chart", target="_blank", rel="noopener noreferrer")], className="learn-card reveal delay-1"),
                    html.Article([html.Span("06 / TAX BASICS", className="learn-kicker"), html.H3("Post-tax contributions"), html.P("Money goes in after income tax has been paid, as with a Roth IRA or Roth 401(k). There is no tax break today, but qualified withdrawals, including the growth, can be tax-free later."), html.A("IRS Roth vs. traditional chart ↗", href="https://www.irs.gov/retirement-plans/roth-comparison-chart", target="_blank", rel="noopener noreferrer")], className="learn-card reveal delay-2"),
                ], className="learn-grid"),
                html.Div([html.Strong("What goes inside?"), html.Span("A stock is a share of one company. An ETF or mutual fund holds a basket of investments; ETFs trade during the day, while mutual funds usually price once daily. An account type doesn't make its holdings fit your values, so check the investments themselves."), html.A("See investment product basics ↗", href="https://www.investor.gov/introduction-investing/investing-basics/investment-products", target="_blank", rel="noopener noreferrer")], className="learn-footnote reveal"),
            ], id="learn", className="learn-section"),
        ], id="learn-page", className="page-content subpage-content", hidden=True),
        html.Main([
            html.Section([
                html.Div([
                    html.Div("MIAN.IO · FREE TO USE", className="eyebrow"),
                    html.H2("Fund research that feels like a conversation."),
                    html.P("Mian.io is our proprietary AI research assistant. It pairs advanced AI models with live market data and real-time web search. Ask in your own words, then ask a follow-up; it remembers the earlier questions in this browser session. No account or fee is needed."),
                    html.Div([
                        html.Div([html.Strong("Say the fund name"), html.Span("Ask about Amana Growth Fund and Mian.io looks up AMAGX, the ticker the price source needs.")], className="mianio-benefit"),
                        html.Div([html.Strong("See a dated chart"), html.Span("Get the latest available close, a price history chart, and the source behind the numbers.")], className="mianio-benefit"),
                        html.Div([html.Strong("Know what needs checking"), html.Span("Read public screening sources and see when a fund's current holdings still need review.")], className="mianio-benefit"),
                    ], className="mianio-benefits"),
                    html.P("Built to make the first research step quicker and easier to verify. It does not certify Shariah compliance or make trades for you.", className="fine-print"),
                ], className="mianio-intro reveal"),
                html.Div([
                html.Section([
                    html.Div([html.Div("MIAN.IO · RESEARCH CHAT", className="card-kicker"), html.Div("What would you like to know?", className="card-title")], className="chat-head"),
                    html.Div(id="chat-window", className="chat-window", role="log", **{"aria-live": "polite"}),
                    html.Div([html.Span("QUICK QUESTIONS", className="quick-label"), html.Div([html.Button(label, id={"type": "quick-question", "index": index}, n_clicks=0, className="quick-chip") for index, (label, _) in enumerate(QUICK_QUESTIONS)], className="quick-chips")], className="quick-row"),
                    html.Div([
                        dcc.Input(id="composer", type="text", debounce=False, placeholder="Ask Mian.io about a fund, a price, or recent news...", className="composer", autoComplete="off"),
                        html.Button("Send", id="send-button", n_clicks=0, className="send-button"),
                    ], className="composer-row"),
                    html.Div("Press Enter to send · Research only; an advisor can help with personal decisions.", className="composer-note"),
                ], className="chat-card reveal delay-1"),
                html.Aside([
                    html.Div("START HERE", className="side-kicker"),
                    html.H2("Questions worth asking"),
                    html.Ul([
                        html.Li("What was Amana Growth Fund's latest closing price?"),
                        html.Li("What recent news is there about HLAL?"),
                        html.Li("Compare HLAL and SPUS closing prices last month."),
                    ], className="example-list"),
                    html.Div(className="rule"),
                    html.Div("SHARIAH-ORIENTED RESEARCH", className="side-kicker"),
                    html.Div([html.Span(x, className="ticker") for x in ("HLAL", "SPUS", "AMANX", "AMAGX", "AMDWX", "AMAPX", "SPRE", "SPSK", "UMMA", "SPWO")], className="ticker-list"),
                    html.Div("MARKET COMPARISONS", className="side-kicker"),
                    html.Div([html.Span(x, className="ticker ticker-benchmark") for x in ("SPY", "QQQ")], className="ticker-list"),
                    html.P("SPY follows the S&P 500; QQQ follows the Nasdaq-100. They are comparison ETFs, not Shariah-screened recommendations. Prices use Yahoo Finance; screening claims need current issuer and holdings review.", className="side-note"),
                ], className="side-card reveal delay-2"),
                ], className="content-grid"),
            ], id="research", className="research-section"),
        ], id="mianio-page", className="page-content subpage-content", hidden=True),
        html.Main([
            html.Section([
                html.Div([
                    html.Div([html.Span(className="eyebrow-line"), "MEET WALI MIAN"], className="eyebrow"),
                    html.H1(["The first step ", html.Em("can be the hardest.")], className="subpage-title"),
                    html.Div("ABOUT YOUR ADVISOR", className="eyebrow about-bio-label"),
                    html.P("I’m Wali Mian, an MBA student at Yale School of Management. I studied mathematics and actuarial science at UT Austin and spent four years as an actuary working with retirement benefits, including 401(k), defined benefit, defined contribution, and pension plans. I started Mian Capital to help people begin investing with more confidence while honoring their values, whether those come from Islam, another faith, or their own convictions.", className="subpage-lede about-bio-copy"),
                    html.A("Explore Mian.io ↗", href="/mianio", className="primary-cta"),
                ], className="about-hero-copy reveal"),
                html.Div([
                    html.Img(src=app.get_asset_url("advisor-figurine.svg"), alt="Playful illustrated advisor figurine with glasses, a calculator, and a coin", className="advisor-figurine"),
                    html.Div("WALI MIAN · FOUNDER", className="advisor-label"),
                    html.Div("Let's make the first money conversation easier.", className="advisor-card-quote"),
                ], className="advisor-card reveal delay-1"),
            ], className="about-hero"),
            html.Section([
                html.Div([
                    html.Div("STARTING IS OFTEN THE HARDEST PART", className="eyebrow"),
                    html.H2("Every paycheck comes with questions."),
                    html.P("Maybe you're a new physician whose income just jumped after years of training. Maybe you're early in your career and want to make a modest paycheck go further. Either way, figuring out a brokerage account, a retirement plan, and a first investment can feel like a lot. I can walk you through the setup and the questions worth asking before you put money to work.", className="service-lede"),
                ], className="service-heading reveal"),
                html.Div([
                    html.Article([html.Div("01", className="service-step-number"), html.H3("Choose a place to begin"), html.P("Understand the basics of opening a brokerage account at firms such as Vanguard, Fidelity, or Charles Schwab, and what to look for in an account.")], className="service-step reveal delay-1"),
                    html.Article([html.Div("02", className="service-step-number"), html.H3("Set it up securely"), html.P("Walk through the account-opening and funding process. You keep control of your credentials, personal information, and account access.")], className="service-step reveal delay-2"),
                    html.Article([html.Div("03", className="service-step-number"), html.H3("Learn the mechanics"), html.P("Understand tickers, order types, and the steps involved in placing your own first trade before making any real decision.")], className="service-step reveal delay-3"),
                ], className="service-grid"),
                html.P("Mian Capital offers education and setup guidance. This website does not place trades or take control of client accounts.", className="fine-print"),
            ], className="account-section"),
            html.Section([html.Div("WRITE TO ME", className="eyebrow"), html.H2("Have a question about getting started?"), html.P("Tell me what you're trying to understand, whether that's opening an account or researching a fund. Please don't email account numbers, passwords, or other sensitive financial information."), html.A("wali.mian@yale.edu ↗", href="mailto:wali.mian@yale.edu", className="primary-cta")], className="about-close reveal"),
        ], id="about-page", className="page-content subpage-content", hidden=True),
        html.Main([
            html.Section([
                html.Div([html.Div("HEAR FROM OUR USERS", className="eyebrow"), html.H1(["Real questions, ", html.Em("answered faster.")], className="subpage-title"), html.P("Here is how people are using Mian Capital to research funds and think through decisions, shared with their permission.", className="subpage-lede")], className="stories-hero-copy reveal"),
                html.Div([html.Span("“", className="stories-hero-number"), html.Span("in their words", className="stories-hero-line")], className="stories-hero-art reveal delay-1"),
            ], className="stories-hero"),
            html.Section([
                html.Div("FUND COMPARISON", className="eyebrow"),
                html.H2("Two funds, side by side, in about 20 seconds."),
                html.P("One of our users tapped the SPUS vs SPY question in Mian.io and had both funds' prices and charts side by side in about 20 seconds. They told us the same check on the open web would have taken closer to a minute, with two separate tabs. They then asked Mian.io for insights on the two funds and got an objective comparison of the tickers, which they found very useful."),
                html.P("Shared with permission. Timings are the user's own estimate; this is not a recommendation of either fund.", className="testimonial-source"),
            ], className="testimonial-feature reveal"),
            html.Section([
                html.Div("PAPER LAB", className="eyebrow"),
                html.H2("Revisiting a trade before making it."),
                html.P("A user compared HLAL and SPUS prices, then used Paper Lab to replay a trade they had considered about a month earlier but never placed. Seeing the scenario helped them feel more confident about the decision they were weighing, and they reached out to us for help opening a brokerage account."),
                html.P("Shared with permission. No trade or investment result is implied.", className="testimonial-source"),
            ], className="testimonial-feature reveal"),
            html.Section([
                html.Div([html.Div("TRY THE TOOLS YOURSELF", className="eyebrow"), html.H2("Two ways to give it a try."), html.P("The examples below use sample questions and holdings. They show what the app can do today, including where it needs more evidence.")], className="section-heading reveal"),
                html.Div([
                    html.Article([
                        html.Div([html.Span("01 / PORTFOLIO SCREENING", className="story-kicker"), html.Img(src=app.get_asset_url("icon-values.svg"), alt="", className="story-icon")], className="story-card-top"),
                        html.H3("See what your funds actually hold."),
                        html.P("Enter $5,000 of HLAL, $3,000 of SPUS, and $2,000 of AMAGX in Portfolio Screening. We open each fund, list its largest companies, and check each one for alcohol, gambling, tobacco, weapons, fossil fuels, and high debt."),
                        html.P("In the sample, almost everything is clear. One holding is flagged: ExxonMobil inside SPUS, for fossil fuels. You see exactly which company it is and how many of your dollars it represents."),
                        html.A("Try the sample portfolio ↗", href="/portfolio", className="story-link"),
                    ], className="story-card reveal delay-1"),
                    html.Article([
                        html.Div([html.Span("02 / MIAN.IO RESEARCH", className="story-kicker"), html.Img(src=app.get_asset_url("icon-research.svg"), alt="", className="story-icon")], className="story-card-top"),
                        html.H3("A quick market check, in your own words."),
                        html.P("Before the day gets busy, open Mian.io and tap the SPUS news question. You can ask a follow-up about its recent price and see a dated chart when price data is available. Source links let you check what the answer is based on."),
                        html.P("This is an on-demand research conversation, not an automatic daily briefing. News coverage can be incomplete, and the tool does not recommend a trade."),
                        html.A("Ask Mian.io ↗", href="/mianio", className="story-link"),
                    ], className="story-card reveal delay-2"),
                ], className="stories-grid"),
            ], className="stories-section"),
            html.Section([html.Div("TELL US WHAT YOU FOUND", className="eyebrow"), html.H2("Tried it yourself? We'd love to hear how it worked."), html.P("Use the sample portfolio or bring a fund question. Tell us what you tried, what helped, and what was confusing. If you would like your words shared here, just let us know. Please do not send account numbers, passwords, or private holdings."), html.A("Write to us ↗", href="mailto:wali.mian@yale.edu?subject=Mian%20Capital%20feedback", className="primary-cta")], className="stories-feedback reveal"),
        ], id="stories-page", className="page-content subpage-content", hidden=True),
        html.Main([
            html.Section([
                html.Div([html.Div([html.Span(className="eyebrow-line"), "PAPER LAB"], className="eyebrow"), html.H1(["What might a small start ", html.Em("have become?")], className="subpage-title"), html.P("Replay a paper-money purchase with real past prices, or project growth at a fund's historical average return to see how compounding works. Nothing here places a trade or predicts the future.", className="subpage-lede")], className="paper-hero-copy reveal"),
                html.Div([html.Div("$", className="paper-coin"), html.Div("TRY IT WITHOUT RISKING A DOLLAR", className="paper-coin-label")], className="paper-hero-art reveal delay-1"),
            ], className="paper-hero"),
            html.Section([
                html.Div([html.Div("BUILD A SCENARIO", className="eyebrow"), html.H2("Put paper money to work."), html.P("Choose a ticker and an amount. Look back uses dated Yahoo prices. Look ahead starts from the fund's historical average return, which you can change.")], className="section-heading reveal"),
                html.Div([
                    html.Div([
                        html.Div("1. Choose a view", className="form-kicker"),
                        dcc.RadioItems(id="paper-mode", options=[{"label": "Look back", "value": "historical"}, {"label": "Look ahead", "value": "future"}], value="historical", className="mode-options"),
                        html.Div([html.Label("Ticker symbol", htmlFor="paper-ticker"), dcc.Input(id="paper-ticker", type="text", value="HLAL", debounce=True, placeholder="HLAL or another USD ticker", className="paper-input"), html.Small("Paper Lab works with USD-listed stocks and funds. It does not place a trade.")], className="field"),
                        html.Div([html.Label("Paper-money amount (USD)", htmlFor="paper-amount"), dcc.Input(id="paper-amount", type="number", value=10000, min=100, max=1000000, step=100, className="paper-input")], className="field"),
                        html.Div([html.Label("Hypothetical purchase date"), dcc.DatePickerSingle(id="paper-date", date="2021-10-25", display_format="MMM D, YYYY", className="paper-date")], id="historical-controls", className="field"),
                        html.Div([html.Div([html.Label("Years from today", htmlFor="paper-years"), dcc.Input(id="paper-years", type="number", value=10, min=1, max=30, step=1, className="paper-input")], className="field"), html.Div([html.Label("Annual return (%)", htmlFor="paper-rate"), dcc.Input(id="paper-rate", type="number", value=6, min=-30, max=30, step=0.1, className="paper-input")], className="field"), html.Div(id="fund-average", className="fund-average"), html.Small("We fill in the fund's historical average. Change it to test your own assumption; past returns don't predict future ones.")], id="future-controls", className="future-fields", style={"display": "none"}),
                        html.Button("Run paper scenario", id="paper-run", n_clicks=0, className="paper-run"),
                        html.P("Historical returns can be negative. A checking-account comparison assumes 0% interest and does not include inflation.", className="paper-form-note"),
                    ], className="paper-form reveal delay-1"),
                    html.Div([html.Div("YOUR RESULTS", className="form-kicker"), html.Div("Your scenario will appear here after you run it.", id="paper-result", className="paper-result-empty")], className="paper-output reveal delay-2"),
                ], className="paper-workspace"),
                html.Div([html.Div("SCENARIO CHART", className="form-kicker"), html.P("The investment line uses the selected scenario. The cash line assumes 0% interest.", className="chart-lede"), dcc.Graph(id="paper-chart", figure=go.Figure(), config={"displayModeBar": False, "responsive": True, "scrollZoom": False}, className="paper-chart")], id="paper-chart-panel", className="paper-chart-panel", style={"display": "none"}),
            ], className="paper-work-section"),
            html.Section([html.Div("SAVED IN THIS BROWSER SESSION", className="eyebrow"), html.H2("Your paper scenarios"), html.Div(id="paper-history", className="paper-history")], className="paper-history-section reveal"),
            html.P("Paper Lab is for education. It does not connect to a brokerage, execute trades, or guarantee results. Past performance does not predict future returns.", className="paper-disclaimer"),
        ], id="paper-page", className="page-content subpage-content", hidden=True),
        html.Main([
            html.Section([
                html.Div([html.Div([html.Span(className="eyebrow-line"), "PORTFOLIO SCREENING"], className="eyebrow"), html.H1(["See what your funds ", html.Em("actually own.")], className="subpage-title"), html.P("Enter your funds or stocks. We open each fund, list the companies it holds, and check every company against six common faith- and values-based screens: alcohol, gambling, tobacco, weapons, fossil fuels, and high debt.", className="subpage-lede")], className="reveal"),
            ], className="portfolio-hero"),
            html.Section([
                html.Div([
                    html.Div([
                        html.Div("1. What do you own?", className="form-kicker"),
                        html.Div([holding_row(0, "HLAL", "5000"), holding_row(1, "SPUS", "3000"), holding_row(2, "AMAGX", "2000"), holding_row(3)], id="holding-rows", className="holding-rows"),
                        html.Button("+ Add another holding", id="add-holding", n_clicks=0, className="add-holding"),
                        html.Small("Funds or individual stocks, with today's dollar value. Leave unused rows blank."),
                        html.Button("Screen my portfolio", id="portfolio-run", n_clicks=0, className="paper-run"),
                        html.P("The first screen takes about 20 seconds while we look up each company. Nothing is sent to a brokerage.", className="paper-form-note"),
                    ], className="paper-form reveal delay-1"),
                    html.Div([
                        html.Div("2. What we check", className="form-kicker"),
                        html.Div([
                            html.Div([html.Strong("Look inside each fund"), html.Span("We pull the fund's ten largest holdings from Yahoo Finance and show how much of your money sits in each company.")], className="screen-step"),
                            html.Div([html.Strong("Screen each company's business"), html.Span("A Mian Capital AI agent reads each company's industry and business description and marks alcohol, gambling, tobacco, weapons, and fossil fuels as clear, flagged, or unclear.")], className="screen-step"),
                            html.Div([html.Strong("Measure debt"), html.Span("Total debt divided by market value. Above 30% is flagged, a common limit in Shariah screens such as AAOIFI's.")], className="screen-step"),
                            html.Div([html.Strong("Add it up"), html.Span("Flagged companies are converted to dollars of your portfolio, so you see how much is actually exposed.")], className="screen-step"),
                        ], className="screen-steps"),
                    ], className="paper-output reveal delay-2"),
                ], className="paper-workspace"),
                dcc.Loading(html.Div(id="portfolio-result"), type="dot", color="#173e32"),
            ], className="paper-work-section"),
            html.P("This screen covers each fund's ten largest holdings, not every company it owns, and uses one common debt limit. It is research, not a religious ruling. Consult a qualified scholar or financial professional before making decisions.", className="paper-disclaimer"),
        ], id="portfolio-page", className="page-content subpage-content", hidden=True),
        html.Footer(html.Div([html.Div([html.Img(src=app.get_asset_url("mian-mark.svg"), alt="", className="footer-mark"), html.Div([html.Strong("MIAN CAPITAL"), html.Span("Values, money, and a plan.")], className="footer-brand")]), html.Div("Research to support a thoughtful conversation. Fund information is not a religious ruling or personal investment advice.", className="footer-note")], className="footer-inner"), className="footer"),
    ], className="app-shell",
)


def _friendly_date(value):
    try:
        day = date.fromisoformat(str(value))
    except ValueError:
        return str(value or "")
    return f"{day.strftime('%b')} {day.day}, {day.year}"


def _research_steps(events):
    """Show useful provenance without exposing model-call JSON to visitors."""
    completed_tickers = {
        event.get("output", {}).get("ticker")
        for event in events
        if event.get("name") == "get_stock_price"
        and event.get("status") == "completed"
        and isinstance(event.get("output"), dict)
    }
    steps = []
    for event in events:
        name = event.get("name")
        status = event.get("status")
        tool_input = event.get("input") if isinstance(event.get("input"), dict) else {}
        output = event.get("output") if isinstance(event.get("output"), dict) else {}
        if name == "get_stock_price":
            ticker = output.get("ticker") or tool_input.get("ticker") or "fund"
            if status != "completed" and ticker in completed_tickers:
                continue  # A later successful retry is the relevant result.
            if status == "completed":
                start = tool_input.get("start")
                stop = output.get("requested_stop_exclusive") or tool_input.get("stop")
                try:
                    last_requested = (date.fromisoformat(str(stop)) - timedelta(days=1)).isoformat()
                    requested = f"Asked for {ticker} closes from {_friendly_date(start)} through {_friendly_date(last_requested)}."
                except ValueError:
                    requested = f"Asked for {ticker} closing prices."
                close = output.get("last_close_usd")
                result_text = f"Latest available close: ${close:,.2f} on {_friendly_date(output.get('last_date'))}." if isinstance(close, (int, float)) else "Dated price history returned."
                source_url = output.get("source_url")
                steps.append(html.Div([
                    html.Strong(f"Yahoo Finance · {ticker}"),
                    html.P(requested),
                    html.P(result_text),
                    html.A("View price history ↗", href=source_url, target="_blank", rel="noopener noreferrer") if isinstance(source_url, str) and source_url.startswith("https://") else None,
                ], className="research-step"))
            else:
                steps.append(html.Div([html.Strong(f"Price lookup · {ticker}"), html.P("This date range could not be retrieved. Please try another period.")], className="research-step"))
        elif name == "web_search":
            queries = tool_input.get("queries") or tool_input.get("search_query") or tool_input.get("query")
            if isinstance(queries, list):
                query_text = "; ".join(str(item.get("search_term") or item.get("q") or item) for item in queries[:2])
            elif isinstance(queries, dict):
                query_text = str(queries.get("search_term") or queries.get("q") or "")
            else:
                query_text = str(queries or "")
            query_text = query_text[:180]
            sources = output.get("sources") if isinstance(output.get("sources"), list) else []
            links = []
            for source in sources[:3]:
                if not isinstance(source, dict):
                    continue
                url = source.get("url")
                if isinstance(url, str) and url.startswith("https://"):
                    links.append(html.A(str(source.get("title") or source.get("domain") or "Read source")[:90] + " ↗", href=url, target="_blank", rel="noopener noreferrer"))
            steps.append(html.Div([
                html.Strong("Web research"),
                html.P(f"Searched: {query_text}" if query_text else "Checked recent public information."),
                html.Div(links, className="research-links") if links else html.P("Source links appear in the answer above."),
            ], className="research-step"))
        elif name == "safety_guard":
            steps.append(html.Div([html.Strong("Safety check"), html.P("A request for private information was blocked before any research call.")], className="research-step"))
    if not steps:
        return None
    return html.Details([html.Summary("How this answer was checked"), html.Div(steps, className="research-steps")], className="research-details")


def render_messages(history, pending):
    blocks = []
    for index, message in enumerate(history or []):
        assistant = message.get("role") == "assistant"
        content = message.get("content", "")
        if index == 0 and isinstance(content, str) and content.startswith("Assalamu alaikum."):
            content = WELCOME
        charts = []
        if assistant:
            chart_outputs = {}
            for event in message.get("tool_events", []):
                if event.get("name") != "get_stock_price" or event.get("status") != "completed" or not isinstance(event.get("output"), dict):
                    continue
                output = event["output"]
                ticker = output.get("ticker")
                if not ticker or not output.get("prices"):
                    continue
                previous = chart_outputs.get(ticker)
                if previous is None or output.get("observations", len(output["prices"])) > previous.get("observations", len(previous["prices"])):
                    chart_outputs[ticker] = output
            for output in chart_outputs.values():
                figure = price_figure(output)
                if figure is None:
                    continue
                charts.append(html.Div([
                    html.Div(f"{output.get('ticker', 'Fund')} · dated closing prices", className="chat-chart-title"),
                    dcc.Graph(figure=figure, config={"displayModeBar": False, "responsive": True, "scrollZoom": False}, className="chat-price-chart", style={"height": "260px", "width": "100%"}),
                    html.P("Sampled dates only; open the source for the full daily history." if output.get("prices_sampled") else "Daily closes from Yahoo Finance. The latest available close may be delayed.", className="chat-chart-note"),
                ], className="chat-chart-card"))
        blocks.append(html.Div([
            html.Div("Mian.io" if assistant else "You", className="message-label"),
            dcc.Markdown(str(content), className="message-body", link_target="_blank"),
            html.Div(charts, className="chat-charts") if charts else None,
            _research_steps(message.get("tool_events") or []) if assistant else None,
        ], className="message assistant chart-message" if charts else ("message assistant" if assistant else "message user")))
    if pending:
        blocks.append(html.Div([html.Div("Mian.io", className="message-label"), html.Span("Thinking", className="thinking")], className="message assistant", role="status"))
    return blocks


@app.callback(Output("chat-window", "children"), Input("chat-history", "data"), Input("pending-request", "data"))
def update_chat(history, pending):
    return render_messages(history, pending)


clientside_callback(
    """function(children) {
        window.setTimeout(function() {
            const chat = document.getElementById('chat-window');
            if (chat) chat.scrollTop = chat.scrollHeight;
        }, 0);
        return Date.now();
    }""",
    Output("scroll-signal", "children"),
    Input("chat-window", "children"),
)


@app.callback(Output("send-button", "disabled"), Output("composer", "disabled"), Output({"type": "quick-question", "index": ALL}, "disabled"), Input("pending-request", "data"))
def lock_composer(pending):
    locked = bool(pending)
    return locked, locked, [locked] * len(QUICK_QUESTIONS)


@app.callback(
    Output("chat-history", "data", allow_duplicate=True), Output("pending-request", "data"),
    Output("composer", "value"), Output("agent-poll", "disabled"),
    Output("agent-poll", "n_intervals"), Output("agent-poll", "max_intervals"),
    Input("send-button", "n_clicks"), Input("composer", "n_submit"), Input({"type": "quick-question", "index": ALL}, "n_clicks"),
    State("composer", "value"), State("chat-history", "data"), State("pending-request", "data"),
    prevent_initial_call=True,
)
def submit_message(_, __, ___, text, history, pending):
    if pending:
        return (no_update,) * 6
    triggered = ctx.triggered_id
    if isinstance(triggered, dict) and triggered.get("type") == "quick-question":
        index = triggered.get("index")
        text = QUICK_QUESTIONS[index][1] if isinstance(index, int) and 0 <= index < len(QUICK_QUESTIONS) else ""
    if not text or not text.strip():
        return (no_update,) * 6
    question = text.strip()[:1500]
    return [*(history or []), {"role": "user", "content": question}], {"text": question}, "", False, 0, 1


@app.callback(
    Output("chat-history", "data", allow_duplicate=True), Output("pending-request", "data", allow_duplicate=True),
    Output("agent-poll", "disabled", allow_duplicate=True), Input("agent-poll", "n_intervals"),
    State("pending-request", "data"), State("chat-history", "data"), prevent_initial_call=True,
)
def complete_agent_turn(n_intervals, pending, history):
    if not pending:
        return no_update, no_update, True
    # Resetting n_intervals to 0 also triggers this callback; run only on the timer tick,
    # otherwise each question would call the agent (and bill tokens) twice.
    if not n_intervals:
        return no_update, no_update, no_update
    try:
        result = run_agent(pending["text"], PORTFOLIO_PATH, (history or [])[:-1])
        reply = {"role": "assistant", "content": result["text"], "tool_events": result.get("tool_events", []), "usage": result.get("usage")}
    except Exception:
        reply = {"role": "assistant", "content": "Research is temporarily unavailable. Check the project key or data connection, then try again."}
    return [*(history or []), reply], None, True


@app.callback(
    Output("home-page", "hidden"),
    Output("about-page", "hidden"),
    Output("paper-page", "hidden"),
    Output("portfolio-page", "hidden"),
    Output("learn-page", "hidden"),
    Output("mianio-page", "hidden"),
    Output("stories-page", "hidden"),
    Input("site-location", "pathname"),
)
def show_page(pathname):
    pages = {"/": 0, "/about": 1, "/paper-lab": 2, "/portfolio": 3, "/learn": 4, "/mianio": 5, "/stories": 6, "/testimonials": 6}
    selected = pages.get(pathname or "/", 0)
    return tuple(index != selected for index in range(7))


@app.callback(
    Output("historical-controls", "style"),
    Output("future-controls", "style"),
    Input("paper-mode", "value"),
)
def show_paper_fields(mode):
    return ({"display": "none"}, {}) if mode == "future" else ({}, {"display": "none"})


@app.callback(Output("fund-average", "children"), Output("paper-rate", "value"), Input("paper-ticker", "value"), Input("paper-mode", "value"))
def show_fund_average(ticker, mode):
    if mode != "future" or not str(ticker or "").strip():
        return no_update, no_update
    try:
        result = average_annual_return(ticker)
    except PaperTradeError as exc:
        return html.Span(str(exc), className="fund-average-missing"), no_update
    rate = max(-30.0, min(30.0, result["average_annual_return_pct"]))
    return html.Div([
        html.Strong(f"{result['ticker']} has averaged {result['average_annual_return_pct']:.1f}% a year"),
        html.Span(f" over the last {result['years']:g} years ({result['start'][:4]}–{result['end'][:4]}, with distributions reinvested). "),
        html.A("Source ↗", href=result["source_url"], target="_blank", rel="noopener noreferrer"),
    ]), rate


def _money(amount: float) -> str:
    return f"{'−' if amount < 0 else ''}${abs(amount):,.2f}"


@app.callback(
    Output("paper-result", "children"),
    Output("paper-chart", "figure"),
    Output("paper-chart-panel", "style"),
    Output("paper-positions", "data"),
    Input("paper-run", "n_clicks"),
    State("paper-mode", "value"),
    State("paper-ticker", "value"),
    State("paper-amount", "value"),
    State("paper-date", "date"),
    State("paper-years", "value"),
    State("paper-rate", "value"),
    State("paper-positions", "data"),
    prevent_initial_call=True,
)
def run_paper_scenario(_, mode, ticker, amount, purchase_date, years, rate, positions):
    try:
        result = simulate_future(ticker, amount, years, rate) if mode == "future" else simulate_historical(ticker, amount, purchase_date)
    except PaperTradeError as exc:
        return html.Div(str(exc), className="paper-error"), go.Figure(), {"display": "none"}, no_update
    historical = result["mode"] == "historical"
    context = f"Bought on {result['actual_purchase_date']} · latest close {result['last_price_date']}" if historical else f"Starting from the close on {result['last_price_date']} · {result['horizon_years']} years at your assumed {result['assumed_annual_return_pct']}% rate"
    metrics = [
        ("Starting paper money", _money(result["initial_amount"])),
        ("Illustrative ending value", _money(result["ending_value"])),
        ("Gain or loss", _money(result["gain_loss"])),
        ("Total change", f"{result['total_return_pct']:+,.2f}%"),
    ]
    if historical:
        metrics.append(("Worst historical drawdown", f"{result['max_drawdown_pct']:,.2f}%"))
    summary = html.Div([
        html.H3(f"{result['ticker']} · {'historical what-if' if historical else 'future scenario'}"),
        html.P(context, className="result-context"),
        html.Div([html.Div([html.Span(label), html.Strong(value)], className="result-metric") for label, value in metrics], className="result-metrics"),
        html.P(result["method"], className="result-method"),
        html.A("See Yahoo price history ↗", href=result["source_url"], target="_blank", rel="noopener noreferrer", className="result-source"),
    ], className="paper-result-content")
    record = {"ticker": result["ticker"], "mode": result["mode"], "initial_amount": result["initial_amount"], "ending_value": result["ending_value"], "total_return_pct": result["total_return_pct"], "context": context}
    updated = [*(positions or [])[-11:], record]
    return summary, paper_figure(result), {}, updated


@app.callback(Output("paper-history", "children"), Input("paper-positions", "data"))
def render_paper_history(positions):
    if not positions:
        return html.P("Run a scenario to see it here. Scenarios stay in this browser session.", className="history-empty")
    return [html.Div([html.Div([html.Strong(item["ticker"]), html.Span("LOOK BACK" if item["mode"] == "historical" else "LOOK AHEAD", className="history-mode")]), html.Div(item["context"], className="history-context"), html.Div([html.Span(_money(item["initial_amount"])), html.Span("→"), html.Strong(_money(item["ending_value"]))], className="history-values")], className="history-card") for item in reversed(positions)]


@app.callback(Output("holding-rows", "children"), Input("add-holding", "n_clicks"), State("holding-rows", "children"), prevent_initial_call=True)
def add_holding_row(n_clicks, rows):
    if not n_clicks or len(rows or []) >= 20:
        return no_update
    return [*(rows or []), holding_row(len(rows or []))]


VERDICT_MARK = {"clear": ("✓", "verdict-clear", "Clear"), "flag": ("⚠", "verdict-flag", "Flagged"), "unclear": ("?", "verdict-unclear", "Not enough data")}
SCREEN_COLUMNS = [("alcohol", "Alcohol"), ("gambling", "Gambling"), ("tobacco", "Tobacco"), ("ordnance", "Weapons"), ("fossil_fuels", "Fossil fuels"), ("high_debt", "Debt")]


def _verdict_cell(verdict: str, title: str = "") -> html.Td:
    mark, css, label = VERDICT_MARK.get(verdict, VERDICT_MARK["unclear"])
    return html.Td(html.Span(mark, className=f"verdict {css}", title=title or label), className="verdict-cell")


def _position_block(position: dict) -> html.Details:
    head = html.Summary([
        html.Strong(position["symbol"]), html.Span(position["name"], className="position-name"),
        html.Span(_money(position["value"]), className="position-value"),
    ])
    if position["kind"] == "sukuk":
        body = html.P("This fund holds sukuk (Islamic bonds), not company stock, so there are no companies to screen.", className="position-note")
    elif not position["holdings"]:
        body = html.P("Yahoo Finance did not report holdings for this fund, so it could not be screened.", className="position-note")
    else:
        flags = sum(1 for row in position["holdings"] for verdict in row["checks"].values() if verdict == "flag")
        note = f"Top {len(position['holdings'])} holdings = {position['top_weight_pct']:.0f}% of the fund." if position["kind"] == "fund" else "Individual stock."
        if position["is_benchmark"]:
            note += " Comparison ETF, not a Shariah fund."
        rows = [html.Tr([
            html.Td([html.Strong(row["ticker"]), html.Div(row["name"], className="company-name")]),
            html.Td(row["industry"], className="company-industry"),
            html.Td(f"{row['fund_weight_pct']:.1f}%" if position["kind"] == "fund" else "—"),
            html.Td(_money(row["dollars"])),
            *[_verdict_cell(row["checks"][key], row["reason"] if key != "high_debt" else (f"Debt is {row['debt_ratio_pct']}% of market value" if row["debt_ratio_pct"] is not None else "Debt data not available in a single currency")) for key, _ in SCREEN_COLUMNS],
        ], className="flag-row" if "flag" in row["checks"].values() else None) for row in position["holdings"]]
        body = html.Div([
            html.P([note, " ", html.Span(f"{flags} flag{'s' if flags != 1 else ''} found." if flags else "No flags found.", className="position-flags" if flags else "position-clean")], className="position-note"),
            html.Div(html.Table([
                html.Thead(html.Tr([html.Th("Company"), html.Th("Industry"), html.Th("% of fund"), html.Th("Your $"), *[html.Th(label) for _, label in SCREEN_COLUMNS]])),
                html.Tbody(rows),
            ], className="screen-table"), className="screen-table-wrap"),
        ])
    return html.Details([head, body], open=True, className="position-block")


@app.callback(Output("portfolio-result", "children"), Input("portfolio-run", "n_clicks"), State({"type": "holding-ticker", "index": ALL}, "value"), State({"type": "holding-value", "index": ALL}, "value"), prevent_initial_call=True)
def run_portfolio_review(n_clicks, tickers, values):
    if not n_clicks:
        return no_update
    try:
        holdings = []
        for ticker, value in zip(tickers, values):
            if not str(ticker or "").strip() and (value is None or str(value).strip() == ""):
                continue
            if not str(ticker or "").strip() or value is None or str(value).strip() == "":
                raise PortfolioInputError("Complete both fields for each holding, or leave the row blank.")
            holdings.append(f"{str(ticker).strip()},{value}")
        parsed = analyze_portfolio("\n".join(holdings))
        result = screen_portfolio({item["ticker"]: item["market_value"] for item in parsed["holdings"]})
    except PortfolioInputError as exc:
        return html.Div(str(exc), className="paper-error")
    except Exception:
        return html.Div("Screening is temporarily unavailable. Check the internet connection and OPENAI_API_KEY, then try again.", className="paper-error")
    tiles = []
    for category in result["categories"]:
        if category["dollars"] > 0:
            tiles.append(html.Div([html.Span("⚠", className="verdict verdict-flag"), html.Strong(category["label"]), html.Div(f"{_money(category['dollars'])} · {category['pct']:.1f}% of your portfolio", className="tile-amount"), html.Div(", ".join(category["companies"]), className="tile-companies")], className="screen-tile tile-flag"))
        else:
            tiles.append(html.Div([html.Span("✓", className="verdict verdict-clear"), html.Strong(category["label"]), html.Div("None found in screened holdings", className="tile-amount")], className="screen-tile tile-clear"))
    return html.Div([
        html.Div("YOUR RESULTS", className="eyebrow"),
        html.H2(f"We screened {result['companies_screened']} companies inside your portfolio."),
        html.P(f"Those holdings account for {result['covered_pct']:.0f}% of your {_money(result['total_value'])}. The rest sits in smaller holdings beyond each fund's top ten, or in sukuk funds that hold no company stock.", className="results-lede"),
        html.Div(tiles, className="screen-tiles"),
        html.H3("Fund by fund"),
        html.P(["✓ clear · ⚠ flagged · ? not enough data. Hover over a mark to see why."], className="screen-legend"),
        *[_position_block(position) for position in result["positions"]],
        html.Details([html.Summary("How this screen works"), html.P(f"Holdings and company data come from Yahoo Finance, checked {result['as_of']}. Business activities are classified by a gpt-6-luna screening agent from each company's industry and description; results are cached so repeat screens are instant. Debt is total debt divided by current market value, flagged above 30%; it shows ? when Yahoo reports debt and market value in different currencies. Screening standards differ (for example, AAOIFI and S&P use different debt bases), and this view does not compute purification amounts or check interest income.")], className="portfolio-method"),
    ], className="screen-results")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False, use_reloader=False)
