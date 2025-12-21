import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]

BADGE_STR = """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
    <linearGradient id="smooth" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <rect rx="3" width="120" height="20" fill="#000"/>
    <rect rx="3" x="60" width="60" height="20" fill="{colour}"/>
    <path fill="{colour}" d="M60 0h4v20h-4z"/>
    <rect rx="3" width="120" height="20" fill="url(#smooth)"/>
    <g fill="#fff" text-anchor="middle"
        font-family="DejaVu Sans,Verdana,Geneva,sans-serif"
        font-size="11">
        <text x="30" y="14">coverage</text>
        <text x="90" y="14">{pct}%</text>
    </g>
</svg>"""


def update_cov_badge(root: str) -> int:
    cov_report = json.loads(Path(f"{root}/coverage.json").read_text())
    new_pct = to_2dp_float_str(cov_report["totals"]["percent_covered"])

    curr_badge = Path(f"{root}/coverage.svg").read_text()
    curr_pct = to_2dp_float_str(
        re.findall(r'<text x="90" y="14">([0-9]+(?:\.[0-9]+)?)%</text>', curr_badge)[0]
    )

    if new_pct == curr_pct:
        return 0

    Path(f"{root}/coverage.svg").write_text(make_badge(BADGE_STR, new_pct))
    return 1


def make_badge(badge_str: str, pct: int) -> str:
    pct = float(pct)
    colour = (
        "red"
        if pct < 50  # noqa: PLR2004
        else "orange"
        if pct < 70  # noqa: PLR2004
        else "yellow"
        if pct < 80  # noqa: PLR2004
        else "yellowgreen"
        if pct < 90  # noqa: PLR2004
        else "green"
    )
    return badge_str.format(colour=colour, pct=f"{pct:.2f}")


def to_2dp_float_str(pct: float) -> str:
    return f"{float(pct):.2f}"


if __name__ == "__main__":
    sys.exit(update_cov_badge(REPO_ROOT))
