"""High-level orchestration: mail + browser + persistence."""

from __future__ import annotations

import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from .browser_client import TokenMixBrowser, TokenMixError
from .config import RunConfig
from .identity import random_email, random_key_name, random_password, random_username
from .logging_utils import get_logger
from .mailtm import MailTmClient, MailTmError
from .results import AccountResult, ResultStore

logger = get_logger("tokenmix_bulk")

ProgressCallback = Callable[[AccountResult], None]


class BulkCreator:
    """Provision ``config.count`` TokenMix accounts and API keys end to end."""

    def __init__(self, config: RunConfig, *, store: ResultStore | None = None) -> None:
        self.config = config
        self.store = store or ResultStore(config.output, config.csv_output)
        self._counter = 0
        self._lock = threading.Lock()

    def _next_index(self) -> int:
        with self._lock:
            self._counter += 1
            return self._counter

    # -- single account ----------------------------------------------------
    def provision_one(self, index: int) -> AccountResult:
        """Run the full flow (mailbox -> register -> key) for one account."""

        config = self.config
        mail = MailTmClient(config.mail_base_url)
        domain = config.mail_domain or mail.pick_domain()
        username = random_username()
        email = random_email(domain, username)
        password = config.password or random_password()
        result = AccountResult(
            index=index, email=email, password=password, username=username
        )

        last_error: Exception | None = None
        for attempt in range(1, config.retries + 1):
            result.attempts = attempt
            try:
                logger.info(
                    "[%d] (%d/%d) creating mailbox %s", index, attempt, config.retries, email
                )
                mailbox = mail.create_account(email, password)
                email = mailbox.address
                result.email = email

                with TokenMixBrowser(config) as client:
                    logger.info("[%d] requesting verification code", index)
                    client.send_verification_code(email)
                    seen: set[str] = set()
                    code = mail.wait_for_code(
                        mailbox,
                        timeout=config.code_timeout,
                        seen=seen,
                    )
                    logger.info("[%d] code received, registering", index)

                    session = client.register(
                        email, code, password, config.referral_code
                    )

                    key_name = random_key_name(config.key_name_prefix)
                    logger.info("[%d] creating api key %s", index, key_name)
                    api_key = client.create_api_key(session, key_name)
                    summary = client.account_summary(session)

                result.api_key = api_key.key
                result.api_key_name = api_key.name
                result.key_id = api_key.key_id
                balance = summary.get("balance")
                if isinstance(balance, (int, float)):
                    result.balance = f"${balance / 1_000_000:.4f}".rstrip("0").rstrip(".")
                elif balance is not None:
                    result.balance = str(balance)
                result.finish("success")
                logger.info("[%d] success -> %s", index, key_name)
                return result
            except (TokenMixError, MailTmError, Exception) as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("[%d] attempt %d failed: %s", index, attempt, exc)
                if runtime_is_fatal(exc):
                    break
                if attempt < config.retries:
                    time.sleep(2.0 * attempt)
                    # New mailbox identity avoids verification-code collisions.
                    username = random_username()
                    email = random_email(domain, username)
                    result.email = email
                    result.username = username

        result.finish("failed", error=str(last_error) if last_error else "unknown error")
        return result

    # -- batch -------------------------------------------------------------
    def run(self, on_progress: ProgressCallback | None = None) -> list[AccountResult]:
        """Provision the whole batch, honouring the configured concurrency."""

        config = self.config
        total = config.count
        logger.info("starting batch: %d account(s), concurrency=%d", total, config.concurrency)

        if config.concurrency <= 1 or total == 1:
            results: list[AccountResult] = []
            for _ in range(total):
                index = self._next_index()
                result = self.provision_one(index)
                self.store.add(result)
                if on_progress:
                    on_progress(result)
                if result.status != "success" and config.stop_on_error:
                    logger.error("stop_on_error set; aborting after account %d", index)
                    break
            return results

        results = []
        with ThreadPoolExecutor(max_workers=config.concurrency) as pool:
            futures = {
                pool.submit(self.provision_one, self._next_index()): None
                for _ in range(total)
            }
            for future in as_completed(futures):
                result = future.result()
                self.store.add(result)
                results.append(result)
                if on_progress:
                    on_progress(result)
        return results


def runtime_is_fatal(exc: BaseException) -> bool:
    """Return True for errors that will not be fixed by retrying."""

    message = str(exc).lower()
    fatal_markers = (
        "playwright",
        "executable doesn't exist",
        "cannot find module",
        "unsupported browser",
    )
    return any(marker in message for marker in fatal_markers)
