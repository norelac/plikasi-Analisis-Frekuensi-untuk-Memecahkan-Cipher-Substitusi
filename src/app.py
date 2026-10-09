"""Aplikasi Analisis Frekuensi untuk Memecahkan Cipher Substitusi.

Streamlit web app dengan antarmuka Bahasa Indonesia.
"""

import sys
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src import analysis, cipher, cracker
from src.cipher import ALPHABET as ALPHABET_STR
from src.reference import load_reference

SAMPLE_TEXTS = {
    "Indonesia": (
        "Kami bangsa Indonesia dengan ini menjatuhkan dan menyatakan kemerdekaan Indonesia. "
        "Hal-hal yang mengenai pemindahan kekuasaan dan lain-lain diselenggarakan dengan "
        "cara seksama dan dalam tempo yang sesingkat-singkatnya. Jakarta, tujuh belas Agustus "
        "seribu sembilan ratus empat puluh lima atas nama bangsa Indonesia Soekarno Hatta."
    ),
    "Inggris": (
        "The quick brown fox jumps over the lazy dog and runs across the wide open fields. "
        "Statistical frequency analysis demonstrates that natural language possesses unmistakable "
        "structural patterns which leak information through monoalphabetic substitution ciphers."
    ),
}

ALPHABET = tuple(ALPHABET_STR)  # Konversi ke tuple untuk kompatibilitas Streamlit selectbox


def init_session_state() -> None:
    """Inisialisasi state sesi jika belum ada."""
    if "input_text" not in st.session_state:
        st.session_state.input_text = SAMPLE_TEXTS["Indonesia"]
    if "ciphertext" not in st.session_state:
        st.session_state.ciphertext = ""
    if "cipher_to_plain" not in st.session_state:
        st.session_state.cipher_to_plain = {ch: ch for ch in ALPHABET}
    if "selected_lang" not in st.session_state:
        st.session_state.selected_lang = "id"


def apply_mapping(ciphertext: str, mapping: dict[str, str]) -> str:
    """Dekripsi teks menggunakan kamus pemetaan cipher -> plain."""
    res = []
    for ch in ciphertext:
        if "A" <= ch <= "Z":
            res.append(mapping.get(ch, ch))
        elif "a" <= ch <= "z":
            res.append(mapping.get(ch.upper(), ch.upper()).lower())
        else:
            res.append(ch)
    return "".join(res)


def set_mapping_from_key(key_str: str) -> None:
    """Perbarui pemetaan session state dari encryption key format cipher.py."""
    dec = cracker._to_dec(key_str)
    st.session_state.cipher_to_plain = {
        chr(65 + c_idx): chr(65 + p_idx) for c_idx, p_idx in enumerate(dec)
    }


