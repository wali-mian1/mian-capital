# Proposed architecture: ethical investment research and portfolio review

This is a design draft for the remaining portfolio tracker and eventual website integration. The chatbot is now implemented separately in Dash; see `README.md`.

## User flows

1. A visitor enters a ticker/name or asks a research question. A research agent resolves the security, calls evidence tools, and returns a structured explanation with a source/date for each fact, the selected screening method, and one of `passes`, `fails`, or `needs_review`.
2. A visitor enters holdings and portfolio weights. A deterministic portfolio service runs the same evidence-backed screen for each holding, applies any optional personal exclusions, and displays covered weight, passing weight, failing weight, and unknown weight. It never converts missing evidence into a pass.
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

The model explains and chooses tools; code applies documented screening rules and portfolio math. Keep a versioned screening methodology and trace every decisive input. A simple demo dataset can support repeatable tests, while live source adapters must clearly identify freshness and coverage.

## Delivery sequence

1. Inspect the existing website and choose the exact screening method and data providers.
2. Create a `.venv` in the new Python backend project before installing or running dependencies.
3. Implement source adapters, deterministic screen, structured agent, API, and a small test dataset.
4. Test real research questions, a mixed portfolio, missing-data handling, and a safety defense. Capture redacted traces and measured token usage.
5. Integrate the API into the existing website; run a user test and measure impact.
6. Build the self-contained report and slides from real app evidence; fresh-clone test the repository with `.env` one folder above it.
