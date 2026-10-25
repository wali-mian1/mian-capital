# Proposed architecture: ethical investment research and portfolio review

This is the forward design for a constituent-level portfolio screen and eventual integration with the student's older website. The current Dash chatbot, Paper Lab, and issuer-evidence portfolio view are implemented; see `README.md`.

## User flows

1. A visitor enters a ticker/name or asks a research question. A research agent resolves the security, calls evidence tools, and returns a structured explanation with a source/date for each fact, the selected screening method, and one of `passes`, `fails`, or `needs_review`.
2. A visitor enters tickers and current USD market values. The current deterministic portfolio view reports issuer-described strategy weight and unknown weight. A future constituent-level service should apply a selected screening method and optional personal exclusions, then display passing, failing, and unknown weight with source dates. It must never convert missing evidence into a pass.
3. The visitor can inspect each holding's reason and bring the report to the human advisor for interpretation or next steps.

## Components

```text
Existing website / standalone demo UI
           |
           v
Dash chatbot now; possible future FastAPI endpoints: /api/screen, /api/portfolio
           |                     |
           |                     +--> deterministic screening and weighted aggregation
           v
PydanticAI research agent (chatbot: gpt-6-luna via Portkey)
           |
           +--> yfinance price tool and native web search (implemented)
           +--> fund holdings and deterministic screening tools (planned)
           +--> structured response with evidence, uncertainty, and usage
```

The model explains and chooses tools; code applies portfolio math. The current fund-level issuer evidence is not a full screening rule. A future version needs a versioned methodology and dated constituent data for every decisive input. A simple demo dataset can support repeatable tests, while live source adapters must clearly identify freshness and coverage.

## Delivery sequence

1. Inspect the existing website and choose the exact screening method and data providers.
2. Create a `.venv` in the new Python backend project before installing or running dependencies.
3. Implement source adapters, deterministic screen, structured agent, API, and a small test dataset.
4. Test real research questions, a mixed portfolio, missing-data handling, and a safety defense. Capture redacted traces and measured token usage.
5. Integrate the API into the existing website; run a user test and measure impact.
6. Build the self-contained report and slides from real app evidence; fresh-clone test the repository with `.env` one folder above it.
