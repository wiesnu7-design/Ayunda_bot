"""
KAMAR 3 - Response Formatter
Tambah emoji & warm tone sesuai mode yang dipilih
"""

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
}

DEFAULT_MODE = "santai"


def format_with_personality(text: str, mode: str = DEFAULT_MODE) -> str:
    """
    Tambah prefix / suffix sesuai mode ke teks yang diberikan.
    Mode yang tersedia: santai, excited, gentle, galau, teman
    """
    config = MODE_CONFIG.get(mode, MODE_CONFIG[DEFAULT_MODE])
    formatted = f"{config['prefix']}{text}{config['suffix']}"
    return formatted