def main() -> None:
    st.set_page_config(
        page_title="Analisis Frekuensi Cipher Substitusi",
        page_icon="🔐",
        layout="wide",
    )
    init_session_state()

    st.title("🔐 Analisis Frekuensi Cipher Substitusi")
    st.caption("Aplikasi Pemecah Cipher Substitusi (Caesar & Monoalfabetik)")

    # Contoh Teks Cepat di Sidebar atau Header
    with st.expander("📝 Muat Contoh Teks"):
        col_s1, col_s2 = st.columns(2)
        if col_s1.button("Muat Contoh Teks Indonesia"):
            st.session_state.input_text = SAMPLE_TEXTS["Indonesia"]
            st.session_state.selected_lang = "id"
            st.rerun()
        if col_s2.button("Muat Contoh Teks Inggris"):
            st.session_state.input_text = SAMPLE_TEXTS["Inggris"]
            st.session_state.selected_lang = "en"
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["1. Enkripsi", "2. Analisis Frekuensi", "3. Pecahkan Cipher", "4. Evaluasi"]
    )

    # ---------------- TAB 1: ENKRIPSI ----------------
    with tab1:
        st.header("Enkripsi Teks")
        plain_input = st.text_area(
            "Plaintext:",
            value=st.session_state.input_text,
            height=140,
            key="tab1_plain",
        )
        st.session_state.input_text = plain_input

        cipher_type = st.radio(
            "Pilih Metode Cipher:",
            ["Caesar Cipher", "Substitusi Acak (Monoalfabetik)"],
            horizontal=True,
        )

        curr_key = ""
        if cipher_type == "Caesar Cipher":
            shift = st.slider("Nilai Shift (0 - 25):", 0, 25, 3)
            ct = cipher.caesar_encrypt(plain_input, shift)
            st.info(f"Shift digunakan: **{shift}**")
        else:
            col_k1, col_k2 = st.columns([1, 2])
            seed_val = col_k1.number_input("Seed Acak:", value=42, step=1)
            generated = cipher.generate_key(int(seed_val))
            key_input = col_k2.text_input(
                "Kunci Substitusi (26 huruf):", value=generated
            )
            curr_key = key_input.strip().upper()

            if not cipher.validate_key(curr_key):
                st.error(
                    "Kunci tidak valid! Kunci harus berupa permutasi 26 huruf unik A-Z."
                )
                ct = ""
            else:
                ct = cipher.substitution_encrypt(plain_input, curr_key)
                st.caption(f"Pemetaan kunci: Plain A-Z dipetakan ke -> {curr_key}")

        st.session_state.ciphertext = ct
        st.text_area("Ciphertext Hasil Enkripsi:", value=ct, height=140)

        if st.button("Kirim Ciphertext ke Tab Analisis & Pecahkan"):
            st.success("Ciphertext berhasil dikirim ke Tab 2 dan Tab 3!")

    # ---------------- TAB 2: ANALISIS ----------------
    with tab2:
        st.header("Analisis Frekuensi & Statistik")
        ct_analysis = st.text_area(
            "Ciphertext untuk dianalisis:",
            value=st.session_state.ciphertext or st.session_state.input_text,
            height=120,
            key="tab2_ct",
        )
        col_l1, _ = st.columns(2)
        lang_choice = col_l1.selectbox(
            "Pilih Bahasa Referensi:",
            ["id", "en"],
            index=0 if st.session_state.selected_lang == "id" else 1,
            format_func=lambda x: (
                "Bahasa Indonesia (id)" if x == "id" else "Bahasa Inggris (en)"
            ),
        )
        st.session_state.selected_lang = lang_choice

        ref_data = load_reference(lang_choice)
        ref_unigram = ref_data["unigram"]

        # Metrik
        chi_val = analysis.chi_square(ct_analysis, ref_unigram)
        ic_val = analysis.index_of_coincidence(ct_analysis)
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Index of Coincidence (IC)", f"{ic_val:.4f}")
        col_m2.metric(
            "Chi-Square vs Referensi",
            f"{chi_val:.2f}" if not np.isinf(chi_val) else "Tak hingga",
        )

        st.subheader("Perbandingan Frekuensi Huruf (Ciphertext vs Referensi)")
        ct_freq = analysis.letter_frequencies(ct_analysis)

        # Urutkan menurun berdasarkan frekuensi ciphertext
        sorted_letters = sorted(ALPHABET, key=lambda c: ct_freq[c], reverse=True)
        ct_vals = [ct_freq[c] for c in sorted_letters]
        ref_vals = [ref_unigram[c] for c in sorted_letters]

        fig, ax = plt.subplots(figsize=(12, 4.5))
        x = np.arange(len(sorted_letters))
        width = 0.4
        ax.bar(
            x - width / 2,
            ct_vals,
            width,
            label="Ciphertext",
            color="#1f77b4",
            alpha=0.9,
        )
        ax.bar(
            x + width / 2,
            ref_vals,
            width,
            label=f"Referensi ({lang_choice.upper()})",
            color="#ff7f0e",
            alpha=0.9,
        )
        ax.set_xticks(x)
        ax.set_xticklabels(sorted_letters)
        ax.set_ylabel("Frekuensi (%)")
        ax.set_xlabel("Huruf (diurutkan menurun berdasarkan frekuensi ciphertext)")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        col_ng1, col_ng2 = st.columns(2)
        with col_ng1:
            st.subheader("10 Bigram Teratas")
            top_bi = analysis.top_ngrams(ct_analysis, 2, 10)
            if top_bi:
                df_bi = pd.DataFrame(top_bi, columns=["Bigram", "Jumlah"])
                st.dataframe(df_bi, use_container_width=True)
            else:
                st.caption("Belum cukup karakter untuk menghitung bigram.")
        with col_ng2:
            st.subheader("10 Trigram Teratas")
            top_tri = analysis.top_ngrams(ct_analysis, 3, 10)
            if top_tri:
                df_tri = pd.DataFrame(top_tri, columns=["Trigram", "Jumlah"])
                st.dataframe(df_tri, use_container_width=True)
            else:
                st.caption("Belum cukup karakter untuk menghitung trigram.")

    # ---------------- TAB 3: PECAHKAN ----------------
    with tab3:
        st.header("Pemecahan Cipher (Otomatis & Manual)")
        ct_solve = st.text_area(
            "Ciphertext untuk dipecahkan:",
            value=st.session_state.ciphertext or st.session_state.input_text,
            height=120,
            key="tab3_ct",
        )

        col_b1, col_b2, col_b3 = st.columns(3)
        solve_lang = col_b1.selectbox(
            "Bahasa Target:",
            ["id", "en"],
            index=0 if st.session_state.selected_lang == "id" else 1,
            key="tab3_lang",
        )

        if col_b2.button("⚡ Tebakan Frekuensi"):
            with st.spinner("Menebak pemetaan frekuensi..."):
                guessed_key = cracker.frequency_guess(ct_solve, solve_lang)
                set_mapping_from_key(guessed_key)
                st.success("Tebakan frekuensi diterapkan!")
                st.rerun()

        if col_b3.button("🧗 Jalankan Hill Climbing"):
            with st.spinner("Mengoptimasi dengan Hill Climbing..."):
                best_key, _, score = cracker.hill_climb(
                    ct_solve, solve_lang, restarts=8, max_iter=2000, seed=42
                )
                set_mapping_from_key(best_key)
                st.success(f"Hill Climbing selesai! Skor kecocokan: {score:.1f}")
                st.rerun()

        # Deteksi Bentrok
        plain_values = list(st.session_state.cipher_to_plain.values())
        counts = Counter(plain_values)
        clashes = [ch for ch, count in counts.items() if count > 1]
        if clashes:
            st.warning(
                f"⚠️ Perhatian: Huruf plaintext berikut dipetakan lebih dari sekali (bentrok): **{', '.join(sorted(clashes))}**"
            )

        # Editor Pemetaan Manual & Fitur Tukar
        st.subheader("Editor Pemetaan Huruf (Cipher -> Plain)")
        with st.expander("Pengaturan Pemetaan Manual & Tukar Huruf", expanded=True):
            col_sw1, col_sw2, col_sw3, col_sw4 = st.columns([1, 1, 1, 1])
            c1 = col_sw1.selectbox("Huruf Cipher 1:", ALPHABET, index=0, key="sw_c1")
            c2 = col_sw2.selectbox("Huruf Cipher 2:", ALPHABET, index=1, key="sw_c2")
            if col_sw3.button("🔄 Tukar Dua Huruf"):
                v1 = st.session_state.cipher_to_plain[c1]
                v2 = st.session_state.cipher_to_plain[c2]
                st.session_state.cipher_to_plain[c1] = v2
                st.session_state.cipher_to_plain[c2] = v1
                st.rerun()
            if col_sw4.button("♻️ Reset Pemetaan"):
                st.session_state.cipher_to_plain = {ch: ch for ch in ALPHABET}
                st.rerun()

            # Grid input pemetaan per huruf (6 baris x 4-5 kolom)
            cols = st.columns(13)
            for i, ch in enumerate(ALPHABET[:13]):
                with cols[i]:
                    new_val = st.text_input(
                        f"{ch} ->",
                        value=st.session_state.cipher_to_plain.get(ch, ch),
                        max_chars=1,
                        key=f"map_{ch}",
                    ).upper()
                    if new_val and new_val in ALPHABET:
                        st.session_state.cipher_to_plain[ch] = new_val

            cols_bottom = st.columns(13)
            for i, ch in enumerate(ALPHABET[13:]):
                with cols_bottom[i]:
                    new_val = st.text_input(
                        f"{ch} ->",
                        value=st.session_state.cipher_to_plain.get(ch, ch),
                        max_chars=1,
                        key=f"map_{ch}",
                    ).upper()
                    if new_val and new_val in ALPHABET:
                        st.session_state.cipher_to_plain[ch] = new_val

        # Tampilkan Hasil Dekripsi Berdampingan
        decrypted_text = apply_mapping(ct_solve, st.session_state.cipher_to_plain)
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.subheader("Ciphertext")
            st.text_area("Teks Tersandi:", value=ct_solve, height=220, disabled=True)
        with col_res2:
            st.subheader("Plaintext (Hasil Pemetaan)")
            st.text_area("Teks Terdekripsi:", value=decrypted_text, height=220)

    # ---------------- TAB 4: EVALUASI ----------------
    with tab4:
        st.header("Hasil Evaluasi Akurasi")
        summary_path = ROOT_DIR / "results" / "summary.csv"
        plot_path = ROOT_DIR / "results" / "accuracy_vs_length.png"

        if summary_path.is_file():
            st.subheader("Ringkasan Rata-rata Akurasi & Waktu")
            df_sum = pd.read_csv(summary_path)
            st.dataframe(df_sum, use_container_width=True)
        else:
            st.info(
                "File `results/summary.csv` belum ditemukan. Jalankan `python scripts/evaluate.py` untuk menghasilkan data evaluasi."
            )

        if plot_path.is_file():
            st.subheader("Grafik Akurasi vs Panjang Teks")
            st.image(
                str(plot_path),
                caption="Akurasi rata-rata vs panjang teks (20 sampel per uji)",
            )
        else:
            st.info("Grafik `results/accuracy_vs_length.png` belum tersedia.")


if __name__ == "__main__":
    main()
