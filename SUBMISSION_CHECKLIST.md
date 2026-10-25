# Final submission checklist

Deadline: **Monday, October 26, 2026, 6:00 PM Eastern**, on Canvas.

## Required Canvas items

- [ ] GitHub repository URL. The local repo is committed on `main`; publish it publicly or add `zlisto` to a private repo. Replace the pending GitHub line in `report.template.html`, rebuild `report.html`, and update slide 1 if appropriate.
- [x] `report.html`: one self-contained HTML file, 11 printed letter pages, embedded screenshots. Check the final GitHub link and every number before upload.
- [x] `slides.html`: one self-contained HTML file, nine reveal.js slides, embedded screenshots. Arrow-key navigation checked locally.
- [ ] Optional 2–3 minute demo video. Recommended as backup if a live data source or setup fails during grading. It does not replace the 10-minute local setup requirement.

## User evidence for Tier 3

- [ ] Ask one consenting target-community user to complete a specific fund research or portfolio task using their usual method; record the task and time.
- [ ] Have the same user try Mian Capital; record their time, whether the answer/date/source was correct, and one candid quote they permit in the report.
- [ ] Update the Impact page of `report.template.html` and slide 9 of `slides.template.html` with the real result. Rebuild the HTML using `.venv/bin/python build_submission.py` and verify that the report remains 10–15 printed pages.

## Suggested demo video outline

1. **0:00–0:25** Introduce the faith-aware investing problem and name the intended user.
2. **0:25–1:10** Ask for Amana Growth Fund's latest close. Open the `get_stock_price` panel to show `AMAGX`, date, output, and Yahoo source.
3. **1:10–1:45** Show the portfolio sample: 80% issuer-described screened strategy and 20% needing source review. Explain that this is evidence coverage, not certification.
4. **1:45–2:15** Show the Paper Lab's historical and assumed-future modes, including the chart and method labels.
5. **2:15–2:40** Show the blocked key request or describe the safety boundary and remaining constituent-level limitation.

## Recheck before uploading

- [x] `.env` and `output/audit.jsonl` are ignored; a staged-file scan found no apparent key value.
- [x] Clean-copy dependency installation, four page routes, and parent-folder `.env` discovery tested.
- [x] Report printed to 11 letter pages; slides opened and advanced with an arrow key.
- [ ] Confirm GitHub link works from an unauthenticated browser and the README starts the app within 10 minutes from the published repo.
- [ ] Upload the repository URL, `report.html`, and `slides.html` to Canvas before the deadline.
