"""
Fill in missing example sentences in data/hsk-words.json.

Runs in batches, writes after every batch, and skips words that already have a
sentence — so it is safe to stop and resume, and cheap to re-run after adding
new words.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    pip install anthropic
    python scripts/generate_sentences.py --limit 200      # try a slice first
    python scripts/generate_sentences.py                  # then the rest
"""
import argparse
import json
import os
import sys

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "hsk-words.json")
BATCH = 20
MODEL = "claude-sonnet-4-6"

PROMPT = """You write example sentences for a Chinese flashcard app at HSK 3 level.

For each word below, write ONE short example sentence.

Rules:
- 6-14 characters. Simplified characters only.
- Use only vocabulary at or below HSK 3. The target word is the hardest thing
  in the sentence.
- Show the word in its most common everyday usage, not an edge case.
- Natural modern Mandarin, not textbook-stiff.
- Pinyin with tone marks, capitalised as a sentence, spaced by word.

Return ONLY a JSON array, no markdown fences, no preamble:
[{"hanzi":"...","sentence":"...","sentencePinyin":"...","sentenceEn":"..."}]

Words:
%s
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="max words this run (0 = all)")
    args = ap.parse_args()

    try:
        from anthropic import Anthropic
    except ImportError:
        sys.exit("pip install anthropic")

    client = Anthropic()
    words = json.load(open(DATA, encoding="utf-8"))
    index = {w["hanzi"]: w for w in words}

    todo = [w for w in words if not w.get("sentence")]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(todo)} words need sentences")

    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        listing = "\n".join(f'{w["hanzi"]} ({w["pinyin"]}) — {w["meaning"]}' for w in batch)

        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                messages=[{"role": "user", "content": PROMPT % listing}],
            )
            text = "".join(b.text for b in resp.content if b.type == "text")
            # Strip fences defensively even though the prompt forbids them.
            text = text.replace("```json", "").replace("```", "").strip()
            for item in json.loads(text):
                w = index.get(item["hanzi"])
                if not w:
                    continue          # model returned a word we didn't ask for
                w["sentence"] = item["sentence"]
                w["sentencePinyin"] = item["sentencePinyin"]
                w["sentenceEn"] = item["sentenceEn"]
        except Exception as e:
            print(f"  batch {start // BATCH + 1} failed: {e} — continuing")
            continue

        # Write after every batch so an interrupted run loses at most 20 words.
        json.dump(words, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        done = sum(1 for w in words if w.get("sentence"))
        print(f"  batch {start // BATCH + 1}: {done}/{len(words)} complete")

    print("done")


if __name__ == "__main__":
    main()
