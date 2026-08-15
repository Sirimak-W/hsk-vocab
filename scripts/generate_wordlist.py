"""
Build data/hsk-words.json for the flashcard app.

Source: drkameleon/complete-hsk-vocabulary — HSK 3.0 (2021 draft) lists.
The "exclusive" files hold only the words introduced at each level, which is
what we need to tag every word with the level it belongs to.

Re-run this whenever you want to rebuild the wordlist. It preserves any
example sentences already present in the existing data file, so a sentence
generation pass is never lost on rebuild.
"""
import json
import os
import urllib.request

BASE = ("https://raw.githubusercontent.com/drkameleon/"
        "complete-hsk-vocabulary/main/wordlists/exclusive/new/")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "hsk-words.json")


def fetch(level: int) -> list:
    with urllib.request.urlopen(f"{BASE}{level}.json", timeout=60) as r:
        return json.load(r)


def to_card(entry: dict, level: int) -> dict:
    # A handful of entries carry several readings (啊 has four). The first form
    # is the dominant one; extra readings would make the card ambiguous, so we
    # keep only the primary and note the count for later review.
    forms = entry["forms"]
    f = forms[0]
    return {
        "hanzi": entry["simplified"],
        "traditional": f.get("traditional"),
        "pinyin": f["transcriptions"]["pinyin"],
        # Two meanings max — long definitions measurably hurt recall on cards.
        "meaning": "; ".join(f["meanings"][:2]),
        "pos": "/".join(entry.get("pos", [])),
        "level": level,
        # Frequency drives the within-level ordering before decks are cut.
        "frequency": entry.get("frequency", 999999),
        "readings": len(forms),
        "sentence": None,
        "sentencePinyin": None,
        "sentenceEn": None,
    }


def main():
    # Keep sentences from any previous run.
    existing = {}
    if os.path.exists(OUT):
        for w in json.load(open(OUT, encoding="utf-8")):
            if w.get("sentence"):
                existing[w["hanzi"]] = (
                    w["sentence"], w.get("sentencePinyin"), w.get("sentenceEn")
                )

    cards = []
    for level in (1, 2, 3):
        raw = fetch(level)
        print(f"level {level}: {len(raw)} words")
        for entry in raw:
            card = to_card(entry, level)
            if card["hanzi"] in existing:
                s, sp, se = existing[card["hanzi"]]
                card["sentence"], card["sentencePinyin"], card["sentenceEn"] = s, sp, se
            cards.append(card)

    # Sort by level then frequency so deck cutting is deterministic even if
    # the upstream file order changes.
    cards.sort(key=lambda c: (c["level"], c["frequency"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(cards, fh, ensure_ascii=False, indent=1)

    with_sentence = sum(1 for c in cards if c["sentence"])
    print(f"\nwrote {len(cards)} words -> {os.path.normpath(OUT)}")
    print(f"decks of 20: {-(-len(cards) // 20)}")
    print(f"with example sentence: {with_sentence} ({with_sentence / len(cards):.0%})")


if __name__ == "__main__":
    main()
