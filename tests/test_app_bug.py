"""Tes untuk bug selectbox ALPHABET di tab 3."""

import streamlit as st
from src.cipher import ALPHABET


def test_alphabet_is_list_or_convertible():
    """ALPHABET harus bisa dikonversi ke list 26 elemen."""
    alpha_list = list(ALPHABET)
    assert len(alpha_list) == 26
    assert alpha_list[0] == "A"
    assert alpha_list[25] == "Z"


def test_selectbox_index_bounds():
    """Index 0 dan 1 harus valid untuk selectbox dengan ALPHABET."""
    alpha_list = list(ALPHABET)
    assert 0 < len(alpha_list)  # index=0 valid
    assert 1 < len(alpha_list)  # index=1 valid
