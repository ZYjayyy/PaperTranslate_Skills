# Translation Guidelines

## Reader Structure

Use a block-level bilingual shape:

```markdown
<a id="S0001"></a>
**Source:** p.1 S0001

**Original:** ...

**中文:** ...
```

For section headings:

```markdown
<a id="S0010"></a>
### p.3 S0010 3 Method

**中文标题:** 3 方法
```

## Terminology

Maintain a batch-level table. For robotics and embodied AI papers, these defaults are usually appropriate:

| English | 中文 |
|---|---|
| affordance | 可供性 |
| embodiment | 具身形态 |
| vision-language-action | 视觉-语言-动作 |
| vision-language model | 视觉-语言模型 |
| large language model | 大语言模型 |
| open-vocabulary | 开放词汇 |
| object-centric | 以对象为中心 |
| robot navigation | 机器人导航 |
| long-horizon | 长时程 |
| goal-conditioned | 目标条件化 |
| language-conditioned | 语言条件化 |
| value function | 价值函数 |
| semantic map | 语义地图 |
| submap | 子地图 |
| zero-shot | 零样本 |
| modality | 模态 |

Preserve names such as LM-Nav, OmniVLA, SayCan, FindAnything, CLIP, GPT-3, OpenVLA, ViNG, VNM, VLM, LLM, MAV, TSDF, SLAM, and dataset names.

## References and Tables

Keep references in original form by default. If the source block is inside a References/Bibliography section, use:

```markdown
**中文:** 参考文献条目保留原文，以避免机器翻译扭曲作者、题名、会议名和页码。
```

For extracted table rows that are mostly abbreviations or metrics, preserve abbreviations and add a compact Chinese note instead of forcing translation.

## PDF Extraction Caveats

Two-column PDFs often interleave left and right columns. Prefer column-aware extraction. If a page contains a wide title/figure/table block, place it before or near the relevant body text, but do not claim exact layout fidelity unless manually verified.

Watch for:

- page headers/footers mixed into text
- arXiv IDs inserted mid-paragraph
- figure labels split across columns
- references mistaken for body text
- repeated model output such as `LLMLLMLLM...`

## Completion Checks

Run a small audit before delivery:

- count source blocks, translated blocks, Markdown anchors, and pending markers
- sample beginning, middle, and end sections
- search for repeated token patterns
- verify PDF page counts
- verify Zotero import by title search or recent item inspection
