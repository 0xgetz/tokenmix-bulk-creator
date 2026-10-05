<p align="center"><a href="README.md">
  <img src="assets/logo.png" alt="TokenMix Bulk Creator" width="150">
</a></p>

<p align="center"><img src="assets/banner.png" alt="TokenMix Bulk Creator banner"></p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/playwright-%E2%9C%94-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-22e6a5?style=for-the-badge" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/tests-7%20passed-39d0ff?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests">
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-7c5cff?style=for-the-badge" alt="Platform">
</p>

# TokenMix Bulk Account Creator

> Bulk-provision TokenMix accounts with disposable inboxes and auto-generate API keys that carry random names.

<p><strong>English</strong> · <a href="readme/README.id.md">Indonesia</a> · <a href="readme/README.zh.md">简体中文</a> · <a href="readme/README.ja.md">日本語</a> · <a href="readme/README.ko.md">한국어</a> · <a href="readme/README.es.md">Español</a></p>

---

`tokenmix-bulk` ties three things together in one reproducible pipeline: a
disposable mailbox provider ([temp-mail.io](https://temp-mail.io)), a real browser that
clears the Cloudflare Turnstile challenge, and the TokenMix REST API. Feed it a
count, and it returns a JSON/CSV table of ready-to-use `sk-tm-...` keys.

> This tool is intended for legitimate automation, internal testing and
> research on accounts you own. You are responsible for complying with
> TokenMix's terms of service and any applicable law.

---

## Why a browser?

TokenMix protects registration with a **Cloudflare Turnstile** challenge. The
token is produced by JavaScript in a real browser and is validated server-side,
so a plain `requests`-only client is rejected with
`400 Please complete the verification`. This project therefore drives a real
browser with [Playwright](https://playwright.dev): the challenge is solved
naturally, then the authenticated REST calls are executed from inside that
browser context using `fetch`.

## Features

- **Disposable mailboxes** – creates a unique temp-mail.io inbox per account.
- **Turnstile-aware** – renders an invisible widget and mints a fresh
  single-use token for every server call.
- **Random identity** – usernames, passwords and key names are unpredictable.
- **Auto API keys** – named like `prod-swift-falcon-a1b2`.
- **Incremental output** – JSON + CSV are flushed after every account, so a
  crash never loses completed work.
- **Concurrency** – optional parallel workers.
- **Retries** – per-account attempts with fresh identities on failure.
- **Structured logging** – colourised, timestamped console output.

## Architecture

```
tokenmix_bulk/
├── cli.py             # argparse CLI entry point
├── config.py          # RunConfig dataclass + JSON/YAML loading
├── identity.py        # random usernames, passwords, key names
├── temp_mail_io.py    # temp-mail.io REST client (inboxes, messages, codes)
├── mailtm.py          # optional mail.tm fallback client
├── providers.py       # uniform provider facade
├── browser_client.py  # Playwright client: Turnstile + TokenMix REST calls
├── orchestrator.py    # end-to-end flow, retries, concurrency
├── results.py         # result models + JSON/CSV persistence
└── logging_utils.py   # shared logger
```

## Requirements

- Python 3.9+
- A Chromium/Firefox/WebKit browser installed for Playwright

## Installation

```bash
git clone https://github.com/0xgetz/tokenmix-bulk-creator.git
cd tokenmix-bulk-creator
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
playwright install chromium
```

## Quick start

```bash
# One account, watch the browser work
tokenmix-bulk --count 1

# Five accounts, custom key prefix, JSON + CSV in ./output
tokenmix-bulk -n 5 --key-prefix prod -o output/accounts.json --csv output/accounts.csv

# Headless batch of ten with two workers
tokenmix-bulk -n 10 -c 2 --headless

# Or use a config file
tokenmix-bulk --config config.example.json
```

### CLI reference

| Flag | Default | Description |
| --- | --- | --- |
| `-n, --count` | `1` | Number of accounts to create |
| `-c, --concurrency` | `1` | Parallel workers |
| `-o, --output` | `accounts.json` | JSON result path |
| `--csv` | `accounts.csv` | CSV result path |
| `--password` | random | Fixed password for all accounts |
| `--key-prefix` | random | Prefix for generated key names |
| `--referral` | – | Referral code to submit |
| `--mail-provider` | `temp-mail-io` | `temp-mail-io` \| `mail-tm` |
| `--mail-domain` | auto | Pin a mail provider domain |
| `--headless` | off | Run the browser headless |
| `--browser` | `chromium` | `chromium` \| `firefox` \| `webkit` |
| `--proxy` | – | Proxy URL for the browser |
| `--retries` | `2` | Attempts per account |
| `--stop-on-error` | off | Abort the batch on first failure |
| `--config` | – | Load a JSON/YAML config file |
| `-v, --verbose` | off | Debug logging |

## Providers & domain support

Two disposable-mail providers are bundled:

| Provider | Flag value | API |
| --- | --- | --- |
| temp-mail.io *(default)* | `temp-mail-io` | `api.internal.temp-mail.io/api/v3` |
| mail.tm *(fallback)* | `mail-tm` | `api.mail.tm` |

TokenMix runs an anti-abuse filter that rejects many throwaway-mail domains
with `400 This email provider is not supported. Please use a mainstream or work
email`. When that happens the run marks the account as failed with
`DomainNotSupported` and **does not retry** the same domain — retrying cannot
help. If your provider domain is on the block-list:

1. Try the other provider, or pin a specific domain with `--mail-domain`.
2. Point `--mail-base-url` at a provider you control, or run your own domain.
3. Slow the batch down; TokenMix also enforces a global registration rate
   limit and answers `429 Too many registration attempts` when it is exceeded.

A separate `429` is treated as retryable and respects `--retries`.

## Output

`accounts.json`:

```json
{
  "generated_at": "2026-01-01T12:00:00+00:00",
  "total": 1,
  "succeeded": 1,
  "failed": 0,
  "accounts": [
    {
      "index": 1,
      "status": "success",
      "email": "swiftfalcon.ab12cd@maxxspace.com",
      "password": "…",
      "api_key": "sk-tm-…",
      "api_key_name": "prod-swift-falcon-a1b2",
      "balance": "$1.0000"
    }
  ]
}
```

A matching CSV is written for spreadsheet workflows.

## Using a generated key

TokenMix is OpenAI-compatible with base URL `https://api.tokenmix.ai/v1`:

```bash
curl https://api.tokenmix.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-tm-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}'
```

## Programmatic use

```python
from tokenmix_bulk import RunConfig
from tokenmix_bulk.orchestrator import BulkCreator

config = RunConfig(count=3, headless=True)
results = BulkCreator(config).run()
for result in results:
    print(result.email, result.api_key)
```

## Development

```bash
pip install -e ".[dev]"
python -m pytest
```

## License

Released under the [MIT License](LICENSE).
