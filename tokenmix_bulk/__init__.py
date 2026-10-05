"""TokenMix Bulk Account Creator.

An end-to-end toolkit that provisions disposable mailboxes, registers
TokenMix accounts and mints API keys with randomised names.
"""

from .browser_client import (
    DomainNotSupported,
    RegistrationBlocked,
    TokenMixBrowser,
    TokenMixError,
)
from .config import RunConfig
from .providers import DEFAULT_PROVIDER, PROVIDERS, MailboxProvider

__all__ = [
    "__version__",
    "RunConfig",
    "MailboxProvider",
    "PROVIDERS",
    "DEFAULT_PROVIDER",
    "TokenMixBrowser",
    "TokenMixError",
    "RegistrationBlocked",
    "DomainNotSupported",
]
__version__ = "1.1.0"
