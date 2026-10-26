# Final Project agent instructions

Use `gpt-6-luna` for all final-project model calls. `OPENAI_API_KEY` (direct OpenAI) is tried first; if it is missing or rejected, the same call falls back to the course `PORTKEY_API_KEY` through Portkey (student decision, October 26, 2026, so graders' course key always works). All other instructions in the course-root `AGENTS.md` still apply, including secret handling, the OpenAI Responses API pattern, and creating a `.venv` before installing or running dependencies for any new Python project.
