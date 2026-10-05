<p align="center"><a href="../README.md">
  <img src="../assets/logo.png" alt="TokenMix Bulk Creator" width="150">
</a></p>

<p align="center"><img src="../assets/banner.png" alt="TokenMix Bulk Creator banner"></p>

<p align="center"><a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a> <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/playwright-%E2%9C%94-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a> <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-22e6a5?style=for-the-badge" alt="MIT License"></a> <img src="https://img.shields.io/badge/tests-7%20passed-39d0ff?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"> <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-7c5cff?style=for-the-badge" alt="Platform"></p>

# TokenMix Bulk Account Creator

> Buat akun TokenMix secara massal dengan inbox sekali pakai dan pembuatan API key otomatis bernama acak.

<p><a href="../README.md">English</a> · <strong>Indonesia</strong> · <a href="README.zh.md">简体中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a></p>

---

## Mengapa pakai browser?

TokenMix melindungi pendaftaran dengan tantangan **Cloudflare Turnstile**. Klien HTTP biasa akan ditolak, sehingga proyek ini mengendalikan browser asli via Playwright, menyelesaikan tantangan secara alami, lalu menjalankan panggilan REST terautentikasi dari dalam konteks browser tersebut.

## Fitur

- Inbox mail.tm sekali pakai untuk setiap akun
- Sadar Turnstile dengan token sekali pakai
- Username, kata sandi, dan nama key yang acak
- API key otomatis bernama seperti `prod-swift-falcon-a1b2`
- Output JSON + CSV bertahap (aman jika berhenti)
- Konkurensi opsional dan percobaan ulang per akun

## Instalasi

```bash
git clone https://github.com/0xgetz/tokenmix-bulk-creator.git
cd tokenmix-bulk-creator
python -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium
```

## Mulai cepat

**Satu akun, browser terlihat**

```bash
tokenmix-bulk --count 1
```

**Lima akun, prefix khusus**

```bash
tokenmix-bulk -n 5 --key-prefix prod
```

**Batch headless dengan worker**

```bash
tokenmix-bulk -n 10 -c 2 --headless
```

**File konfigurasi**

```bash
tokenmix-bulk --config config.example.json
```

## Keluaran

Setiap proses menulis `accounts.json` dan `accounts.csv` berisi email, kata sandi, API key, dan status tiap akun.

## Memakai API key

TokenMix kompatibel dengan OpenAI, base URL `https://api.tokenmix.ai/v1`.

```bash
curl https://api.tokenmix.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-tm-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}'
```

## Pengembangan

```bash
pip install -e ".[dev]"
python -m pytest
```

## Lisensi

Dirilis di bawah Lisensi MIT.
