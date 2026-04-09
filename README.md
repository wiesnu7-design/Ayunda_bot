# 🎀 Ayunda Bot — Tukang Hitung NPK

Bot Telegram cerdas untuk pertanian:
- 🧮 **Hitung NPK** — Reverse formula & analisa bahan pupuk
- 💚 **Curhat santai** — Diagnosa tanaman & ngobrol hangat
- 🌱 **Dialogflow Bridge** *(coming week 2)*

---

## Struktur Proyek

```
AyundaBot/
├── main.py                  # RECEPTION - router & handler (ringan!)
├── .env                     # TOKEN Telegram (jangan di-push!)
├── .env.example             # Template .env
├── .gitignore
├── requirements.txt
├── README.md
├── logic/
│   ├── __init__.py
│   ├── hitung_npk.py        # KAMAR 1 - otak hitung NPK
│   ├── ayunda_personality.py# KAMAR 1 - otak curhat santai
│   └── response_formatter.py# KAMAR 3 - formatter response
└── data/
    ├── gudang_pupuk.json    # Data bahan & kandungan NPK
    └── gudang_fat.json      # Respon santai Ayunda (GENDUT!)
```

---

## Setup

1. **Clone repo & masuk folder:**
   ```bash
   git clone https://github.com/wiesnu7-design/Ayunda_bot.git
   cd Ayunda_bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Buat file `.env`** (jangan di-push!):
   ```
   TOKEN=token_telegram_bot_kamu
   ```

4. **Jalankan bot:**
   ```bash
   python main.py
   ```

---

## Fitur

| Keyword | Kamar | Contoh |
|---------|-------|--------|
| `npk`, `hitung`, `formula` | KAMAR 1 - Hitung NPK | "hitung npk 15-15-15 100kg" |
| `layu`, `kuning`, `busuk` | KAMAR 1 - Curhat Tanaman | "tanaman saya layu bray" |
| `sedih`, `stress`, `uang` | KAMAR 1 - Curhat User | "lagi stress bray" |
| Lainnya | KAMAR 3 - Default | respon hangat Ayunda |

---

## Kategori NPK

| Kategori | Kondisi |
|----------|---------|
| Pembenah Tanah | N≤4, P≤4, K≤4 — wajib Zeolit 45% |
| Vegetative | N paling tinggi |
| Generative | P+K > N |
| Finishing | K paling tinggi |

---

*Made with 💚 by Ayunda Bot*
