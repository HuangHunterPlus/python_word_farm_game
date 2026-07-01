import math


def separator(char="-", width=40):
    return char * width


def title(text, char="=", width=40):
    side = (width - len(text) - 2) // 2
    return f"{char * side} {text} {char * side}"


def subtitle(text, char="─", width=40):
    return f"{char * 2} {text} {char * (width - len(text) - 5)}"


def status_icon(status):
    icons = {
        "empty": "⬜",
        "growing": "⏳",
        "mature": "🟢",
        "withered": "💀",
    }
    return icons.get(status, "❓")


def crop_emoji(crop_id):
    emojis = {
        "carrot": "🥕",
        "potato": "🥔",
        "tomato": "🍅",
        "strawberry": "🍓",
        "wheat": "🌾",
        "apple_tree": "🍎",
        "orange_tree": "🍊",
        "grape": "🍇",
        "lingzhi": "🍄",
    }
    return emojis.get(crop_id, "🌱")


def format_gold(amount):
    return f"{amount}💰"


def format_exp(amount):
    return f"{amount}✨"


def level_bar(exp, next_exp, width=15):
    if next_exp <= 0:
        return "[" + "█" * width + "]"
    filled = int((exp / next_exp) * width)
    bar = "█" * min(filled, width) + "░" * max(width - filled, 0)
    return f"[{bar}]"
