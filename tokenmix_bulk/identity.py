"""Random identity primitives: names, emails, passwords and key names."""

from __future__ import annotations

import random
import secrets
import string

ADJECTIVES = (
    "swift", "silent", "crimson", "azure", "lunar", "solar", "rapid", "cosmic",
    "frost", "ember", "vivid", "quiet", "noble", "brave", "clever", "atomic",
    "hidden", "golden", "electric", "shadow", "prime", "titan", "nova", "drift",
)

NOUNS = (
    "falcon", "otter", "raven", "panda", "tiger", "comet", "harbor", "summit",
    "vector", "matrix", "cipher", "quartz", "phoenix", "orbit", "nebula", "cobalt",
    "lynx", "dragon", "pilot", "ranger", "forge", "beacon", "glacier", "meadow",
)

KEY_PREFIXES = (
    "prod", "staging", "dev", "ci", "worker", "gateway", "relay", "edge",
    "service", "automation", "batch", "runner",
)

_ALPHABET = string.ascii_lowercase + string.digits


def _random_word(words: tuple[str, ...]) -> str:
    return random.choice(words)


def random_username(separator: str = ".") -> str:
    """Return a readable, lower-case username such as ``swift.falcon``."""

    return f"{_random_word(ADJECTIVES)}{separator}{_random_word(NOUNS)}"


def random_email(domain: str, username: str | None = None) -> str:
    """Build a random address for ``domain``.

    A single dot separates the two words and a short alphanumeric suffix is
    appended. Both supported providers accept this shape (mail.tm strips dots
    server-side; temp-mail.io keeps them).
    """

    local = username or random_username(separator=".")
    suffix = "".join(secrets.choice(_ALPHABET) for _ in range(6))
    return f"{local}.{suffix}@{domain}"


def random_password(length: int = 18) -> str:
    """Return a strong password that satisfies letter+digit policies."""

    if length < 8:
        raise ValueError("password length must be at least 8 characters")

    letters = string.ascii_letters
    digits = string.digits
    specials = "!@#$%^&*"
    required = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(digits),
        secrets.choice(specials),
    ]
    remaining = [secrets.choice(letters + digits) for _ in range(length - len(required))]
    pool = required + remaining
    random.shuffle(pool)
    return "".join(pool)


def random_key_name(prefix: str | None = None) -> str:
    """Return a descriptive API-key name such as ``prod-swift-falcon-a1b2``."""

    head = prefix or random.choice(KEY_PREFIXES)
    tail = "".join(secrets.choice(_ALPHABET) for _ in range(4))
    return f"{head}-{_random_word(ADJECTIVES)}-{_random_word(NOUNS)}-{tail}"
