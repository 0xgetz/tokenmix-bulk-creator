"""Minimal, dependency-light client for the mail.tm disposable inbox API.

The public documentation lives at https://docs.mail.tm. Only the subset of the
API required by this project is implemented: domains, account creation, token
issuance and message polling.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

import requests

DEFAULT_BASE_URL = "https://api.mail.tm"


class MailTmError(RuntimeError):
    """Raised when the mail.tm API returns an unexpected response."""


@dataclass
class Message:
    """A single inbox message, reduced to the fields this project needs."""

    id: str
    sender: str
    subject: str
    intro: str
    created_at: str
    raw_text: str = ""

    @property
    def code(self) -> str | None:
        """Extract the first 4-8 digit numeric verification code, if present."""

        import re

        haystack = f"{self.subject}\n{self.intro}\n{self.raw_text}"
        match = re.search(r"(?<!\d)(\d{4,8})(?!\d)", haystack)
        return match.group(1) if match else None


@dataclass
class Mailbox:
    """An authenticated disposable mailbox."""

    address: str
    password: str
    account_id: str
    token: str
    base_url: str = DEFAULT_BASE_URL
    _session: requests.Session = field(default_factory=requests.Session, repr=False)

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}


class MailTmClient:
    """Thin wrapper around the mail.tm REST API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 20.0,
        retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self._session = session or requests.Session()

    # -- low level ---------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self._session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
            except requests.RequestException as exc:  # network hiccup
                last_error = exc
            else:
                if response.status_code < 500:
                    return response
                last_error = MailTmError(
                    f"server error {response.status_code} for {path}"
                )
            if attempt < self.retries:
                time.sleep(0.8 * attempt)
        raise MailTmError(f"request to {path} failed: {last_error}")

    @staticmethod
    def _json(response: requests.Response) -> dict:
        try:
            payload = response.json()
        except ValueError as exc:
            raise MailTmError(f"invalid JSON from server: {response.text[:200]}") from exc
        if response.status_code >= 400:
            message = payload.get("message") or payload.get("detail") or response.text
            raise MailTmError(f"HTTP {response.status_code}: {message}")
        return payload

    # -- public API --------------------------------------------------------
    def domains(self) -> list[str]:
        """Return the list of active, publicly available domains."""

        payload = self._json(self._request("GET", "/domains"))
        members = payload.get("hydra:member", payload if isinstance(payload, list) else [])
        active = [
            entry["domain"]
            for entry in members
            if isinstance(entry, dict) and entry.get("isActive", True)
        ]
        if not active:
            raise MailTmError("no active mail.tm domains available")
        return active

    def pick_domain(self) -> str:
        """Return a random active domain."""

        return random.choice(self.domains())

    def create_account(self, address: str, password: str) -> Mailbox:
        """Register a new mailbox and exchange credentials for a JWT.

        mail.tm normalises the local part of the address (it strips dots), so
        the authoritative address is taken from the API response rather than
        from the value passed in. Callers must use ``Mailbox.address`` for any
        downstream registration step.
        """

        payload = self._json(
            self._request(
                "POST",
                "/accounts",
                json={"address": address, "password": password},
            )
        )
        canonical = payload.get("address") or address
        token = self._json(
            self._request(
                "POST",
                "/token",
                json={"address": canonical, "password": password},
            )
        )["token"]
        account_id = payload.get("id", "")
        if not account_id:
            try:
                me = self._json(
                    self._request(
                        "GET", "/me", headers={"Authorization": f"Bearer {token}"}
                    )
                )
                account_id = me.get("id", "")
            except MailTmError:
                pass
        return Mailbox(
            address=canonical,
            password=password,
            account_id=account_id,
            token=token,
            base_url=self.base_url,
            _session=self._session,
        )

    def messages(self, mailbox: Mailbox) -> list[Message]:
        """Return the messages currently in ``mailbox``.

        mail.tm replies either with a Hydra collection or, for an empty inbox,
        with a bare JSON list, so both shapes are handled here.
        """

        payload = self._json(
            self._request("GET", "/messages", headers=mailbox._headers)
        )
        if isinstance(payload, list):
            members = payload
        else:
            members = payload.get("hydra:member", [])
        return [
            Message(
                id=m["id"],
                sender=m.get("from", {}).get("address", ""),
                subject=m.get("subject", ""),
                intro=m.get("intro", ""),
                created_at=m.get("createdAt", ""),
            )
            for m in members
        ]

    def read_message(self, mailbox: Mailbox, message_id: str) -> Message:
        """Fetch a single message including its plain-text body."""

        payload = self._json(
            self._request("GET", f"/messages/{message_id}", headers=mailbox._headers)
        )
        return Message(
            id=payload.get("id", message_id),
            sender=payload.get("from", {}).get("address", ""),
            subject=payload.get("subject", ""),
            intro=payload.get("intro", ""),
            created_at=payload.get("createdAt", ""),
            raw_text=payload.get("text", ""),
        )

    def wait_for_code(
        self,
        mailbox: Mailbox,
        *,
        sender_contains: str | None = "tokenmix",
        timeout: float = 120.0,
        interval: float = 3.0,
        seen: set[str] | None = None,
    ) -> str:
        """Poll until a verification code arrives, then return the digits."""

        seen = seen if seen is not None else set()
        deadline = time.monotonic() + timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                for message in self.messages(mailbox):
                    if message.id in seen:
                        continue
                    if sender_contains and sender_contains.lower() not in message.sender.lower():
                        continue
                    full = self.read_message(mailbox, message.id)
                    seen.add(message.id)
                    if full.code:
                        return full.code
            except MailTmError as exc:  # transient; keep polling
                last_error = exc
            time.sleep(interval)
        raise MailTmError(
            f"no verification code for {mailbox.address} within {timeout:.0f}s"
            + (f" (last error: {last_error})" if last_error else "")
        )
