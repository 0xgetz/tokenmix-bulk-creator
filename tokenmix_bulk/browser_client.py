"""Browser-driven TokenMix client.

TokenMix protects registration with a Cloudflare Turnstile challenge whose token
is issued by JavaScript running in a real browser. A pure HTTP client therefore
cannot register accounts by itself. This module drives a real browser (via
Playwright) so that the challenge is solved naturally, then performs the
authenticated REST calls from inside that browser context using ``fetch``.

The client exposes a small, synchronous API:

    with TokenMixBrowser(config) as client:
        client.send_verification_code(email)
        session = client.register(email, code, password)
        key = client.create_api_key(session, name)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .config import RunConfig


class TokenMixError(RuntimeError):
    """Raised for any unrecoverable TokenMix interaction error."""


class RegistrationBlocked(TokenMixError):
    """Raised when the site refuses registration (Turnstile / risk control)."""


class DomainNotSupported(TokenMixError):
    """Raised when TokenMix rejects the inbox domain as disposable.

    TokenMix maintains a block-list of throwaway-mail domains. When the
    supplied address uses one of them the API answers with
    ``400 This email provider is not supported``. Retrying with the same
    domain cannot succeed; use a different provider or a custom domain.
    """


@dataclass
class Session:
    """Authenticated session material returned by the register/login calls."""

    access_token: str
    refresh_token: str | None = None
    user: dict[str, Any] = field(default_factory=dict)


@dataclass
class ApiKey:
    """A freshly minted API key."""

    key: str
    name: str
    key_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class TokenMixBrowser:
    """Playwright-backed client for the TokenMix web application."""

    def __init__(self, config: RunConfig) -> None:
        self.config = config
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._turnstile_site_key: str | None = None

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self) -> "TokenMixBrowser":
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def start(self) -> None:
        """Launch the browser and open the TokenMix origin."""

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:  # pragma: no cover
            raise TokenMixError(
                "Playwright is required. Install it with "
                "`pip install playwright` and `playwright install chromium`."
            ) from exc

        self._playwright = sync_playwright().start()
        launcher = getattr(self._playwright, self.config.browser, None)
        if launcher is None:
            raise TokenMixError(f"unsupported browser engine: {self.config.browser}")

        launch_kwargs: dict[str, Any] = {"headless": self.config.headless}
        if self.config.proxy:
            launch_kwargs["proxy"] = {"server": self.config.proxy}
        if self.config.browser == "chromium":
            launch_kwargs["args"] = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]

        self._browser = launcher.launch(**launch_kwargs)
        context_kwargs: dict[str, Any] = {}
        if self.config.user_agent:
            context_kwargs["user_agent"] = self.config.user_agent
        self._context = self._browser.new_context(**context_kwargs)
        self._context.set_default_timeout(self.config.page_timeout * 1000)
        self._page = self._context.new_page()
        self._page.goto(self.config.site_url, wait_until="domcontentloaded")
        self._wait_turnstile_ready()

    def close(self) -> None:
        for resource in (self._context, self._browser):
            try:
                if resource is not None:
                    resource.close()
            except Exception:  # noqa: BLE001 - best-effort teardown
                pass
        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:  # noqa: BLE001
                pass
        self._context = self._browser = self._page = self._playwright = None

    # -- Turnstile helpers -------------------------------------------------
    def _wait_turnstile_ready(self, timeout: float = 20.0) -> None:
        """Best-effort wait until the Turnstile script has loaded."""

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                ready = self._page.evaluate("typeof window.turnstile !== 'undefined'")
                if ready:
                    return
            except Exception:  # noqa: BLE001
                pass
            self._page.wait_for_timeout(500)

    def _turnstile_token(self, timeout: float | None = None, *, fresh: bool = True) -> str | None:
        """Return a usable Turnstile token, waiting for the widget to solve.

        Turnstile tokens are single-use: every server call that validates one
        must be given a freshly generated token. When ``fresh`` is true the
        widget is reset and re-executed before the token is read. The site key
        is taken from the public configuration endpoint so the widget can be
        rendered even before the SPA creates it.
        """

        timeout = timeout or self.config.timeout
        self._render_turnstile()
        if fresh:
            self._reset_turnstile()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            token = self._page.evaluate(
                """() => {
                    try {
                        if (window.turnstile && typeof window.turnstile.getResponse === 'function') {
                            const values = [];
                            // render=explicit widgets get an id; probe common ids.
                            for (const id of ['cf-turnstile', 'turnstile-widget', 'register-turnstile']) {
                                try { const v = window.turnstile.getResponse(id); if (v) values.push(v); } catch (e) {}
                            }
                            const any = window.turnstile.getResponse();
                            if (any) values.push(any);
                            if (values.length) return values[0];
                        }
                        const input = document.querySelector('input[name="cf-turnstile-response"]');
                        if (input && input.value) return input.value;
                    } catch (e) {}
                    return null;
                }"""
            )
            if token:
                return token
            self._page.wait_for_timeout(500)
        return None

    def _reset_turnstile(self) -> None:
        """Reset and re-execute the rendered widget to mint a new token."""

        self._page.evaluate(
            """async () => {
                try {
                    if (!window.turnstile) return;
                    window.turnstile.reset();
                    await new Promise((r) => setTimeout(r, 800));
                    try { window.turnstile.execute(); } catch (e) {}
                } catch (e) {}
            }"""
        )
        self._page.wait_for_timeout(1200)

    def _render_turnstile(self) -> None:
        """Explicitly render an invisible Turnstile widget if none exists.

        The site key is read from the public configuration endpoint so the
        widget can be rendered even when the SPA has not created it yet.
        """

        if not self._turnstile_site_key:
            self._turnstile_site_key = self._fetch_site_key()
        if not self._turnstile_site_key:
            return
        self._page.evaluate(
            """async (key) => {
                if (!window.turnstile) return;
                if (document.querySelector('input[name=\"cf-turnstile-response\"]')) return;
                if (window.__tmBulkWidgetId__ !== undefined) return;
                const slot = document.createElement('div');
                slot.id = 'tm-bulk-turnstile';
                slot.style.display = 'none';
                document.body.appendChild(slot);
                try {
                    window.__tmBulkWidgetId__ = window.turnstile.render('#tm-bulk-turnstile', {
                        sitekey: key, size: 'invisible'
                    });
                    window.turnstile.execute(window.__tmBulkWidgetId__);
                } catch (e) {}
            }""",
            self._turnstile_site_key,
        )

    def _fetch_site_key(self) -> str | None:
        """Read the Turnstile site key from the public configuration API."""

        try:
            payload = self._fetch("/api/configs/public")
        except TokenMixError:
            return None
        data = payload.get("data", payload)
        if isinstance(data, dict):
            return data.get("turnstile_site_key")
        return None

    # -- HTTP gateway ------------------------------------------------------
    def _fetch(self, path: str, *, method: str = "GET",
               body: dict[str, Any] | None = None,
               token: str | None = None) -> dict[str, Any]:
        """Perform an authenticated REST call from inside the page context."""

        result = self._page.evaluate(
            """async ({path, method, body, token, base}) => {
                const headers = {'Content-Type': 'application/json', 'Accept-Language': 'en'};
                const stored = localStorage.getItem('access_token');
                const bearer = token || stored;
                if (bearer) headers['Authorization'] = `Bearer ${bearer}`;
                const options = {method, headers};
                if (body !== null && body !== undefined) options.body = JSON.stringify(body);
                const response = await fetch(base + path, options);
                let payload = null;
                try { payload = await response.json(); } catch (e) { payload = null; }
                return {status: response.status, ok: response.ok, payload};
            }""",
            {
                "path": path,
                "method": method,
                "body": body,
                "token": token,
                "base": self.config.base_url,
            },
        )
        status = result.get("status", 0)
        payload = result.get("payload")
        if status >= 400:
            message = ""
            if isinstance(payload, dict):
                message = payload.get("message") or str(payload.get("error") or "")
            if status == 400 and "verification" in message.lower():
                raise RegistrationBlocked(message or "Turnstile verification failed")
            if status == 400 and (
                "not supported" in message.lower()
                or "disposable" in message.lower()
                or "mainstream" in message.lower()
            ):
                raise DomainNotSupported(message)
            if status == 429:
                raise RegistrationBlocked(
                    message or "rate limited by TokenMix; retry later"
                )
            raise TokenMixError(f"HTTP {status} for {path}: {message or payload}")
        return payload or {}

    # -- public API --------------------------------------------------------
    def send_verification_code(self, email: str) -> None:
        """Trigger the ``register`` verification email for ``email``."""

        token = self._turnstile_token()
        body: dict[str, Any] = {"email": email, "type": "register"}
        if token:
            body["turnstile_token"] = token
        try:
            self._fetch("/api/auth/verify-email", method="POST", body=body)
        except RegistrationBlocked:
            # Retry once after giving the widget more time to solve.
            self._page.wait_for_timeout(4000)
            token = self._turnstile_token()
            if token:
                body["turnstile_token"] = token
            self._fetch("/api/auth/verify-email", method="POST", body=body)

    def register(
        self,
        email: str,
        code: str,
        password: str,
        referral_code: str | None = None,
    ) -> Session:
        """Complete registration using the emailed verification code."""

        token = self._turnstile_token()
        body: dict[str, Any] = {
            "email": email,
            "code": code,
            "password": password,
        }
        if referral_code:
            body["referral_code"] = referral_code
        if token:
            body["turnstile_token"] = token
        payload = self._fetch("/api/auth/register", method="POST", body=body)
        data = payload.get("data", payload)
        access = data.get("access_token")
        if not access:
            raise TokenMixError("registration succeeded but no access token returned")
        session = Session(
            access_token=access,
            refresh_token=data.get("refresh_token"),
            user=data.get("user", {}),
        )
        self._page.evaluate(
            """(data) => {
                try {
                    localStorage.setItem('access_token', data.access);
                    if (data.refresh) localStorage.setItem('refresh_token', data.refresh);
                } catch (e) {}
            }""",
            {"access": session.access_token, "refresh": session.refresh_token},
        )
        return session

    def create_api_key(
        self,
        session: Session,
        name: str,
        *,
        monthly_limit_usd: float | None = None,
        allowed_models: list[str] | None = None,
        allowed_ips: str | None = None,
    ) -> ApiKey:
        """Create an API key with the given (randomised) ``name``."""

        body: dict[str, Any] = {"name": name}
        if monthly_limit_usd is not None:
            body["monthly_limit"] = int(monthly_limit_usd * 1_000_000)
        if allowed_models:
            import json as _json

            body["allowed_models"] = _json.dumps(allowed_models)
        if allowed_ips:
            body["allowed_ips"] = allowed_ips

        payload = self._fetch(
            "/api/user/api-keys", method="POST", body=body, token=session.access_token
        )
        data = payload.get("data", payload)
        key = data.get("key")
        if not key:
            raise TokenMixError("key creation returned no key material")
        return ApiKey(
            key=key,
            name=data.get("name", name),
            key_id=str(data.get("id")) if data.get("id") is not None else None,
            raw=data,
        )

    def account_summary(self, session: Session) -> dict[str, Any]:
        """Return the authenticated user's profile (used for balance display)."""

        try:
            payload = self._fetch("/api/user/profile", token=session.access_token)
            return payload.get("data", payload) or {}
        except TokenMixError:
            return {}
