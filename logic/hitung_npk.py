"""
KAMAR 1 - Otak Hitung NPK
HitungNPK: Logic perhitungan formula pupuk NPK
"""
import json
import re


class HitungNPK:
    def __init__(self, gudang_path: str = "data/gudang_pupuk.json"):
        with open(gudang_path, "r", encoding="utf-8") as f:
            gudang = json.load(f)
        # Gabungkan bahan_utama & bahan_tambahan ke satu dict
        self.bahan = {}
        self.bahan.update(gudang.get("bahan_utama", {}))
        self.bahan.update(gudang.get("bahan_tambahan", {}))

    # ------------------------------------------------------------------
    # 1. Parse input user - abaikan typo / variasi penulisan
    # ------------------------------------------------------------------
    def parse_npk_input(self, user_input: str) -> dict | None:
        """
        Coba baca angka N-P-K dari teks bebas.
        Contoh yang dikenali:
          "NPK 15-15-15", "npk 10 10 10", "buat npk 16:16:16 100kg"
        Returns dict {'N': int, 'P': int, 'K': int} atau None jika gagal.
        """
        # Coba pola angka-angka-angka (pisah -, :, spasi)
        pattern = r"(\d+)\s*[-:,\s]\s*(\d+)\s*[-:,\s]\s*(\d+)"
        match = re.search(pattern, user_input)
        if match:
            return {
                "N": int(match.group(1)),
                "P": int(match.group(2)),
                "K": int(match.group(3)),
            }
        return None

    # ------------------------------------------------------------------
    # 2. Hitung bahan dari NPK target (Reverse NPK)
    # ------------------------------------------------------------------
    def hitung_reverse_npk(
        self, n_target: float, p_target: float, k_target: float, total_kg: float = 100
    ) -> dict:
        """
        Hitung berapa kg setiap bahan untuk memenuhi target NPK
        dalam total_kg pupuk campuran.

        Asumsi urutan prioritas bahan: Urea → TSP/SP-36 → KCl → Pupuk Organik
        Zeolit wajib 45% jika masuk kategori Pembenah Tanah.
        """
        kategori = self.kategorisasi_npk(n_target, p_target, k_target)

        hasil = {}
        sisa_kg = total_kg

        # Khusus Pembenah Tanah: zeolit 45%
        if kategori == "Pembenah Tanah":
            zeolit_kg = round(total_kg * 0.45, 2)
            hasil["Zeolit"] = zeolit_kg
            sisa_kg -= zeolit_kg

        # Hitung kebutuhan N (dari Urea, 46% N)
        if n_target > 0:
            urea_kg = round((n_target / 100) * total_kg / (self.bahan["Urea"]["N"] / 100), 2)
            urea_kg = min(urea_kg, sisa_kg)
            hasil["Urea"] = urea_kg
            sisa_kg -= urea_kg

        # Hitung kebutuhan P (dari TSP, 36% P)
        if p_target > 0:
            tsp_kg = round((p_target / 100) * total_kg / (self.bahan["TSP"]["P"] / 100), 2)
            tsp_kg = min(tsp_kg, sisa_kg)
            hasil["TSP"] = tsp_kg
            sisa_kg -= tsp_kg

        # Hitung kebutuhan K (dari KCl, 60% K)
        if k_target > 0:
            kcl_kg = round((k_target / 100) * total_kg / (self.bahan["KCl"]["K"] / 100), 2)
            kcl_kg = min(kcl_kg, sisa_kg)
            hasil["KCl"] = kcl_kg
            sisa_kg -= kcl_kg

        # Sisa → Pupuk Organik
        if sisa_kg > 0:
            hasil["Pupuk Organik"] = round(sisa_kg, 2)

        hasil["_kategori"] = kategori
        hasil["_total_kg"] = total_kg
        return hasil

    # ------------------------------------------------------------------
    # 3. Analisa bahan (input kg bahan → output kandungan NPK)
    # ------------------------------------------------------------------
    def hitung_analisa_bahan(self, bahan_input: dict) -> dict:
        """
        bahan_input: {'Urea': 20, 'TSP': 15, 'KCl': 10, ...} (dalam kg)
        Returns: {'N': float, 'P': float, 'K': float, 'total_kg': float}
        """
        total_kg = sum(bahan_input.values())
        if total_kg == 0:
            return {"N": 0, "P": 0, "K": 0, "total_kg": 0}

        n_total = p_total = k_total = 0.0
        for nama_bahan, kg in bahan_input.items():
            info = self.bahan.get(nama_bahan)
            if info:
                n_total += (info["N"] / 100) * kg
                p_total += (info["P"] / 100) * kg
                k_total += (info["K"] / 100) * kg

        return {
            "N": round((n_total / total_kg) * 100, 2),
            "P": round((p_total / total_kg) * 100, 2),
            "K": round((k_total / total_kg) * 100, 2),
            "total_kg": total_kg,
        }

    # ------------------------------------------------------------------
    # 4. Kategorisasi NPK ke 4 stage
    # ------------------------------------------------------------------
    def kategorisasi_npk(self, n: float, p: float, k: float) -> str:
        """
        4 kategori berdasarkan nilai N-P-K:
          - Pembenah Tanah : semua ≤ 4 (≤4-4-4)
          - Vegetative      : N paling tinggi
          - Generative      : P dan K tinggi (P+K > N)
          - Finishing       : K paling tinggi dari ketiganya
        """
        if n <= 4 and p <= 4 and k <= 4:
            return "Pembenah Tanah"
        if k > n and k > p:
            return "Finishing"
        if (p + k) > n:
            return "Generative"
        return "Vegetative"

    # ------------------------------------------------------------------
    # 5. Format hasil reverse NPK
    # ------------------------------------------------------------------
    def format_hasil_reverse_npk(self, hasil: dict) -> str:
        """Ubah dict hasil hitung menjadi teks siap kirim."""
        kategori = hasil.get("_kategori", "-")
        total_kg = hasil.get("_total_kg", 100)

        lines = [
            f"🧮 *Hasil Hitung NPK* ({total_kg} kg)",
            f"📊 Kategori: *{kategori}*",
            "",
            "📦 *Komposisi Bahan:*",
        ]
        bahan_items = {k: v for k, v in hasil.items() if not k.startswith("_")}
        for nama, kg in bahan_items.items():
            lines.append(f"  • {nama}: *{kg} kg*")

        lines += [
            "",
            "✅ Pastikan ditimbang dengan benar ya bray~ 🌱",
        ]
        return "\n".join(lines)
