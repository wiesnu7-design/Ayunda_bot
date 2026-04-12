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
          "sp36 kosong npk 16-16-16" → flag sp36_kosong=True
        Returns dict {'N': int, 'P': int, 'K': int, 'sp36_kosong': bool}
        atau None jika tidak ada pola NPK yang ditemukan.
        """
        sp36_kosong = bool(re.search(r"sp[\s\-]?36\s+kosong", user_input, re.IGNORECASE))

        # Coba pola angka-angka-angka (pisah -, :, spasi)
        pattern = r"(\d+)\s*[-:,\s]\s*(\d+)\s*[-:,\s]\s*(\d+)"
        match = re.search(pattern, user_input)
        if match:
            return {
                "N": int(match.group(1)),
                "P": int(match.group(2)),
                "K": int(match.group(3)),
                "sp36_kosong": sp36_kosong,
            }
        return None

    # ------------------------------------------------------------------
    # 2. Hitung bahan dari NPK target (Reverse NPK)
    # ------------------------------------------------------------------
    def _pilih_sumber_p(self, sp36_kosong: bool) -> str | None:
        """
        Pilih nama bahan sumber P yang tersedia di gudang.
        sp36_kosong=False : coba SP-36 → TSP → DAP → MAP → UltraDAP → Phertipos
        sp36_kosong=True  : skip SP-36/TSP, coba DAP → MAP → UltraDAP → Phertipos
        """
        if sp36_kosong:
            prioritas = ["DAP", "MAP", "UltraDAP", "Phertipos"]
        else:
            prioritas = ["SP-36", "TSP", "DAP", "MAP", "UltraDAP", "Phertipos"]
        for nama in prioritas:
            if nama in self.bahan and self.bahan[nama].get("P", 0) > 0:
                return nama
        return None

    def hitung_reverse_npk(
        self,
        n_target: float,
        p_target: float,
        k_target: float,
        total_kg: float = 100,
        sp36_kosong: bool = False,
    ) -> dict:
        """
        Hitung berapa kg setiap bahan untuk memenuhi target NPK
        dalam total_kg pupuk campuran.

        Asumsi urutan prioritas bahan: P-source → Urea → KCl → Pupuk Organik
        (P dihitung lebih dulu agar kontribusi N dari DAP/MAP/UltraDAP bisa
        dikurangkan dari kebutuhan Urea, sehingga N tidak dobel.)
        Zeolit wajib 45% jika masuk kategori Pembenah Tanah.
        """
        kategori = self.kategorisasi_npk(n_target, p_target, k_target)

        hasil = {}
        sisa_kg = total_kg
        p_source_name = None
        p_source_n_contribution = 0.0

        # Khusus Pembenah Tanah: zeolit 45%
        if kategori == "Pembenah Tanah":
            zeolit_kg = round(total_kg * 0.45, 2)
            hasil["Zeolit"] = zeolit_kg
            sisa_kg -= zeolit_kg

        # Hitung kebutuhan P terlebih dulu (biar tahu kontribusi N dari sumber P)
        if p_target > 0:
            p_source_name = self._pilih_sumber_p(sp36_kosong)
            if p_source_name:
                p_pct = self.bahan[p_source_name]["P"] / 100
                p_source_kg = round((p_target / 100) * total_kg / p_pct, 2)
                p_source_kg = min(p_source_kg, sisa_kg)
                hasil[p_source_name] = p_source_kg
                sisa_kg -= p_source_kg
                # Hitung kontribusi N dari sumber P (misal DAP/MAP punya N)
                p_source_n_pct = self.bahan[p_source_name].get("N", 0) / 100
                p_source_n_contribution = p_source_kg * p_source_n_pct
            # Tandai jika tidak ada sumber P
            if p_source_name is None:
                hasil["_no_p_source"] = True

        # Hitung kebutuhan N (dari Urea), kurangi kontribusi N dari sumber P
        if n_target > 0:
            urea_n_needed = (n_target / 100) * total_kg - p_source_n_contribution
            if urea_n_needed > 0:
                urea_kg = round(urea_n_needed / (self.bahan["Urea"]["N"] / 100), 2)
                urea_kg = min(urea_kg, sisa_kg)
                hasil["Urea"] = urea_kg
                sisa_kg -= urea_kg

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
        hasil["_p_source"] = p_source_name
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
        p_source = hasil.get("_p_source")
        no_p_source = hasil.get("_no_p_source", False)

        lines = [
            f"🧮 *Hasil Hitung NPK* ({total_kg} kg)",
            f"📊 Kategori: *{kategori}*",
            "",
            "📦 *Komposisi Bahan:*",
        ]
        bahan_items = {k: v for k, v in hasil.items() if not k.startswith("_")}
        for nama, kg in bahan_items.items():
            lines.append(f"  • {nama}: *{kg} kg*")

        if p_source:
            lines.append(f"\n💡 Sumber P dipakai: *{p_source}* (P = P₂O₅ label pasar)")
        elif no_p_source:
            lines.append("\n⚠️ *Tidak ada sumber P tersedia di gudang.* Periksa stok sumber P (DAP/MAP/SP-36/TSP/UltraDAP/Phertipos) ya bray~")

        lines += [
            "",
            "✅ Pastikan ditimbang dengan benar ya bray~ 🌱",
        ]
        return "\n".join(lines)
