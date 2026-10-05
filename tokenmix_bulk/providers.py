"""Provider registry: a thin, uniform façade over the mailbox back-ends.

Two disposable-mail providers are supported:

* ``temp-mail-io``  (default) – api.internal.temp-mail.io
* ``mail-tm``       – api.mail.tm

Each provider exposes the same operations used by the orchestrator:
``pick_domain``, ``create_inbox``, ``messages`` and ``wait_for_code``.
``MailboxProvider`` normalises the clients' slightly different return types
(``Mailbox`` vs ``Inbox``) behind a single ``UnifiedInbox`` dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass

from .mailtm import MailTmClient, Mailbox
from .temp_mail_io import Inbox, TempMailClient

PROVIDERS = ("temp-mail-io", "mail-tm")
DEFAULT_PROVIDER = "temp-mail-io"


@dataclass
class UnifiedInbox:
    """Provider-agnostic inbox handle."""

    address: str
    token: str
    provider: str
    password: str = ""
    raw: object | None = None


class MailboxProvider:
    """Uniform interface over the supported disposable-mail providers."""

    def __init__(
        self,
        name: str = DEFAULT_PROVIDER,
        *,
        base_url: str | None = None,
    ) -> None:
        if name not in PROVIDERS:
            raise ValueError(
                f"unknown mail provider {name!r}; choose one of {', '.join(PROVIDERS)}"
            )
        self.name = name
        if name == "mail-tm":
            self._client = MailTmClient(base_url) if base_url else MailTmClient()
        else:
            self._client = TempMailClient(base_url) if base_url else TempMailClient()

    def pick_domain(self) -> str:
        return self._client.pick_domain()

    def create_inbox(
        self, name: str | None = None, domain: str | None = None
    ) -> UnifiedInbox:
        if self.name == "mail-tm":
            local = name or ""
            address = f"{local}@{domain}" if (local and domain) else None
            mailbox: Mailbox = self._client.create_account(
                address or self._generated_address(domain),
                self._password(),
            )
            return UnifiedInbox(
                address=mailbox.address,
                token=mailbox.token,
                provider=self.name,
                password=mailbox.password,
                raw=mailbox,
            )
        inbox: Inbox = self._client.create_inbox(name=name, domain=domain)
        return UnifiedInbox(
            address=inbox.address,
            token=inbox.token,
            provider=self.name,
            raw=inbox,
        )

    def messages(self, inbox: UnifiedInbox):
        return self._client.messages(inbox.raw)

    def wait_for_code(
        self,
        inbox: UnifiedInbox,
        *,
        sender_contains: str | None = "tokenmix",
        timeout: float = 120.0,
        interval: float = 3.0,
        seen: set[str] | None = None,
    ) -> str:
        return self._client.wait_for_code(
            inbox.raw,
            sender_contains=sender_contains,
            timeout=timeout,
            interval=interval,
            seen=seen,
        )

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _password() -> str:
        from .identity import random_password

        return random_password()

    @staticmethod
    def _generated_address(domain: str | None) -> str:
        from .identity import random_email

        return random_email(domain or MailTmClient().pick_domain())
