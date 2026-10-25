"""Mian Capital Dash chat shell. Run: python app.py, then open http://127.0.0.1:8050."""

from __future__ import annotations

import json
from pathlib import Path

from dash import Dash, Input, Output, State, dcc, html, no_update, clientside_callback
import plotly.graph_objects as go

from agent import run_agent
from paper_trader import PaperTradeError, simulate_future, simulate_historical
from portfolio_alignment import PortfolioInputError, analyze_portfolio

HERE = Path(__file__).resolve().parent
PORTFOLIO_PATH = HERE / "portfolio.json"
app = Dash(__name__, title="Mian Capital | Research chat")
server = app.server

WELCOME = (
    "Assalamu alaikum. Ask for a fund's dated price, recent news, or public screening information. "
    "I cover **HLAL, SPUS, AMANX, AMAGX, SPRE, SPSK, UMMA, and SPWO**. "
    "Open each tool step to see its input and output."
)


def feature_card(number: str, icon: str, title: str, copy: str, foot: str, delay: str) -> html.Article:
    return html.Article(
        [
            html.Div([html.Img(src=app.get_asset_url(icon), alt="", className="feature-icon"), html.Span(number, className="feature-number")], className="feature-top"),
            html.H3(title),
            html.P(copy),
            html.Div(foot, className="feature-foot"),
        ],
        className=f"feature-card reveal {delay}",
    )

