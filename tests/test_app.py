"""Tes untuk fungsi pembantu antarmuka Streamlit (src/app.py)."""

from src.app import SAMPLE_TEXTS, apply_mapping
from src.cipher import ALPHABET


def test_apply_mapping_identity():
    identity = {ch: ch for ch in ALPHABET}
    text = "Halo, Dunia! 123"
    assert apply_mapping(text, identity) == text


def test_apply_mapping_custom():
    mapping = {ch: ch for ch in ALPHABET}
    mapping["A"] = "X"
    mapping["B"] = "Y"
    assert apply_mapping("Abc", mapping) == "Xyc"


def test_sample_texts_not_empty():
    assert len(SAMPLE_TEXTS["Indonesia"]) > 50
    assert len(SAMPLE_TEXTS["Inggris"]) > 50
