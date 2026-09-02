import re

# Comprehensive shortcode mapping table
EMOJI_MAP = {
    ':)': '🙂',
    ':-)': '🙂',
    ':D': '😃',
    ':-D': '😃',
    ';)': '😉',
    ';-)': '😉',
    ':smile:': '😄',
    ':grin:': '😁',
    ':heart:': '❤️',
    ':fire:': '🔥',
    ':thumbsup:': '👍',
    ':thumbsdown:': '👎',
    ':rocket:': '🚀',
    ':wave:': '👋',
    ':100:': '💯',
    ':party:': '🎉',
    ':thinking:': '🤔',
    ':clap:': '👏',
    ':star:': '⭐',
    ':check:': '✅',
    ':x:': '❌'
}

# Compile regex pattern matching exact keys in EMOJI_MAP
_EMOJI_REGEX = re.compile('|'.join(map(re.escape, EMOJI_MAP.keys())))

def parse_emoji_shortcodes(text: str) -> str:
    """Replaces emoji shortcodes with their Unicode counterparts while preserving non-emoji text."""
    if not text:
        return ""
    
    return _EMOJI_REGEX.sub(lambda match: EMOJI_MAP[match.group(0)], text)
