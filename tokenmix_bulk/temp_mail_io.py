"""Minimal client for the temp-mail.io disposable inbox API.

temp-mail.io exposes a small public REST API at
``https://api.internal.temp-mail.io/api/v3``:

* ``GET  /domains``                       -> list of public domains
* ``POST /email/new``                     -> create an inbox, returns {email, token}
* ``GET  /email/{address}/messages``      -> list messages
* ``GET  /email/{address}/messages/{id}`` -> single message with bodies

This module wraps that subset behind the same tiny interface used by the
mail.tm provider, so the orchestrator can stay provider-agnostic.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

import requests

DEFAULT_BASE_URL = "https://api.internal.temp-mail.io/api/v3"


class TempMailError(RuntimeError):
    """Raised when the temp-mail.io API returns an unexpected response."""


@dataclass
class Message:
    """A single inbox message, reduced to the fields this project needs."""

    id: str
    sender: str
    subject: str
    body_text: str = ""
    body_html: str = ""
    created_at: str = ""

    @property
    def code(self) -> str | None:
        """Extract the first 4-8 digit numeric verification code, if present."""

        import re

        haystack = f"{self.subject}\n{self.body_text}"
        match = re.search(r"(?<!\d)(\d{4,8})(?!\d)", haystack)
        return match.group(1) if match else None


@dataclass
class Inbox:
    """A created disposable inbox."""

    address: str
    password: str = ""
    token: str = ""
    base_url: str = DEFAULT_BASE_URL
    _session: requests.Session = field(default_factory=requests.Session, repr=False)


class TempMailClient:
    """Thin wrapper around the temp-mail.io REST API."""

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
        self._headers = {
            "Accept": "application/json",
            "User-Agent": "tokenmix-bulk-creator/1.0",
        }

    # -- low level ---------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        headers = {**self._headers, **kwargs.pop("headers", {})}
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self._session.request(
                    method, url, headers=headers, timeout=self.timeout, **kwargs
                )
            except requests.RequestException as exc:
                last_error = exc
            else:
                if response.status_code < 500:
                    return response
                last_error = TempMailError(
                    f"server error {response.status_code} for {path}"
                )
            if attempt < self.retries:
                time.sleep(0.8 * attempt)
        raise TempMailError(f"request to {path} failed: {last_error}")

    @staticmethod
    def _json(response: requests.Response):
        try:
            payload = response.json()
        except ValueError as exc:
            raise TempMailError(
                f"invalid JSON from server: {response.text[:200]}"
            ) from exc
        if response.status_code >= 400:
            message = ""
            if isinstance(payload, dict):
                message = payload.get("message") or payload.get("detail") or ""
            raise TempMailError(
                f"HTTP {response.status_code}: {message or response.text[:200]}"
            )
        return payload

    # -- public API --------------------------------------------------------
    def domains(self) -> list[str]:
        """Return the list of public domains."""

        payload = self._json(self._request("GET", "/domains"))
        entries = payload.get("domains", []) if isinstance(payload, dict) else payload
        names = [
            entry["name"]
            for entry in entries
            if isinstance(entry, dict) and entry.get("name")
        ]
        if not names:
            raise TempMailError("no temp-mail.io domains available")
        return names

    def pick_domain(self) -> str:
        """Return a random public domain."""

        return random.choice(self.domains())

    def create_inbox(self, name: str | None = None, domain: str | None = None) -> Inbox:
        """Create a new inbox and return its address and access token.

        ``name`` is the local part; when omitted the service generates a random
        one. ``domain`` pins the domain; when omitted the service picks one.
        """

        body: dict[str, str] = {}
        if name:
            body["name"] = name
        if domain:
            body["domain"] = domain
        payload = self._json(self._request("POST", "/email/new", json=body))
        address = payload.get("email")
        if not address:
            raise TempMailError("temp-mail.io did not return an email address")
        return Inbox(
            address=address,
            token=payload.get("token", ""),
            base_url=self.base_url,
            _session=self._session,
        )

    def messages(self, inbox: Inbox) -> list[Message]:
        """Return the messages currently in ``inbox``."""

        payload = self._json(self._request("GET", f"/email/{inbox.address}/messages"))
        members = payload if isinstance(payload, list) else payload.get("messages", [])
        return [
            Message(
                id=m.get("id", ""),
                sender=m.get("from", ""),
                subject=m.get("subject", ""),
                body_text=m.get("body_text", "") or "",
                body_html=m.get("body_html", "") or "",
                created_at=m.get("created_at", ""),
            )
            for m in members
            if isinstance(m, dict)
        ]

    def read_message(self, inbox: Inbox, message_id: str) -> Message:
        """Fetch a single message including its plain-text body."""

        payload = self._json(
            self._request("GET", f"/email/{inbox.address}/messages/{message_id}")
        )
        data = payload.get("message", payload) if isinstance(payload, dict) else payload
        return Message(
            id=data.get("id", message_id),
            sender=data.get("from", ""),
            subject=data.get("subject", ""),
            body_text=data.get("body_text", "") or "",
            body_html=data.get("body_html", "") or "",
            created_at=data.get("created_at", ""),
        )

    def wait_for_code(
        self,
        inbox: Inbox,
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
                for message in self.messages(inbox):
                    if message.id in seen:
                        continue
                    if sender_contains and sender_contains.lower() not in message.sender.lower():
                        continue
                    seen.add(message.id)
                    full = message
                    if not full.body_text:
                        full = self.read_message(inbox, message.id)
                    if full.code:
                        return full.code
            except TempMailError as exc:
                last_error = exc
            time.sleep(interval)
        raise TempMailError(
            f"no verification code for {inbox.address} within {timeout:.0f}s"
            + (f" (last error: {last_error})" if last_error else "")
        )
