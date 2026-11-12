# unslop-rules

Open data and rules for spotting and removing **AI slop** from text: the phrases, hedges and formatting habits that make writing sound machine-generated.

- **Online tool:** [gounslop.com](https://gounslop.com): paste text, get a slop score and a natural rewrite (quick clean is free).
- **Full measured list with charts and method:** [gounslop.com/ai-slop-phrases](https://gounslop.com/ai-slop-phrases)

## What's here

| Path | What |
|---|---|
| `slop-rules.json` | 115 phrase rules (delete / replace / flag) + 5 structural patterns (em dashes, "not X, it's Y", rule of three…). Used by the gounslop rule engine. |
| `data/slop-rules.csv` | Same rules as CSV with plain-English replacements. |
| `data/ai-words-measured.csv` / `.json` | **Measured** top 100 words/phrases AI overuses vs humans, plus formatting stats. |
| `skill/SKILL.md` | Drop-in "unslop" skill for Claude Code (`~/.claude/skills/unslop/`) and Cursor rules. |
| `scripts/` | Corpus generation and analysis scripts to reproduce the numbers. |

## Key findings (2026-11-12)

300 questions from the [HC3 dataset](https://huggingface.co/datasets/Hello-SimpleAI/HC3) (CC BY-SA 4.0), answered by humans (HC3) and by gpt-4o-mini (100), gpt-5.4-nano (100), gpt-6-luna (100) with default settings.

| Per 1,000 words | Modern AI | Humans | ChatGPT (Dec 2022) |
|---|---|---|---|
| Em dashes | 4.5 | 0.21 | 0.06 |
| Bold spans | 32.68 | 0 | 0 |
| Bullet lines | 29.24 | 0.03 | 0 |

"delve" appeared **0 times** in 67,773 words of 2026 AI answers. The new tells are formatting, offers ("if you tell me…") and hedges.

### Top 25 (ratio = AI rate ÷ human rate, per 10k words)

| # | Phrase | Ratio | AI /10k | Human /10k |
|---|---|---|---|---|
| 1 | tell me | 26.8× | 7.97 | 0.15 |
| 2 | if you tell me | 34.1× | 5.02 | 0 |
| 3 | and whether | 28.2× | 4.13 | 0 |
| 4 | can help | 13.6× | 8.12 | 0.45 |
| 5 | can lead to | 17.5× | 5.16 | 0.15 |
| 6 | specific | 8.2× | 12.25 | 1.36 |
| 7 | summary | 19.5× | 2.8 | 0 |
| 8 | here are some | 12.2× | 3.54 | 0.15 |
| 9 | common | 6.7× | 14.02 | 1.97 |
| 10 | whether | 6.5× | 13.72 | 1.97 |
| 11 | it's important to | 16.6× | 2.36 | 0 |
| 12 | plan | 9.5× | 5.61 | 0.45 |
| 13 | can sometimes | 16.6× | 2.36 | 0 |
| 14 | avoid | 8.4× | 7.53 | 0.76 |
| 15 | may | 4.3× | 45 | 10.31 |
| 16 | and may | 15.6× | 2.21 | 0 |
| 17 | rules | 6.7× | 11.07 | 1.52 |
| 18 | improve | 10.2× | 2.95 | 0.15 |
| 19 | here are | 6.3× | 5.61 | 0.76 |
| 20 | especially if | 9.7× | 2.8 | 0.15 |
| 21 | beneficial | 13.6× | 1.92 | 0 |
| 22 | lead to | 7× | 7.23 | 0.91 |
| 23 | important to | 7.8× | 3.39 | 0.3 |
| 24 | if you want i | 12.7× | 1.77 | 0 |
| 25 | can create | 12.7× | 1.77 | 0 |

Full top 100: [`data/ai-words-measured.csv`](data/ai-words-measured.csv) · [gounslop.com/ai-slop-phrases](https://gounslop.com/ai-slop-phrases)

## Method (short)
1–4 word n-grams, lower-cased, markdown stripped. Kept phrases in ≥8 AI answers, spread over ≥3 of 5 topic sources (none >60%), AI/human ratio ≥3 (add-one smoothed). Ranked by log(ratio) × log(answers containing it). Limits: Q&A text only; some topic words remain. Signals, not proof: no tool can prove authorship.

## License
Rules and data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Credit: "gounslop.com" with a link. Human text is from HC3 (CC BY-SA 4.0); only aggregate counts are published here.

Maintained by Zhe Li · [gounslop.com](https://gounslop.com)