app.layout = html.Div(
    [
        dcc.Store(id="chat-history", storage_type="session", data=[{"role": "assistant", "content": WELCOME}]),
        dcc.Store(id="pending-request", data=None),
        dcc.Store(id="paper-positions", storage_type="session", data=[]),
        dcc.Location(id="site-location", refresh=False),
        dcc.Interval(id="agent-poll", interval=250, n_intervals=0, max_intervals=0, disabled=True),
        html.Div(id="scroll-signal", style={"display": "none"}),
        html.Header(html.Div([
            html.A([html.Div("M", className="mark", **{"aria-hidden": "true"}), html.Div([html.Div("MIAN CAPITAL", className="brand"), html.Div("Values at the heart of investing", className="brand-sub")])], href="/", className="brand-lockup", **{"aria-label": "Mian Capital, home"}),
            html.Nav([html.A("Our approach", href="/#approach"), html.A("About", href="/about"), html.A("Paper Lab", href="/paper-lab"), html.A("Portfolio", href="/portfolio"), html.A("Ask the assistant", href="/#research", className="nav-cta")], className="top-nav", **{"aria-label": "Main navigation"}),
        ], className="topbar-inner"), className="topbar"),
        html.Main([
            html.Section([
                html.Div([
                    html.Div([html.Span(className="eyebrow-line"), "INVEST WITH INTENTION"], className="eyebrow"),
                    html.H1(["Your values. ", html.Br(), "Your future. ", html.Em("In harmony.")], className="hero-title"),
                    html.P("Explore investments through the lens of your faith and principles. Mian Capital brings clear research, visible sources, and a human perspective to the conversation.", className="hero-copy"),
                    html.Div([html.A(["Explore fund research", html.Span("↗", **{"aria-hidden": "true"})], href="#research", className="primary-cta"), html.A("See our approach", href="#approach", className="text-cta")], className="hero-actions"),
                    html.Div([html.Span("FAITH AWARE"), html.Span(className="hero-dot"), html.Span("EVIDENCE FIRST"), html.Span(className="hero-dot"), html.Span("HUMAN GUIDED")], className="hero-signals"),
                ], className="hero-content reveal"),
                html.Div([
                    html.Img(src=app.get_asset_url("hero-wealth.svg"), alt="Illustration of a gold coin, rising bars, and a leaf inside an arch", className="hero-image"),
                    html.Div([html.Span("01 / 03", className="art-index"), html.Span("A thoughtful path to investing", className="art-caption")], className="hero-art-foot"),
                ], className="hero-art reveal delay-1"),
            ], id="top", className="hero-section"),
            html.Section([
                html.Div([html.Div("INVESTING, WITH PURPOSE", className="eyebrow"), html.H2("More than a return on paper."), html.P("The right investment conversation considers what a fund owns, how it is screened, and what matters to you.")], className="section-heading reveal"),
                html.Div([
                    feature_card("01", "icon-values.svg", "Why values matter", "For many investors, faith and personal principles shape which businesses they can support. Clear screening information helps turn those priorities into informed questions.", "YOUR PRINCIPLES, VISIBLE", "delay-1"),
                    feature_card("02", "icon-research.svg", "What we offer", "Ask about supported funds, dated prices, and recent news. Inspect the tools and sources behind each answer, then bring the findings to a human advisor.", "RESEARCH YOU CAN INSPECT", "delay-2"),
                    feature_card("03", "icon-journey.svg", "How to use us", "Start with a question. Review the evidence and what remains uncertain. Use that clarity to guide your next conversation and decision.", "A SIMPLE PLACE TO START", "delay-3"),
                ], className="feature-grid"),
            ], id="approach", className="approach-section"),
            html.Section([
                html.Div([html.Div("EXPLORE WITH CONFIDENCE", className="eyebrow"), html.H2("Ask. Explore. Understand."), html.P("A research companion for Shariah-oriented funds. Every price comes from a tool, and every search can be inspected."),], className="section-heading reveal"),
                html.Div([
                html.Section([
                    html.Div([html.Div("MIAN CAPITAL ASSISTANT", className="card-kicker"), html.Div("Fund research", className="card-title")], className="chat-head"),
                    html.Div(id="chat-window", className="chat-window", role="log", **{"aria-live": "polite"}),
                    html.Div([
                        dcc.Input(id="composer", type="text", debounce=False, placeholder="Ask for Amana Growth Fund's price or news about HLAL...", className="composer", autoComplete="off"),
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
                    html.Div("THE CURRENT UNIVERSE", className="side-kicker"),
                    html.Div([html.Span(x, className="ticker") for x in ("HLAL", "SPUS", "AMANX", "AMAGX", "SPRE", "SPSK", "UMMA", "SPWO")], className="ticker-list"),
                    html.P("Prices come from Yahoo Finance through yfinance. News uses OpenAI web search. Public screening claims are not independent religious certification.", className="side-note"),
                ], className="side-card reveal delay-2"),
                ], className="content-grid"),
            ], id="research", className="research-section"),
        ], id="home-page", className="page-content"),
        html.Main([
            html.Section([
                html.Div([
                    html.Div([html.Span(className="eyebrow-line"), "THE PERSON BEHIND THE RESEARCH"], className="eyebrow"),
                    html.H1(["Investing guidance with ", html.Em("people in mind.")], className="subpage-title"),
                    html.P("Mian Capital brings a quantitative mindset and a values-aware conversation to people who want to get started with greater clarity.", className="subpage-lede"),
                    html.A("Try the research assistant ↗", href="/#research", className="primary-cta"),
                ], className="about-hero-copy reveal"),
                html.Div([
                    html.Img(src=app.get_asset_url("advisor-figurine.svg"), alt="Playful illustrated advisor figurine with glasses, a calculator, and a coin", className="advisor-figurine"),
                    html.Div("WALI MIAN · FOUNDER", className="advisor-label"),
                    html.Div("A quantitative lens. A human conversation.", className="advisor-card-quote"),
                ], className="advisor-card reveal delay-1"),
            ], className="about-hero"),
            html.Section([
                html.Div("ABOUT YOUR ADVISOR", className="eyebrow"),
                html.H2("Rooted in numbers. Guided by values."),
                html.P("I’m Wali Mian, a Yale School of Management student with eight years of personal investing experience. I studied mathematics and actuarial science at UT Austin, then spent four years as an actuary focused on retirement and benefits, including 401(k), defined benefit, defined contribution, and pension plans. I started Mian Capital to make investing conversations clearer for people in my community who want their financial choices to reflect their faith.", className="bio-copy"),
                html.Div([html.Span("Yale SOM student"), html.Span("UT Austin math + actuarial science"), html.Span("4 years in retirement benefits"), html.Span("8 years investing")], className="bio-tags"),
            ], className="bio-section reveal"),
            html.Section([
                html.Div([
                    html.Div("STARTING IS OFTEN THE HARDEST PART", className="eyebrow"),
                    html.H2("From the first paycheck to the first account."),
                    html.P("After years of training, many professionals, including new physicians, face a sudden jump in income without a clear investing setup. We can help you understand account choices and take the first steps with confidence.", className="service-lede"),
                ], className="service-heading reveal"),
                html.Div([
                    html.Article([html.Div("01", className="service-step-number"), html.H3("Choose a place to begin"), html.P("Understand the basics of opening a brokerage account at firms such as Vanguard, Fidelity, or Charles Schwab, and what to look for in an account.")], className="service-step reveal delay-1"),
                    html.Article([html.Div("02", className="service-step-number"), html.H3("Set it up securely"), html.P("Walk through the account-opening and funding process. You keep control of your credentials, personal information, and account access.")], className="service-step reveal delay-2"),
                    html.Article([html.Div("03", className="service-step-number"), html.H3("Learn the mechanics"), html.P("Understand tickers, order types, and the steps involved in placing your own first trade before making any real decision.")], className="service-step reveal delay-3"),
                ], className="service-grid"),
                html.P("Mian Capital’s current site offers education and setup guidance. It does not place trades or take control of client accounts through this website.", className="service-boundary"),
            ], className="account-section"),
            html.Section([html.Div("CURIOUS WHAT A DECISION COULD HAVE LOOKED LIKE?", className="eyebrow"), html.H2("Learn with paper money first."), html.P("Try a hypothetical purchase using historical prices or explore how an assumed annual rate compounds. No account and no real order required."), html.A("Open the Paper Lab ↗", href="/paper-lab", className="primary-cta")], className="about-close reveal"),
        ], id="about-page", className="page-content subpage-content", hidden=True),
        html.Main([
            html.Section([
                html.Div([html.Div([html.Span(className="eyebrow-line"), "PAPER MONEY · REAL QUESTIONS"], className="eyebrow"), html.H1(["What if you had ", html.Em("started earlier?")], className="subpage-title"), html.P("Explore a hypothetical investment with real historical prices, or choose your own growth rate to see how compounding works. No real trades, no account connection, and no prediction of future returns.", className="subpage-lede")], className="paper-hero-copy reveal"),
                html.Div([html.Div("$", className="paper-coin"), html.Div("TRY IT WITHOUT RISKING A DOLLAR", className="paper-coin-label")], className="paper-hero-art reveal delay-1"),
            ], className="paper-hero"),
            html.Section([
                html.Div([html.Div("BUILD A SCENARIO", className="eyebrow"), html.H2("Put paper money to work."), html.P("Choose a ticker and an amount. Historical mode uses dated Yahoo prices; future mode compounds a rate that you choose.")], className="section-heading reveal"),
                html.Div([
                    html.Div([
                        html.Div("1. Choose a view", className="form-kicker"),
                        dcc.RadioItems(id="paper-mode", options=[{"label": "Look back", "value": "historical"}, {"label": "Look ahead", "value": "future"}], value="historical", className="mode-options"),
                        html.Div([html.Label("Ticker symbol", htmlFor="paper-ticker"), dcc.Input(id="paper-ticker", type="text", value="HLAL", placeholder="HLAL or another USD ticker", className="paper-input"), html.Small("This paper lab can test USD-listed stocks or funds. It does not place a trade.")], className="field"),
                        html.Div([html.Label("Paper-money amount (USD)", htmlFor="paper-amount"), dcc.Input(id="paper-amount", type="number", value=10000, min=100, max=1000000, step=100, className="paper-input")], className="field"),
                        html.Div([html.Label("Hypothetical purchase date"), dcc.DatePickerSingle(id="paper-date", date="2021-10-25", display_format="MMM D, YYYY", className="paper-date")], id="historical-controls", className="field"),
                        html.Div([html.Div([html.Label("Years from today", htmlFor="paper-years"), dcc.Input(id="paper-years", type="number", value=10, min=1, max=30, step=1, className="paper-input")], className="field"), html.Div([html.Label("Assumed annual return (%)", htmlFor="paper-rate"), dcc.Input(id="paper-rate", type="number", value=6, min=-30, max=30, step=0.5, className="paper-input")], className="field"), html.Small("This rate is your assumption, not a forecast for the ticker.")], id="future-controls", className="future-fields", style={"display": "none"}),
                        html.Button("Run paper scenario", id="paper-run", n_clicks=0, className="paper-run"),
                        html.P("Historical returns can be negative. A checking-account comparison assumes 0% interest and does not include inflation.", className="paper-form-note"),
                    ], className="paper-form reveal delay-1"),
                    html.Div([html.Div("YOUR RESULTS", className="form-kicker"), html.Div("Your scenario will appear here after you run it.", id="paper-result", className="paper-result-empty"), dcc.Graph(id="paper-chart", figure=go.Figure(), style={"display": "none"}, config={"displayModeBar": False, "responsive": True})], className="paper-output reveal delay-2"),
                ], className="paper-workspace"),
            ], className="paper-work-section"),
            html.Section([html.Div("SAVED IN THIS BROWSER SESSION", className="eyebrow"), html.H2("Your paper scenarios"), html.Div(id="paper-history", className="paper-history")], className="paper-history-section reveal"),
            html.P("Paper Lab is for education. It does not connect to a brokerage, execute trades, or guarantee results. Past performance does not predict future returns.", className="paper-disclaimer"),
        ], id="paper-page", className="page-content subpage-content", hidden=True),
        html.Main([
            html.Section([
                html.Div([html.Div([html.Span(className="eyebrow-line"), "YOUR HOLDINGS · YOUR VALUES"], className="eyebrow"), html.H1(["See what your portfolio ", html.Em("can show.")], className="subpage-title"), html.P("Enter market values to see how much of your portfolio has documented issuer screening claims and how much needs review. The result shows evidence coverage, not a religious certification.", className="subpage-lede")], className="reveal"),
            ], className="portfolio-hero"),
            html.Section([
                html.Div([html.Div("START WITH WHAT YOU OWN", className="eyebrow"), html.H2("A clearer view of alignment."), html.P("Paste one ticker and current USD market value per line. The sample is illustrative. You can add up to 20 holdings; no account connection or personal identity is needed.")], className="section-heading reveal"),
                html.Div([
                    html.Div([
                        html.Label("Holdings: ticker, current market value (USD)", htmlFor="portfolio-input"),
                        dcc.Textarea(id="portfolio-input", value="HLAL,5000\nSPUS,3000\nAMAGX,2000", className="portfolio-textarea"),
                        html.Small("Example: HLAL,5000. Use today's position values, not share counts."),
                        html.Div("Extra personal exclusions to flag for review", className="portfolio-exclusion-label"),
                        dcc.Checklist(id="portfolio-exclusions", options=[{"label": "Tobacco", "value": "tobacco"}, {"label": "Weapons", "value": "weapons"}, {"label": "Fossil fuels", "value": "fossil_fuels"}], value=[], className="portfolio-checklist"),
                        html.Button("Review my portfolio", id="portfolio-run", n_clicks=0, className="paper-run"),
                        html.P("Entries are processed by this app when you run a review; the form resets on reload. This version does not check every underlying company in a fund.", className="paper-form-note"),
                    ], className="paper-form reveal delay-1"),
                    html.Div([html.Div("YOUR EVIDENCE VIEW", className="form-kicker"), html.Div("Run a review to see coverage and holding-level sources.", id="portfolio-result", className="paper-result-empty")], className="paper-output reveal delay-2"),
                ], className="paper-workspace"),
            ], className="paper-work-section"),
            html.P("Issuer descriptions are claims about fund strategy, not independent checks of every current holding or a fatwa. Missing evidence is shown as unknown. Consult a qualified scholar and financial professional for decisions.", className="paper-disclaimer"),
        ], id="portfolio-page", className="page-content subpage-content", hidden=True),
        html.Footer(html.Div([html.Div([html.Div("M", className="footer-mark"), html.Div([html.Strong("MIAN CAPITAL"), html.Span("Invest with intention.")], className="footer-brand")]), html.Div("Research to support a thoughtful conversation. Fund information is not a religious ruling or personal investment advice.", className="footer-note")], className="footer-inner"), className="footer"),
    ], className="app-shell",
)


def render_messages(history, pending):
    blocks = []
    for message in history or []:
        assistant = message.get("role") == "assistant"
        blocks.append(html.Div([
            html.Div("Mian Capital" if assistant else "You", className="message-label"),
            dcc.Markdown(str(message.get("content", "")), className="message-body", link_target="_blank"),
            html.Div([html.Details([
                html.Summary(f"{event.get('name', 'tool')} · {event.get('status', 'completed')}"),
                html.Div("Input", className="tool-label"),
                html.Pre(json.dumps(event.get("input"), indent=2, ensure_ascii=False, default=str), className="tool-json"),
                html.Div("Output", className="tool-label"),
                html.Pre(json.dumps(event.get("output"), indent=2, ensure_ascii=False, default=str), className="tool-json"),
            ], className="tool-detail") for event in message.get("tool_events", [])], className="tool-events") if message.get("tool_events") else None,
            html.Div(f"Tokens: {message['usage'].get('input_tokens', 0)} in · {message['usage'].get('cached_input_tokens', 0)} cached · {message['usage'].get('output_tokens', 0)} out", className="usage") if message.get("usage") else None,
        ], className="message assistant" if assistant else "message user"))
    if pending:
        blocks.append(html.Div([html.Div("Mian Capital", className="message-label"), html.Span("Thinking", className="thinking")], className="message assistant", role="status"))
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


@app.callback(Output("send-button", "disabled"), Output("composer", "disabled"), Input("pending-request", "data"))
def lock_composer(pending):
    return bool(pending), bool(pending)


@app.callback(
    Output("chat-history", "data", allow_duplicate=True), Output("pending-request", "data"),
    Output("composer", "value"), Output("agent-poll", "disabled"),
    Output("agent-poll", "n_intervals"), Output("agent-poll", "max_intervals"),
    Input("send-button", "n_clicks"), Input("composer", "n_submit"),
    State("composer", "value"), State("chat-history", "data"), State("pending-request", "data"),
    prevent_initial_call=True,
)
def submit_message(_, __, text, history, pending):
    if pending or not text or not text.strip():
        return (no_update,) * 6
    question = text.strip()[:1500]
    return [*(history or []), {"role": "user", "content": question}], {"text": question}, "", False, 0, 1


@app.callback(
    Output("chat-history", "data", allow_duplicate=True), Output("pending-request", "data", allow_duplicate=True),
    Output("agent-poll", "disabled", allow_duplicate=True), Input("agent-poll", "n_intervals"),
    State("pending-request", "data"), State("chat-history", "data"), prevent_initial_call=True,
)
def complete_agent_turn(_, pending, history):
    if not pending:
        return no_update, no_update, True
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
    Input("site-location", "pathname"),
)
def show_page(pathname):
    if pathname == "/about":
        return True, False, True, True
    if pathname == "/paper-lab":
        return True, True, False, True
    if pathname == "/portfolio":
        return True, True, True, False
    return False, True, True, True


@app.callback(
    Output("historical-controls", "style"),
    Output("future-controls", "style"),
    Input("paper-mode", "value"),
)
def show_paper_fields(mode):
    return ({"display": "none"}, {}) if mode == "future" else ({}, {"display": "none"})


def _money(amount: float) -> str:
    return f"{'−' if amount < 0 else ''}${abs(amount):,.2f}"


def _paper_figure(result: dict) -> go.Figure:
    series = result["series"]
    x = [row.get("date", row.get("year")) for row in series]
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=x, y=[row["investment_value"] for row in series], mode="lines", name="Paper investment", line={"color": "#245a43", "width": 3}, fill="tozeroy", fillcolor="rgba(50,113,76,.10)"))
    figure.add_trace(go.Scatter(x=x, y=[row["cash_at_zero_interest"] for row in series], mode="lines", name="Cash at 0%", line={"color": "#b58b51", "width": 2, "dash": "dash"}))
    figure.update_layout(height=330, margin={"l": 55, "r": 12, "t": 20, "b": 48}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"family": "DM Sans, Arial", "color": "#4b5d51", "size": 11}, legend={"orientation": "h", "y": 1.12, "x": 0}, hovermode="x unified", xaxis={"title": "Date" if result["mode"] == "historical" else "Years from today", "showgrid": False}, yaxis={"title": "Illustrative value (USD)", "gridcolor": "#e5ebe3", "tickprefix": "$"})
    return figure


