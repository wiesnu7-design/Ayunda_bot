"""
main.py - RECEPTION (Ringan & Clean)

KAMAR-KAMAR architecture:
  KAMAR 1 → Local Logic  (hitung NPK + curhat)
  KAMAR 2 → Dialogflow   (TUTUP, dibuka week 2)
  KAMAR 3 → Response Formatter
"""
import os
import re

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load TOKEN dari .env (AMAN - jangan hard-code!)
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ============================================================
# IMPORT LOGIC
# ============================================================
from logic.ayunda_personality import AyundaPersonality
from logic.hitung_npk import HitungNPK
from logic.response_formatter import format_with_personality

# ============================================================
# INITIALIZE
# ============================================================
hitung_npk = HitungNPK("data/gudang_pupuk.json")
ayunda = AyundaPersonality("data/gudang_fat.json")

# ============================================================
# HELPERS
# ============================================================

def _extract_total_kg(user_input: str) -> int | None:
    """Ambil angka kg dari teks, contoh: '100kg' → 100."""
    match = re.search(r"(\d+)\s*kg", user_input.lower())
    return int(match.group(1)) if match else None


# ============================================================
# HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """KAMAR 1: Greeting awal."""
    greeting = ayunda.get_greeting()
    await update.message.reply_text(greeting)


async def cmd_teman(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set mode ke teman (default)."""
    context.user_data["mode"] = "teman"
    await update.message.reply_text(
        "Mode *teman* aktif! 🤗 Ayunda siap jadi teman setia kamu~",
        parse_mode="Markdown",
    )


async def cmd_pacar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set mode ke pacar (Sunda style, hangat & bucin tipis)."""
    context.user_data["mode"] = "pacar"
    await update.message.reply_text(
        "Mode *pacar* aktif! 💕 Ayunda disini, Akang~ Cerita aja ya~",
        parse_mode="Markdown",
    )


async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tampilkan mode aktif + cara ganti."""
    mode = context.user_data.get("mode", "teman")
    if mode == "pacar":
        desc = "pacar 💕 (Sunda style, bucin tipis)"
    else:
        desc = "teman 🤗 (default)"
    await update.message.reply_text(
        f"Mode Ayunda kamu sekarang: *{desc}*\n\n"
        "Cara ganti mode:\n"
        "• /teman → mode teman (default)\n"
        "• /pacar → mode pacar (Sunda style)",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """MAIN HANDLER — routing ke kamar-kamar."""
    user_input = update.message.text
    mode = context.user_data.get("mode", "teman")

    # ========== KAMAR 1A: Curhat (keyword match) ==========
    keyword_result = ayunda.detect_keyword(user_input)
    if keyword_result:
        kategori, sub_kategori = keyword_result
        respon = ayunda.get_respon(kategori, sub_kategori)
        response = format_with_personality(respon, mode=mode)
        await update.message.reply_text(response)
        return

    # ========== KAMAR 1B: Hitung NPK ==========
    npk_keywords = ["npk", "hitung", "buatkan", "formula", "pupuk"]
    if any(word in user_input.lower() for word in npk_keywords):
        npk_data = hitung_npk.parse_npk_input(user_input)
        if npk_data:
            total_kg = _extract_total_kg(user_input) or 100
            hasil = hitung_npk.hitung_reverse_npk(
                npk_data["N"], npk_data["P"], npk_data["K"], total_kg
            )
            respon = hitung_npk.format_hasil_reverse_npk(hasil)
            response = format_with_personality(respon, mode=mode)
            await update.message.reply_text(response, parse_mode="Markdown")
            return

    # ========== KAMAR 2: Dialogflow Bridge (TUTUP - week 2) ==========
    # TODO: integrate ZSNBot / Dialogflow di sini

    # ========== KAMAR 3: Default / warm response ==========
    if mode == "pacar":
        default = ayunda.get_respon("interaksi_hangat_pacar")
    else:
        default = ayunda.get_respon("interaksi_hangat")
    response = format_with_personality(default, mode=mode)
    await update.message.reply_text(response)


# ============================================================
# BUILD & RUN
# ============================================================
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("TOKEN tidak ditemukan! Buat file .env dengan TOKEN=<token_kamu>")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teman", cmd_teman))
    app.add_handler(CommandHandler("pacar", cmd_pacar))
    app.add_handler(CommandHandler("mode", cmd_mode))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🎀 Ayunda Bot Running... 💚")
    app.run_polling()
