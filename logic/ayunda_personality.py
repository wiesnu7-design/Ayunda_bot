"""
KAMAR 1 - Otak Curhat Ayunda
AyundaPersonality: Load gudang_fat.json & provide responses
"""
import json
import random


class AyundaPersonality:
    KEYWORD_MAP = {
        # Curhat tanaman
        "layu": ("curhat_tanaman", "layu"),
        "kuning": ("curhat_tanaman", "kuning"),
        "busuk": ("curhat_tanaman", "busuk"),
        "tidak berbuah": ("curhat_tanaman", "tidak_berbuah"),
        "gak berbuah": ("curhat_tanaman", "tidak_berbuah"),
        "ga berbuah": ("curhat_tanaman", "tidak_berbuah"),
        # Curhat user
        "sedih": ("curhat_user", "sedih"),
        "galau": ("curhat_user", "sedih"),
        "stress": ("curhat_user", "stress"),
        "stres": ("curhat_user", "stress"),
        "pacar": ("curhat_user", "pacar"),
        "gebetan": ("curhat_user", "pacar"),
        "uang": ("curhat_user", "uang"),
        "duit": ("curhat_user", "uang"),
        "bokek": ("curhat_user", "uang"),
    }

    def __init__(self, gudang_path: str = "data/gudang_fat.json"):
        with open(gudang_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    # ------------------------------------------------------------------
    # Ambil respon random berdasarkan kategori & sub_kategori
    # ------------------------------------------------------------------
    def get_respon(self, kategori: str, sub_kategori: str | None = None) -> str:
        """
        Ambil satu respon random dari gudang_fat.json.
        Jika sub_kategori None → ambil dari list langsung.
        """
        pool = self.data.get(kategori)
        if pool is None:
            return "Hehe Ayunda bingung bray 😅"

        if sub_kategori:
            pool = pool.get(sub_kategori)
            if not pool:
                return "Ayunda dengerin bray 😊"

        if isinstance(pool, list):
            return random.choice(pool)
        return str(pool)

    # ------------------------------------------------------------------
    # Detect keyword dari input user
    # ------------------------------------------------------------------
    def detect_keyword(self, user_input: str) -> tuple[str, str] | None:
        """
        Returns (kategori, sub_kategori) jika keyword ditemukan,
        None jika tidak ada yang cocok.
        """
        text = user_input.lower()
        for keyword, mapping in self.KEYWORD_MAP.items():
            if keyword in text:
                return mapping
        return None

    # ------------------------------------------------------------------
    # Greeting
    # ------------------------------------------------------------------
    def get_greeting(self) -> str:
        return self.get_respon("greeting")
