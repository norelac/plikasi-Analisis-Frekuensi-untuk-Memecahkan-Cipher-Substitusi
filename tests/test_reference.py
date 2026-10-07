"""Tes untuk M1: pembangunan dan pemuatan referensi frekuensi."""

import importlib.util
import json
import math
import string
from pathlib import Path

import pytest

from src import reference

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"


def load_build_module():
    """Muat scripts/build_reference.py sebagai modul tanpa side effect."""
    spec = importlib.util.spec_from_file_location(
        "build_reference", SCRIPTS_DIR / "build_reference.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


br = load_build_module()


def test_clean_text_keeps_only_a_z():
    assert br.clean_text("Halo, Dunia! 123") == "HALODUNIA"


def test_read_sentences_leipzig(tmp_path):
    corpus = tmp_path / "c.txt"
    corpus.write_text("1\tHalo dunia\n2\tApa kabar?\n", encoding="utf-8")
    assert br.read_sentences(corpus, "leipzig") == ["Halo dunia", "Apa kabar?"]


def test_read_sentences_plain(tmp_path):
    corpus = tmp_path / "c.txt"
    corpus.write_text("Baris satu\n\nBaris dua\n", encoding="utf-8")
    assert br.read_sentences(corpus, "plain") == ["Baris satu", "Baris dua"]


def test_split_holdout_last_ten_percent():
    sentences = [f"kalimat {i}" for i in range(100)]
    train, holdout = br.split_holdout(sentences)
    assert len(train) == 90
    assert holdout == sentences[90:]


def test_build_reference_structure_and_sums():
    ref = br.build_reference(["ABAB", "BC"], "en")
    assert ref["lang"] == "en"
    assert set(ref["unigram"]) == set(string.ascii_uppercase)
    assert sum(ref["unigram"].values()) == pytest.approx(100.0)
    assert len(ref["bigram"]) == 26**2
    assert len(ref["trigram"]) == 26**3
    assert all(v <= 0.0 for v in ref["bigram"].values())
    assert all(math.isfinite(v) for v in ref["trigram"].values())


def test_build_reference_empty_raises():
    with pytest.raises(ValueError):
        br.build_reference(["123 !!!"], "id")


def test_main_end_to_end_plain(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(
        "\n".join(f"kalimat contoh nomor {i}" for i in range(50)) + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "ref.json"
    holdout = tmp_path / "holdout.txt"
    assert (
        br.main(
            [
                "--corpus",
                str(corpus),
                "--lang",
                "id",
                "--format",
                "plain",
                "--out",
                str(out),
                "--holdout",
                str(holdout),
            ]
        )
        == 0
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    reference.validate_reference(data)
    assert len(holdout.read_text(encoding="utf-8").splitlines()) == 5


def test_main_missing_corpus(tmp_path):
    assert (
        br.main(
            [
                "--corpus",
                str(tmp_path / "tidak_ada.txt"),
                "--lang",
                "id",
                "--out",
                str(tmp_path / "ref.json"),
            ]
        )
        == 1
    )


def test_reference_path_rejects_unknown_lang():
    with pytest.raises(ValueError):
        reference.reference_path("fr")


def test_validate_reference_rejects_bad_data():
    with pytest.raises(ValueError):
        reference.validate_reference({"lang": "en"})
    with pytest.raises(ValueError):
        reference.validate_reference(
            {"lang": "en", "unigram": {"A": 100.0}, "bigram": {}, "trigram": {}}
        )


def test_validate_reference_rejects_positive_logprob():
    valid = reference.load_reference("en")
    corrupt = json.loads(json.dumps(valid))
    corrupt["bigram"]["AA"] = 1.5
    with pytest.raises(ValueError, match="non-positif"):
        reference.validate_reference(corrupt)
    corrupt["bigram"]["AA"] = -1.0
    corrupt["trigram"]["AAA"] = 0.5
    with pytest.raises(ValueError, match="non-positif"):
        reference.validate_reference(corrupt)
