"""Readable browser charts for paper scenarios and observed price-tool results."""

from __future__ import annotations

from datetime import date

import plotly.graph_objects as go

FOREST = "#245a43"
GOLD = "#b58b51"
GRID = "#e8eee6"


def _base_layout(figure: go.Figure, height: int) -> None:
    figure.update_layout(
        height=height,
        autosize=True,
        margin={"l": 56, "r": 18, "t": 60, "b": 46},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"family": "DM Sans, Arial, sans-serif", "color": "#52665a", "size": 12},
        legend={"orientation": "h", "x": 0, "y": 1.16, "xanchor": "left", "yanchor": "bottom", "font": {"size": 11}},
        hovermode="x unified",
        hoverlabel={"bgcolor": "#ffffff", "font_size": 12},
        xaxis={"showgrid": False, "zeroline": False, "automargin": True},
        yaxis={"showgrid": True, "gridcolor": GRID, "zeroline": False, "tickprefix": "$", "tickformat": ",.0f", "automargin": True},
    )


def paper_figure(result: dict) -> go.Figure:
    series = result["series"]
    historical = result["mode"] == "historical"
    x = [item["date"] if historical else item["year"] for item in series]
    investment = [item["investment_value"] for item in series]
    cash = [item["cash_at_zero_interest"] for item in series]
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=x, y=investment, mode="lines", name="Paper investment",
        line={"color": FOREST, "width": 3, "shape": "linear"},
        hovertemplate="%{x}<br><b>$%{y:,.2f}</b><extra></extra>",
        connectgaps=False,
    ))
    figure.add_trace(go.Scatter(
        x=x, y=cash, mode="lines", name="Cash at 0%",
        line={"color": GOLD, "width": 2, "dash": "dash"},
        hovertemplate="%{x}<br><b>$%{y:,.2f}</b><extra></extra>",
    ))
    figure.add_trace(go.Scatter(
        x=[x[-1]], y=[investment[-1]], mode="markers", showlegend=False,
        marker={"color": FOREST, "size": 10, "line": {"color": "#ffffff", "width": 2}},
        hovertemplate="Ending value<br><b>$%{y:,.2f}</b><extra></extra>",
    ))
    _base_layout(figure, 380)
    low, high = min(investment + cash), max(investment + cash)
    padding = max((high - low) * 0.12, result["initial_amount"] * 0.04)
    figure.update_yaxes(range=[max(0, low - padding), high + padding])
    if historical:
        figure.update_xaxes(type="date", tickformat="%b %Y", nticks=7, title_text="Historical close date")
    else:
        figure.update_xaxes(type="linear", dtick=max(1, result["horizon_years"] // 6), title_text="Years from today")
    return figure


def price_figure(tool_output: dict) -> go.Figure | None:
    rows = tool_output.get("prices") or []
    valid = [row for row in rows if isinstance(row, dict) and row.get("date") and isinstance(row.get("close_usd"), (int, float))]
    if not valid:
        return None
    x: list[str | None] = []
    y: list[float | None] = []
    previous: date | None = None
    for row in valid:
        current = date.fromisoformat(row["date"])
        if tool_output.get("prices_sampled") and previous and (current - previous).days > 14:
            x.append(None)
            y.append(None)
        x.append(row["date"])
        y.append(row["close_usd"])
        previous = current
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers" if len(valid) > 1 else "markers",
        name="Daily close", line={"color": FOREST, "width": 2.5},
        marker={"color": FOREST, "size": 5 if len(valid) > 1 else 10},
        connectgaps=False,
        hovertemplate="%{x}<br><b>$%{y:,.2f}</b><extra></extra>",
    ))
    _base_layout(figure, 250)
    figure.update_layout(margin={"l": 48, "r": 12, "t": 18, "b": 38}, showlegend=False)
    figure.update_xaxes(type="date", tickformat="%b %d", nticks=5)
    values = [row["close_usd"] for row in valid]
    low, high = min(values), max(values)
    pad = max((high - low) * 0.15, high * 0.015)
    figure.update_yaxes(range=[max(0, low - pad), high + pad])
    return figure
