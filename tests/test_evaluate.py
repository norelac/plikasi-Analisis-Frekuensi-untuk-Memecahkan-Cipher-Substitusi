"""Tes untuk M5: helper evaluasi (tanpa hill climbing, cepat)."""

import importlib.util
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"


def load_evaluate_module():
    """Muat scripts/evaluate.py sebagai modul tanpa side effect."""
    spec = importlib.util.spec_from_file_location(
        "evaluate", SCRIPTS_DIR / "evaluate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ev = load_evaluate_module()

SENTENCES = [
    "Kemerdekaan Indonesia diproklamasikan",
    "pada tanggal tujuh belas Agustus",
    "seribu sembilan ratus empat puluh lima",
    "oleh Soekarno dan Hatta di Jakarta",
]


def _index():
    counts = [ev.letter_count(s) for s in SENTENCES]
    prefix = [0]
    for c in counts:
        prefix.append(prefix[-1] + c)
    return counts, prefix


def test_char_accuracy_perfect_and_partial():
    assert ev.char_accuracy("ABC", "abc") == 1.0
    # Manual: 2 dari 3 huruf benar -> 0,6667.
    assert ev.char_accuracy("ABA", "ABC") == 2 / 3


def test_take_sample_meets_target_and_deterministic():
    counts, prefix = _index()
    first = ev.take_sample(SENTENCES, counts, prefix, 50, 0, 4)
    assert ev.letter_count(first) >= 50
    assert first == ev.take_sample(SENTENCES, counts, prefix, 50, 0, 4)


def test_take_sample_starts_differ():
    numbered = [f"kalimat contoh nomor {i} untuk pengujian" for i in range(200)]
    counts = [ev.letter_count(s) for s in numbered]
    prefix = [0]
    for c in counts:
        prefix.append(prefix[-1] + c)
    samples = {ev.take_sample(numbered, counts, prefix, 20, i, 4) for i in range(4)}
    assert len(samples) == 4


def test_summarize_averages():
    rows = [
        {"lang": "id", "length": 50, "method": "hill", "accuracy": 1.0, "seconds": 2.0},
        {"lang": "id", "length": 50, "method": "hill", "accuracy": 0.5, "seconds": 4.0},
    ]
    (summary,) = ev.summarize(rows)
    assert summary["mean_accuracy"] == 0.75
    assert summary["mean_seconds"] == 3.0
    assert summary["n"] == 2
