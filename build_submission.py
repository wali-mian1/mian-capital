"""Embed screenshots and reveal.js in the two standalone submission HTML files."""

from __future__ import annotations

import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCREENSHOTS = ROOT / "output"
ASSET_MAP = {
    "REVEAL_CSS": ROOT / "vendor" / "reveal.css",
    "REVEAL_JS": ROOT / "vendor" / "reveal.js",
}


def build(name: str) -> None:
    template = (ROOT / f"{name}.template.html").read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in ASSET_MAP:
            path = ASSET_MAP[key]
            if not path.exists():
                raise FileNotFoundError(f"Missing vendored reveal.js asset: {path}")
            return path.read_text(encoding="utf-8").replace("</script>", "<\\/script>")
        path = SCREENSHOTS / key
        if not path.is_file() or path.suffix.lower() != ".png":
            raise FileNotFoundError(path)
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return "data:image/png;base64," + data

    output = re.sub(r"@@([\w.\-]+)@@", replace, template)
    if "@@" in output:
        raise ValueError("Unfilled template marker")
    (ROOT / f"{name}.html").write_text(output, encoding="utf-8")


if __name__ == "__main__":
    build("report")
    build("slides")