@app.callback(
    Output("paper-result", "children"),
    Output("paper-chart", "figure"),
    Output("paper-chart", "style"),
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
    return summary, _paper_figure(result), {}, updated


@app.callback(Output("paper-history", "children"), Input("paper-positions", "data"))
def render_paper_history(positions):
    if not positions:
        return html.P("Run a scenario to see it here. Scenarios stay in this browser session.", className="history-empty")
    return [html.Div([html.Div([html.Strong(item["ticker"]), html.Span("LOOK BACK" if item["mode"] == "historical" else "LOOK AHEAD", className="history-mode")]), html.Div(item["context"], className="history-context"), html.Div([html.Span(_money(item["initial_amount"])), html.Span("→"), html.Strong(_money(item["ending_value"]))], className="history-values")], className="history-card") for item in reversed(positions)]


@app.callback(Output("portfolio-result", "children"), Input("portfolio-run", "n_clicks"), State("portfolio-input", "value"), State("portfolio-exclusions", "value"), prevent_initial_call=True)
def run_portfolio_review(_, holdings_text, exclusions):
    try:
        result = analyze_portfolio(holdings_text, exclusions)
    except PortfolioInputError as exc:
        return html.Div(str(exc), className="paper-error")
    rows = []
    for item in result["holdings"]:
        rows.append(html.Div([
            html.Div([html.Strong(item["ticker"]), html.Span(f"{item['weight_pct']:.2f}% of portfolio", className="portfolio-weight")], className="portfolio-row-head"),
            html.Div(item["name"], className="portfolio-name"),
            html.Div(item["status"], className="portfolio-status"),
            html.P(item["explanation"]),
            html.A("Issuer source ↗", href=item["source_url"], target="_blank", rel="noopener noreferrer") if item["source_url"] else html.Span("No reviewed source", className="portfolio-no-source"),
            html.Div(f"Source checked: {item['source_checked_on']}" if item["source_checked_on"] else "Source check pending", className="portfolio-source-date"),
        ], className="portfolio-row"))
    selected = ", ".join(x.replace("_", " ") for x in result["personal_exclusions"])
    return html.Div([
        html.H3("Portfolio evidence coverage"),
        html.Div([html.Div([html.Strong(f"{result['issuer_screened_share_pct']:.2f}%"), html.Span("Issuer-described screened strategies")]), html.Div([html.Strong(f"{result['needs_review_share_pct']:.2f}%"), html.Span("Needs source review")])], className="portfolio-score-grid"),
        html.P(f"Entered portfolio value: {_money(result['total_value'])}", className="portfolio-total"),
        html.H4("Holding-level evidence"),
        html.Div(rows, className="portfolio-rows"),
        html.H4("Your extra exclusions"),
        html.P(f"{selected.title()}: {result['personal_exclusions_status']}. Current fund holdings have not been checked for these exclusions." if selected else "None selected. You can select extra exclusions and run the review again."),
        html.Details([html.Summary("How this percentage is calculated"), html.P(result["method"])], className="portfolio-method"),
    ], className="portfolio-results")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False, use_reloader=False)
