"""Command-line interface for TokenMix Bulk Account Creator."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from . import __version__
from .config import RunConfig
from .logging_utils import get_logger
from .orchestrator import BulkCreator
from .results import ResultStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tokenmix-bulk",
        description=(
            "Bulk-create TokenMix accounts with disposable mail.tm inboxes and "
            "auto-generate API keys with randomised names."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-n", "--count", type=int, default=1, help="number of accounts")
    parser.add_argument("-c", "--concurrency", type=int, default=1, help="parallel workers")
    parser.add_argument("-o", "--output", default="accounts.json", help="JSON output path")
    parser.add_argument("--csv", dest="csv_output", default="accounts.csv", help="CSV output path")
    parser.add_argument("--password", default=None, help="fixed password (default: random)")
    parser.add_argument("--key-prefix", dest="key_name_prefix", default=None,
                        help="prefix for generated key names")
    parser.add_argument("--referral", dest="referral_code", default=None, help="referral code")
    parser.add_argument("--mail-domain", dest="mail_domain", default=None,
                        help="pin a specific mail.tm domain")
    parser.add_argument("--headless", action="store_true", help="run the browser headless")
    parser.add_argument("--browser", default="chromium",
                        choices=["chromium", "firefox", "webkit"], help="browser engine")
    parser.add_argument("--proxy", default=None, help="proxy URL, e.g. http://host:port")
    parser.add_argument("--config", default=None, help="JSON/YAML config file")
    parser.add_argument("--retries", type=int, default=2, help="attempts per account")
    parser.add_argument("--stop-on-error", action="store_true",
                        help="abort the batch on the first failure")
    parser.add_argument("--timeout", type=float, default=180.0, help="per-account timeout")
    parser.add_argument("--code-timeout", type=float, default=150.0,
                        help="seconds to wait for the verification email")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def config_from_args(args: argparse.Namespace) -> RunConfig:
    if args.config:
        config = RunConfig.from_file(args.config)
        overrides = vars(args)
        for key in (
            "count", "concurrency", "output", "csv_output", "password",
            "key_name_prefix", "referral_code", "mail_domain", "headless",
            "browser", "proxy", "retries", "stop_on_error", "timeout",
            "code_timeout", "verbose",
        ):
            value = overrides.get(key)
            if value not in (None, False):
                setattr(config, key, value)
        return config
    return RunConfig(
        count=args.count,
        concurrency=args.concurrency,
        output=args.output,
        csv_output=args.csv_output,
        password=args.password,
        key_name_prefix=args.key_name_prefix,
        referral_code=args.referral_code,
        mail_domain=args.mail_domain,
        headless=args.headless,
        browser=args.browser,
        proxy=args.proxy,
        retries=args.retries,
        stop_on_error=args.stop_on_error,
        timeout=args.timeout,
        code_timeout=args.code_timeout,
        verbose=args.verbose,
    )


def _progress_printer():
    def show(result) -> None:
        if result.status == "success":
            print(f"  ✔ [{result.index}] {result.email} -> {result.api_key}")
        else:
            print(f"  ✘ [{result.index}] {result.email} -> {result.error}")
    return show


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    get_logger(level=logging.DEBUG if args.verbose else logging.INFO)
    logger = get_logger()

    if args.count < 1:
        parser.error("--count must be >= 1")
    if args.concurrency < 1:
        parser.error("--concurrency must be >= 1")

    config = config_from_args(args)
    logger.info("TokenMix Bulk Account Creator v%s", __version__)
    logger.info("output: %s", config.output)

    store = ResultStore(config.output, config.csv_output)
    creator = BulkCreator(config, store=store)
    try:
        creator.run(on_progress=_progress_printer())
    except KeyboardInterrupt:
        logger.warning("interrupted by user; partial results were saved")
        store.flush()
        return 130
    except Exception as exc:  # noqa: BLE001
        logger.error("fatal error: %s", exc)
        store.flush()
        return 1

    summary = store.summary()
    print()
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
