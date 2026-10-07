"""Bangun file referensi frekuensi dari korpus.

Contoh:
    python scripts/build_reference.py --corpus data/corpus/ind_wikipedia_2021_30K-sentences.txt --lang id --out data/ref_id.json
    python scripts/build_reference.py --corpus data/corpus/eng_news_2023_30K-sentences.txt --lang en --format leipzig --out data/ref_en.json
"""

import argparse
import json
import math
import string
import sys
from collections import Counter
from pathlib import Path

ALPHABET = string.ascii_uppercase
HOLDOUT_FRACTION = 0.10


def clean_text(text: str) -> str:
    """Ubah ke huruf besar dan buang semua karakter selain A-Z."""
    return "".join(ch for ch in text.upper() if ch in ALPHABET)


def read_sentences(corpus_path: Path, format: str) -> list[str]:
    """Baca korpus menjadi daftar kalimat mentah.

    Format `leipzig`: tiap baris `nomor<TAB>kalimat`.
    Format `plain`: tiap baris non-kosong adalah satu kalimat.
    """
    sentences = []
    with corpus_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if format == "leipzig":
                _, _, sentence = line.partition("\t")
                sentence = sentence if sentence else line
            else:
                sentence = line
            if sentence.strip():
                sentences.append(sentence)
    return sentences


def split_holdout(
    sentences: list[str], fraction: float = HOLDOUT_FRACTION
) -> tuple[list[str], list[str]]:
    """Sisihkan `fraction` kalimat terakhir sebagai holdout.

    Mengembalikan (train, holdout). Referensi hanya dihitung dari train.
    """
    n_holdout = max(1, int(len(sentences) * fraction))
    return sentences[:-n_holdout], sentences[-n_holdout:]


def count_ngrams(cleaned: list[str]) -> tuple[Counter, Counter, Counter, Counter]:
    """Hitung unigram, bigram, trigram, dan konteks bigram per kalimat.

    N-gram tidak melewati batas kalimat.
    """
    unigram: Counter = Counter()
    bigram: Counter = Counter()
    trigram: Counter = Counter()
    bigram_context: Counter = Counter()
    for sentence in cleaned:
        unigram.update(sentence)
        for i in range(len(sentence) - 1):
            bigram[sentence[i : i + 2]] += 1
        for i in range(len(sentence) - 2):
            trigram[sentence[i : i + 3]] += 1
            bigram_context[sentence[i : i + 2]] += 1
    return unigram, bigram, trigram, bigram_context


def build_reference(sentences: list[str], lang: str) -> dict:
    """Bangun struktur referensi dari daftar kalimat mentah."""
    cleaned = [clean_text(s) for s in sentences]
    cleaned = [s for s in cleaned if s]
    if not cleaned:
        raise ValueError("Korpus kosong setelah dibersihkan (tidak ada huruf A-Z).")

    unigram, bigram, trigram, bigram_context = count_ngrams(cleaned)
    total_letters = sum(unigram.values())

    unigram_pct = {ch: unigram.get(ch, 0) / total_letters * 100.0 for ch in ALPHABET}

    bigram_logprob = {}
    for first in ALPHABET:
        context_count = sum(bigram.get(first + second, 0) for second in ALPHABET)
        for second in ALPHABET:
            prob = (bigram.get(first + second, 0) + 1) / (context_count + 26)
            bigram_logprob[first + second] = math.log(prob)

    trigram_logprob = {}
    for first in ALPHABET:
        for second in ALPHABET:
            context = first + second
            context_count = bigram_context.get(context, 0)
            for third in ALPHABET:
                prob = (trigram.get(context + third, 0) + 1) / (context_count + 26)
                trigram_logprob[context + third] = math.log(prob)

    return {
        "lang": lang,
        "n_sentences": len(cleaned),
        "n_letters": total_letters,
        "unigram": unigram_pct,
        "bigram": bigram_logprob,
        "trigram": trigram_logprob,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Urai argumen baris perintah."""
    parser = argparse.ArgumentParser(
        description="Bangun referensi frekuensi dari korpus."
    )
    parser.add_argument("--corpus", required=True, help="Path file korpus.")
    parser.add_argument(
        "--lang", required=True, choices=["en", "id"], help="Kode bahasa."
    )
    parser.add_argument(
        "--format",
        default="leipzig",
        choices=["leipzig", "plain"],
        help="Format korpus.",
    )
    parser.add_argument("--out", required=True, help="Path file JSON keluaran.")
    parser.add_argument(
        "--holdout",
        default=None,
        help="Path file holdout (default: data/samples/holdout_<lang>.txt).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Titik masuk skrip."""
    args = parse_args(argv)
    corpus_path = Path(args.corpus)
    if not corpus_path.is_file():
        print(f"Korpus tidak ditemukan: {corpus_path}", file=sys.stderr)
        return 1

    sentences = read_sentences(corpus_path, args.format)
    if not sentences:
        print("Korpus kosong (tidak ada kalimat).", file=sys.stderr)
        return 1

    train, holdout = split_holdout(sentences)

    holdout_path = (
        Path(args.holdout)
        if args.holdout
        else Path("data/samples") / f"holdout_{args.lang}.txt"
    )
    holdout_path.parent.mkdir(parents=True, exist_ok=True)
    with holdout_path.open("w", encoding="utf-8") as f:
        for sentence in holdout:
            f.write(sentence + "\n")

    reference = build_reference(train, args.lang)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(reference, f)

    print(f"Kalimat latih: {len(train)}, holdout: {len(holdout)} -> {holdout_path}")
    print(f"Referensi ({args.lang}): {reference['n_letters']} huruf -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
