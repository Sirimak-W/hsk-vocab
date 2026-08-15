# HSK 3 decks

Flashcard app for the HSK 3.0 (2021 draft) cumulative vocabulary — levels 1–3,
cut into fixed decks of 20 words. Static site, no build step, no dependencies.

## Contents

```
index.html                    the whole app (HTML + CSS + JS, one file)
data/hsk-words.json           2,209 words with pinyin, meaning, POS, level
scripts/generate_wordlist.py  rebuilds the wordlist from the source repo
scripts/generate_sentences.py fills in missing example sentences
```

## Deploy to GitHub Pages

```bash
# 1. create an empty repo on github.com first, then:
git init
git add .
git commit -m "HSK 3 flashcard decks"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from a branch →
Branch: `main` / `(root)` → Save.**

Live at `https://<you>.github.io/<repo>/` in about a minute.

## Word counts

The source list normalises repeated written forms, so the totals sit slightly
below the official syllabus figures:

| Level | Official (2021 draft) | In this data | Reason |
|---|---|---|---|
| 1 | 500 | 506 | variant forms counted separately |
| 2 | 772 | 750 | duplicates folded into level 1 |
| 3 | 973 | 953 | duplicates folded into lower levels |
| **Total** | **2,245** | **2,209** | 36 entries are repeated written forms |

2,209 words → **111 decks** of 20 (the last one holds 9).

## Example sentences

Only 24 words ship with a sentence. The rest render "No example sentence for
this word yet" — the app works fine without them. To fill them in:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-...
python scripts/generate_sentences.py --limit 200   # sample first, check quality
python scripts/generate_sentences.py               # then the rest
```

It writes after every batch of 20, so it is safe to interrupt and resume.
Commit the updated `data/hsk-words.json` when you are happy with the output.

## How decks are built

Deck membership is fixed. `SEED` in `index.html` drives a seeded PRNG, so the
same word lands in the same deck on every load and across devices.

1. Each level is shuffled independently with a stable seed.
2. Words are interleaved by relative position within their level, so every
   chunk of 20 inherits the pool's overall level ratio (~4 / 7 / 9).
3. Chunks are shuffled internally so levels are genuinely mixed, not ordered
   easy-to-hard.

**Do not change `SEED` after you start studying** — it reshuffles every deck
and your progress numbers stop meaning anything.

## Progress

Deck completion and retention are stored in `localStorage` under
`hsk-progress`. It is per-browser and per-device; there is no sync.

## Voice

Pronunciation is locked to Meijia (zh-TW), an Apple voice available on macOS
and iOS. On other platforms the app falls back to any Chinese voice and says so
in red on the deck screen. Note that Taiwan Mandarin differs from the mainland
standard HSK tests on some words (和 as `hàn`, 垃圾 as `lèsè`).

## Keyboard

| Key | Action |
|---|---|
| Space | reveal the card |
| 1–4 | grade: again / hard / good / easy |
| R | replay pronunciation |

## Source

Vocabulary from
[drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary).
