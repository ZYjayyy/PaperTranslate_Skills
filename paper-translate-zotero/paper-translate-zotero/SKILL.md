---
name: paper-translate-zotero
description: Use when translating full research papers from Zotero attachments or local PDFs into paragraph-level Chinese-English Markdown readers, enforcing a shared terminology table across multiple papers, exporting readable PDF versions, and optionally importing generated PDFs back into Zotero through the local Connector.
---

# Paper Translate Zotero

## Overview

Create source-grounded full-paper translations from Zotero or local PDFs. The default deliverable is a paragraph-level bilingual Markdown reader plus a PDF version that can be opened inside Zotero.

Use this skill for requests such as:

- "把 Zotero 里的这些论文做全文翻译"
- "把几篇论文翻译成中英对照，并保持术语一致"
- "将翻译好的文件转成 PDF 并导入 Zotero"
- "从本地 PDF 文件夹批量生成论文翻译 reader"

Do not replace the output with a summary unless the user explicitly asks for a summary.

## Workflow

1. Resolve sources.
   - If the user names Zotero, first use the Zotero skill/helper to check `status --json`, search items, list children, and get PDF `file-url`s.
   - If the user gives local PDFs, treat those as the source files.
   - Keep Zotero writes explicit. Read operations are safe; imports are library writes.

2. Build a source map before translating.
   - Use `scripts/extract_pdf_source_map.py` or an equivalent PDF parser.
   - Preserve page numbers, stable block IDs (`S0001`, `S0002`, ...), original text, and extraction confidence.
   - For two-column papers, prefer column-aware reading order over raw PDF text order.
   - Mark tables, figure captions, references, and OCR/layout uncertainty when detected.

3. Translate conservatively.
   - Produce block-level original/Chinese pairs.
   - Preserve model names, dataset names, variables, equations, citations, units, and URLs.
   - Keep hedging and evidence chains; do not rewrite dense methods text into bullets.
   - Build one shared terminology table for a batch and apply it consistently.
   - Keep reference entries in original form unless the user asks to translate references; machine translation often corrupts author names and venues.

4. Write deliverables.
   - For each paper, write:
     - `paper.md`: bilingual reader
     - `source_map.json`: source blocks and translations
     - optional `translation_notes.md`: extraction/model caveats
   - Write a batch-level `terminology.md` and `translation_report.json`.
   - Use clear titles such as `中文全文翻译 - <PaperName>`.

5. Export PDFs for Zotero.
   - Use `scripts/render_markdown_to_pdf.py` when browser-based PDF printing is available.
   - Verify each PDF exists, has nonzero size, and has a plausible page count.
   - Prefer PDF over Markdown for Zotero because Zotero can preview PDFs reliably.

6. Import generated PDFs back into Zotero if requested.
   - Use `scripts/zotero_connector_import.py` or the Zotero Connector endpoint `/connector/saveStandaloneAttachment`.
   - Import PDF translations with titles such as `中文全文翻译PDF - <PaperName>`.
   - After import, search Zotero for the title and/or inspect recent items; Zotero may auto-recognize imported PDFs and turn some into new top-level items.
   - Do not delete old Markdown attachments unless the user explicitly approves the exact paths/items to delete.

## Quality Gates

Before reporting completion, verify:

- every source block has a translation or an intentional note
- `paper.md` has no `[待翻译]` markers
- Markdown anchors match `source_map.json` block counts
- generated PDFs open and have plausible page counts
- Zotero imports return `201` and are searchable or visible in recent items
- no obvious model-degeneration patterns remain, such as repeated `LLMLLMLLM` or long repeated initials

If a local machine translation model is used, clearly label the output as a machine-assisted first pass. For publication-quality translation, recommend a human/LLM polishing pass over the generated reader.

## Scripts

- `scripts/extract_pdf_source_map.py`: create page-aware source maps from one or more PDFs.
- `scripts/render_markdown_to_pdf.py`: render Markdown readers to PDFs with Chrome/Edge headless printing.
- `scripts/zotero_connector_import.py`: import generated files to Zotero through the local Connector.

Read `references/translation-guidelines.md` when the task needs detailed terminology, table/reference, or verification rules.
