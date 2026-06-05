#!/usr/bin/env python3
"""Render Markdown files to PDFs with a local Chrome/Edge executable."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import fitz
import markdown


CSS = """
@page { size: A4; margin: 18mm 16mm; }
body {
  font-family: "Microsoft YaHei", "SimSun", "Noto Serif CJK SC", Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.58;
  color: #111;
}
h1, h2, h3 { line-height: 1.25; page-break-after: avoid; }
h1 { font-size: 22pt; margin: 0 0 18pt; }
h2 { font-size: 16pt; margin: 22pt 0 10pt; border-bottom: 1px solid #ddd; padding-bottom: 4pt; }
h3 { font-size: 12pt; margin: 16pt 0 8pt; }
p, li { orphans: 2; widows: 2; }
pre, code { font-family: Consolas, "Microsoft YaHei Mono", monospace; }
pre { white-space: pre-wrap; border: 1px solid #ddd; padding: 8pt; background: #fafafa; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; }
th, td { border: 1px solid #ccc; padding: 4pt 6pt; vertical-align: top; }
a { color: #174ea6; text-decoration: none; }
"""


def find_browser(explicit: str | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    for name in ("chrome", "google-chrome", "chromium", "msedge"):
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    candidates.extend(
        [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Chrome/Edge executable not found; pass --browser")


def render_one(md_path: Path, browser: Path, user_data_dir: Path) -> dict:
    html_path = md_path.with_suffix(".html")
    pdf_path = md_path.with_suffix(".pdf")
    body = markdown.markdown(
        md_path.read_text(encoding="utf-8"),
        extensions=["extra", "toc", "sane_lists"],
        output_format="html5",
    )
    html_path.write_text(
        f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>',
        encoding="utf-8",
    )
    user_data_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={user_data_dir}",
        f"--print-to-pdf={pdf_path}",
        "--print-to-pdf-no-header",
        html_path.resolve().as_uri(),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    doc = fitz.open(pdf_path)
    return {"markdown": str(md_path), "html": str(html_path), "pdf": str(pdf_path), "pages": len(doc), "bytes": pdf_path.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown_files", nargs="+")
    parser.add_argument("--browser")
    parser.add_argument("--user-data-dir", default=".paper-translate-browser-profile")
    args = parser.parse_args()

    browser = find_browser(args.browser)
    results = [render_one(Path(path).resolve(), browser, Path(args.user_data_dir).resolve()) for path in args.markdown_files]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
