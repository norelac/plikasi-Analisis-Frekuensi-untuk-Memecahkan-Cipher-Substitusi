"""Evaluasi akurasi pemecahan cipher (teks uji dari data holdout).

Contoh:
    python scripts/evaluate.py --quick
    python scripts/evaluate.py
"""

import argparse
import csv
import string
import sys
import time
from bisect import bisect_right
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from src import cipher, cracker
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src import cipher, cracker

ALPHABET = string.ascii_uppercase
LENGTHS = [50, 100, 200, 500, 1000]
LANGS = ("id", "en")
METHODS = ("guess", "hill")
ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
SAMPLES_DIR = ROOT_DIR / "data" / "samples"


def letter_count(text: str) -> int:
    """Jumlah huruf A-Z dalam teks (case-insensitive)."""
    return sum(1 for ch in text.upper() if ch in ALPHABET)


def char_accuracy(decrypted: str, expected: str) -> float:
    """Fraksi huruf (A-Z, case-insensitive) hasil dekripsi yang benar."""
    dec = [ch for ch in decrypted.upper() if ch in ALPHABET]
    exp = [ch for ch in expected.upper() if ch in ALPHABET]
    if not exp:
        return 0.0
    return sum(1 for a, b in zip(dec, exp) if a == b) / len(exp)


def take_sample(
    sentences: list[str],
    counts: list[int],
    prefix: list[int],
    target: int,
    index: int,
    n: int,
) -> str:
    """Ambil potongan kalimat dengan >= target huruf, mulai deterministik.

    Sampel ke-`index` dari `n` mulai pada posisi huruf `index * total // n`.
    """
    total = prefix[-1]
    if target > total:
        raise ValueError(
            f"Target huruf ({target}) melebihi total huruf teks ({total})."
        )
    start = (index * total) // n
    first = max(0, bisect_right(prefix, start, 0, len(prefix) - 1) - 1)
    parts, gathered, i = [], 0, first
    max_steps = len(sentences) * 2
    steps = 0
    while gathered < target:
        if steps >= max_steps:
            break
        parts.append(sentences[i % len(sentences)])
        gathered += counts[i % len(sentences)]
        i += 1
        steps += 1
    return " ".join(parts)


def evaluate_sample(text: str, lang: str, seed: int) -> list[dict]:
    """Enkripsi teks lalu pecahkan dengan kedua metode, kembalikan baris hasil."""
    key = cipher.generate_key(seed)
    ciphertext = cipher.substitution_encrypt(text, key)
    rows = []

    start = time.perf_counter()
    guess_key = cracker.frequency_guess(ciphertext, lang)
    guess_plain = cipher.substitution_decrypt(ciphertext, guess_key)
    rows.append(
        {
            "method": "guess",
            "accuracy": char_accuracy(guess_plain, text),
            "seconds": time.perf_counter() - start,
        }
    )

    start = time.perf_counter()
    _, hill_plain, _ = cracker.hill_climb(ciphertext, lang, seed=seed)
    rows.append(
        {
            "method": "hill",
            "accuracy": char_accuracy(hill_plain, text),
            "seconds": time.perf_counter() - start,
        }
    )
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    """Rata-rata akurasi dan waktu per (lang, length, method)."""
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        groups.setdefault((row["lang"], row["length"], row["method"]), []).append(row)
    summary = []
    for (lang, length, method), group in sorted(groups.items()):
        summary.append(
            {
                "lang": lang,
                "length": length,
                "method": method,
                "mean_accuracy": sum(r["accuracy"] for r in group) / len(group),
                "mean_seconds": sum(r["seconds"] for r in group) / len(group),
                "n": len(group),
            }
        )
    return summary


def save_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    """Simpan baris ke CSV."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def save_plot(summary: list[dict], path: Path) -> None:
    """Grafik akurasi rata-rata vs panjang teks (dua subplot bahasa)."""
    names = {"guess": "Tebakan frekuensi", "hill": "Hill climbing"}
    titles = {"id": "Bahasa Indonesia", "en": "Bahasa Inggris"}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, lang in zip(axes, LANGS):
        for method in METHODS:
            points = sorted(
                (s["length"], s["mean_accuracy"])
                for s in summary
                if s["lang"] == lang and s["method"] == method
            )
            ax.plot(
                [p[0] for p in points],
                [p[1] for p in points],
                marker="o",
                label=names[method],
            )
        ax.set_title(titles[lang])
        ax.set_xlabel("Panjang teks (huruf)")
        ax.set_xscale("log")
        ax.set_xticks(LENGTHS)
        ax.set_xticklabels([str(v) for v in LENGTHS])
        ax.grid(True, linestyle="--", alpha=0.5)
    axes[0].set_ylabel("Akurasi rata-rata")
    axes[0].set_ylim(0.0, 1.05)
    axes[1].legend()
    fig.suptitle("Akurasi rata-rata vs Panjang teks")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Urai argumen baris perintah."""
    parser = argparse.ArgumentParser(description="Evaluasi akurasi pemecahan cipher.")
    parser.add_argument(
        "--quick", action="store_true", help="Versi kecil (N=3) untuk pengujian."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Titik masuk skrip."""
    args = parse_args(argv)
    n = 3 if args.quick else 20
    rows = []
    for lang_idx, lang in enumerate(LANGS):
        path = SAMPLES_DIR / f"holdout_{lang}.txt"
        if not path.is_file():
            print(f"File holdout tidak ditemukan: {path}", file=sys.stderr)
            return 1
        sentences = path.read_text(encoding="utf-8").splitlines()
        counts = [letter_count(s) for s in sentences]
        prefix = [0]
        for c in counts:
            prefix.append(prefix[-1] + c)
        for length in LENGTHS:
            for i in range(n):
                seed = lang_idx * 1_000_000 + length * 1_000 + i
                text = take_sample(sentences, counts, prefix, length, i, n)
                for result in evaluate_sample(text, lang, seed):
                    rows.append(
                        {"lang": lang, "length": length, "seed": seed, **result}
                    )
            print(f"Selesai: {lang} {length} huruf ({n} sampel)", flush=True)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    save_csv(
        RESULTS_DIR / "evaluation.csv",
        rows,
        ["lang", "length", "seed", "method", "accuracy", "seconds"],
    )
    summary = summarize(rows)
    save_csv(
        RESULTS_DIR / "summary.csv",
        summary,
        ["lang", "length", "method", "mean_accuracy", "mean_seconds", "n"],
    )
    save_plot(summary, RESULTS_DIR / "accuracy_vs_length.png")
    print(
        "Tersimpan: results/evaluation.csv, results/summary.csv, results/accuracy_vs_length.png"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
