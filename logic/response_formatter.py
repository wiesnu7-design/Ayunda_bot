"""
KAMAR 3 - Response Formatter
Tambah emoji & warm tone sesuai mode yang dipilih
"""
import random

MODE_CONFIG = {
    "santai": {
        "prefix": "",
        "suffix": " 😊",
        "emoji_filler": ["~", "✨", "🌸"],
    },
    "excited": {
        "prefix": "🎉 ",
        "suffix": " 🚀",
        "emoji_filler": ["!", "🌟", "💪"],
    },
    "gentle": {
        "prefix": "",
        "suffix": " 🌿",
        "emoji_filler": ["~", "💚", "🌱"],
    },
    "galau": {
        "prefix": "",
        "suffix": " 😔",
        "emoji_filler": ["...", "🥺", "💙"],
    },
    "teman": {
        "prefix": "",
        "suffix": " 🤗",
        "emoji_filler": ["~", "😄", "🌸"],
    },
    "pacar": {
        # address: list of Sunda-style terms — one is picked randomly per reply
        "address": ["Akang", "Aa", "A'a", "Aang", "Ang"],
        "suffix": " 💕",
        "emoji_filler": ["~", "🌸", "💞"],
    },
}

DEFAULT_MODE = "santai"


def format_with_personality(text: str, mode: str = DEFAULT_MODE) -> str:
    """
    Tambah prefix / suffix sesuai mode ke teks yang diberikan.
    Mode yang tersedia: santai, excited, gentle, galau, teman, pacar
    Mode pacar: Sunda style (akang/aa/a'a/aang/ang), hangat & bucin tipis.
    """
    config = MODE_CONFIG.get(mode, MODE_CONFIG[DEFAULT_MODE])

    # Modes with a random address list use a randomly chosen address as prefix
    address_list = config.get("address")
    if address_list:
        prefix = f"{random.choice(address_list)}~ "
    else:
        prefix = config.get("prefix", "")

    formatted = f"{prefix}{text}{config['suffix']}"
    return formatted
