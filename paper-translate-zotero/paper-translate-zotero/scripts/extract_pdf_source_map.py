#!/usr/bin/env python3
"""Extract page-aware source maps from research-paper PDFs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import fitz


SECTION_RE = re.compile(
    r"^(abstract|introduction|related work|method|methods|approach|experiments?|experimental evaluation|evaluation|results|discussion|conclusion|limitations?|references|bibliography|appendix|acknowledg(?:e)?ments?|supplementary material|"
    r"\d+\.?\s+[A-Z][A-Za-z0-9 ,:;()/-]{2,})$",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def page_text_in_reading_order(page: fitz.Page) -> str:
    blocks = []
    for raw in page.get_text("blocks"):
        if len(raw) < 5:
            continue
        x0, y0, x1, y1, text = raw[:5]
        text = clean_text(text)
        if len(text) < 3:
            continue
        blocks.append({"x0": x0, "y0": y0, "x1": x1, "text": text})
    if not blocks:
        return ""

    width = page.rect.width
    left = [b for b in blocks if (b["x0"] + b["x1"]) / 2 < width * 0.52]
    right = [b for b in blocks if (b["x0"] + b["x1"]) / 2 >= width * 0.52]
    wide = [b for b in blocks if (b["x1"] - b["x0"]) > width * 0.62]

    if len(left) >= 3 and len(right) >= 3:
        ordered = []
        consumed: set[int] = set()
        for b in sorted(wide, key=lambda item: item["y0"]):
            if b["y0"] < page.rect.height * 0.23:
                ordered.append(b)
                consumed.add(id(b))
        for column in (left, right):
            for b in sorted(column, key=lambda item: (item["y0"], item["x0"])):
                if id(b) not in consumed:
                    ordered.append(b)
                    consumed.add(id(b))
        for b in sorted(blocks, key=lambda item: (item["y0"], item["x0"])):
            if id(b) not in consumed:
                ordered.append(b)
    else:
        ordered = sorted(blocks, key=lambda item: (item["y0"], item["x0"]))

    return "\n\n".join(b["text"] for b in ordered)


def split_reading_block(text: str, limit: int) -> list[str]:
    if len(text) <= limit or (SECTION_RE.match(text) and len(text.split()) <= 10):
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= limit:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def extract_pdf(pdf_path: Path, block_limit: int) -> dict:
    doc = fitz.open(pdf_path)
    blocks = []
    sections = []
    sid = 1
    for page_number, page in enumerate(doc, start=1):
        page_text = page_text_in_reading_order(page)
        for raw_block in page_text.split("\n\n"):
            raw_block = clean_text(raw_block)
            if len(raw_block) < 20 and not SECTION_RE.match(raw_block):
                continue
            for block in split_reading_block(raw_block, block_limit):
                block_type = "section" if SECTION_RE.match(block) and len(block.split()) <= 10 else "text"
                block_id = f"S{sid:04d}"
                item = {
                    "id": block_id,
                    "page": page_number,
                    "type": block_type,
                    "original": block,
                    "translation": "",
                    "confidence": "text-extracted",
                }
                blocks.append(item)
                if block_type == "section":
                    sections.append({"id": block_id, "page": page_number, "title": block})
                sid += 1
    return {
        "paper": {
            "title": pdf_path.stem,
            "pdf_path": str(pdf_path.resolve()),
            "page_count": len(doc),
        },
        "sections": sections,
        "blocks": blocks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdfs", nargs="+", help="PDF files to extract")
    parser.add_argument("--out-dir", required=True, help="Directory for source maps")
    parser.add_argument("--block-limit", type=int, default=1300)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = []
    for pdf in args.pdfs:
        pdf_path = Path(pdf).expanduser().resolve()
        data = extract_pdf(pdf_path, args.block_limit)
        paper_dir = out_dir / pdf_path.stem
        paper_dir.mkdir(parents=True, exist_ok=True)
        source_map = paper_dir / "source_map.json"
        source_map.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        report.append(
            {
                "pdf": str(pdf_path),
                "source_map": str(source_map),
                "pages": data["paper"]["page_count"],
                "blocks": len(data["blocks"]),
            }
        )
    (out_dir / "extraction_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
