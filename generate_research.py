#!/usr/bin/env python3

from __future__ import annotations

import csv
from collections import defaultdict
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "research.csv"
OUTPUT_PATH = ROOT / "research.html"

SECTION_ORDER = [
    ("thesis", "学位論文・卒業論文"),
    ("talk", "学会発表"),
    ("journal", "査読付き論文"),
    ("conference", "国際会議論文"),
]


def load_records() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return sorted(rows, key=lambda row: row["sort_date"], reverse=True)


def render_record(record: dict[str, str]) -> str:
    title = escape(record["title"])
    authors = escape(record["authors"])
    venue = escape(record["venue"])
    details = escape(record["details"])
    url = record["url"].strip()

    title_html = f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{title}</a>' if url else title

    meta_parts = [part for part in [venue, details] if part]
    meta_html = " / ".join(meta_parts)

    return (
        "      <article class=\"entry\">\n"
        f"        <h3>{title_html}</h3>\n"
        f"        <p class=\"authors\">{authors}</p>\n"
        f"        <p class=\"meta\">{meta_html}</p>\n"
        "      </article>"
    )


def render_section(records: list[dict[str, str]], category: str, heading: str) -> str:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        if record["category"] == category:
            grouped[record["year"]].append(record)

    if not grouped:
        return ""

    parts = [f'    <section class="content-section">\n      <h2>{escape(heading)}</h2>']
    for year in sorted(grouped.keys(), reverse=True):
        parts.append(f"      <h3 class=\"year-heading\">{escape(year)}年</h3>")
        for record in grouped[year]:
            parts.append(render_record(record))
    parts.append("    </section>")
    return "\n".join(parts)


def build_html(records: list[dict[str, str]]) -> str:
    sections = "\n\n".join(
        section
        for category, heading in SECTION_ORDER
        if (section := render_section(records, category, heading))
    )

    return f"""<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>研究成果 | Takigawa Lab</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
      body {{
        font-family: 'Noto Sans JP', 'Roboto', sans-serif;
        margin: 0;
        padding: 0;
        background: #f5f5f5;
        color: #333;
        line-height: 1.7;
      }}
      .container {{
        max-width: 880px;
        margin: 30px auto;
        background: #fff;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }}
      h1 {{
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
      }}
      .lead {{
        margin-top: 0;
        color: #555;
      }}
      .nav {{
        margin-bottom: 1.5rem;
      }}
      .nav a {{
        color: #0056b3;
        text-decoration: none;
      }}
      .content-section {{
        margin-top: 2.2rem;
      }}
      .content-section h2 {{
        border-bottom: 2px solid #ddd;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
      }}
      .year-heading {{
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
        color: #0056b3;
      }}
      .entry {{
        padding: 0.9rem 0;
        border-bottom: 1px solid #eee;
      }}
      .entry h3 {{
        margin: 0 0 0.3rem;
        font-size: 1.05rem;
      }}
      .entry a {{
        color: #0056b3;
        text-decoration: none;
      }}
      .entry a:hover {{
        text-decoration: underline;
      }}
      .authors,
      .meta {{
        margin: 0.2rem 0;
      }}
      .authors {{
        font-weight: 700;
      }}
      footer {{
        margin-top: 2rem;
        font-size: 0.95rem;
        color: #666;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="nav"><a href="index.html">← トップページへ戻る</a></div>
      <header>
        <h1>研究成果</h1>
        <p class="lead">2025年以降の業績を掲載しています。</p>
      </header>
{sections}
    </div>
  </body>
</html>
"""


def main() -> None:
    records = load_records()
    OUTPUT_PATH.write_text(build_html(records), encoding="utf-8")


if __name__ == "__main__":
    main()
