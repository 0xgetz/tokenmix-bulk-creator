#!/usr/bin/env python3
"""Generate the six localised README files from a single template.

Run from the repository root:  python docs/build_readmes.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "0xgetz/tokenmix-bulk-creator"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"
ASSET = f"{RAW}/assets"

def badges(prefix: str) -> str:
    return (
        f'<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a> '
        f'<a href="https://playwright.dev/"><img src="https://img.shields.io/badge/playwright-%E2%9C%94-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a> '
        f'<a href="{prefix}LICENSE"><img src="https://img.shields.io/badge/license-MIT-22e6a5?style=for-the-badge" alt="MIT License"></a> '
        f'<img src="https://img.shields.io/badge/tests-7%20passed-39d0ff?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"> '
        f'<img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-7c5cff?style=for-the-badge" alt="Platform">'
    )

LANG_NAMES = [
    ("en", "English"),
    ("id", "Indonesia"),
    ("zh", "简体中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("es", "Español"),
]


def switcher(active: str) -> str:
    parts = []
    for code, name in LANG_NAMES:
        if code == "en":
            target = "README.md" if active == "en" else "../README.md"
        else:
            target = f"readme/README.{code}.md" if active == "en" else f"README.{code}.md"
        if code == active:
            parts.append(f"**{name}**")
        else:
            parts.append(f"[{name}]({target})")
    return " · ".join(parts)


TEMPLATES = {
    "en": {
        "title": "TokenMix Bulk Account Creator",
        "tagline": "Bulk-provision TokenMix accounts with disposable inboxes and auto-generate API keys that carry random names.",
        "why_h": "Why a browser?",
        "why_p": "TokenMix protects registration with a **Cloudflare Turnstile** challenge. A plain HTTP client is rejected, so this project drives a real browser with Playwright, solves the challenge naturally, then performs the authenticated REST calls from inside that browser context.",
        "features_h": "Features",
        "features": [
            "Disposable mail.tm inbox per account",
            "Turnstile-aware single-use token generation",
            "Random usernames, passwords and key names",
            "Auto-created API keys named like `prod-swift-falcon-a1b2`",
            "Incremental JSON + CSV output (crash-safe)",
            "Optional concurrency and per-account retries",
        ],
        "install_h": "Installation",
        "quick_h": "Quick start",
        "quick": [
            ("One account, browser visible", "tokenmix-bulk --count 1"),
            ("Five accounts, custom prefix", "tokenmix-bulk -n 5 --key-prefix prod"),
            ("Headless batch with workers", "tokenmix-bulk -n 10 -c 2 --headless"),
            ("Config file", "tokenmix-bulk --config config.example.json"),
        ],
        "output_h": "Output",
        "output_p": "Each run writes `accounts.json` and `accounts.csv` with the email, password, API key and status of every account.",
        "usage_h": "Using a generated key",
        "usage_p": "TokenMix is OpenAI-compatible with base URL `https://api.tokenmix.ai/v1`.",
        "dev_h": "Development",
        "license_h": "License",
        "license_p": "Released under the MIT License.",
    },
    "id": {
        "title": "TokenMix Bulk Account Creator",
        "tagline": "Buat akun TokenMix secara massal dengan inbox sekali pakai dan pembuatan API key otomatis bernama acak.",
        "why_h": "Mengapa pakai browser?",
        "why_p": "TokenMix melindungi pendaftaran dengan tantangan **Cloudflare Turnstile**. Klien HTTP biasa akan ditolak, sehingga proyek ini mengendalikan browser asli via Playwright, menyelesaikan tantangan secara alami, lalu menjalankan panggilan REST terautentikasi dari dalam konteks browser tersebut.",
        "features_h": "Fitur",
        "features": [
            "Inbox mail.tm sekali pakai untuk setiap akun",
            "Sadar Turnstile dengan token sekali pakai",
            "Username, kata sandi, dan nama key yang acak",
            "API key otomatis bernama seperti `prod-swift-falcon-a1b2`",
            "Output JSON + CSV bertahap (aman jika berhenti)",
            "Konkurensi opsional dan percobaan ulang per akun",
        ],
        "install_h": "Instalasi",
        "quick_h": "Mulai cepat",
        "quick": [
            ("Satu akun, browser terlihat", "tokenmix-bulk --count 1"),
            ("Lima akun, prefix khusus", "tokenmix-bulk -n 5 --key-prefix prod"),
            ("Batch headless dengan worker", "tokenmix-bulk -n 10 -c 2 --headless"),
            ("File konfigurasi", "tokenmix-bulk --config config.example.json"),
        ],
        "output_h": "Keluaran",
        "output_p": "Setiap proses menulis `accounts.json` dan `accounts.csv` berisi email, kata sandi, API key, dan status tiap akun.",
        "usage_h": "Memakai API key",
        "usage_p": "TokenMix kompatibel dengan OpenAI, base URL `https://api.tokenmix.ai/v1`.",
        "dev_h": "Pengembangan",
        "license_h": "Lisensi",
        "license_p": "Dirilis di bawah Lisensi MIT.",
    },
    "zh": {
        "title": "TokenMix 批量账号创建器",
        "tagline": "使用一次性邮箱批量创建 TokenMix 账号，并自动生成随机命名的 API 密钥。",
        "why_h": "为什么需要浏览器？",
        "why_p": "TokenMix 使用 **Cloudflare Turnstile** 验证来保护注册。普通 HTTP 客户端会被拒绝，因此本项目通过 Playwright 驱动真实浏览器，自然通过验证，然后在浏览器上下文中执行带认证的 REST 调用。",
        "features_h": "特性",
        "features": [
            "为每个账号创建一次性 mail.tm 邮箱",
            "感知 Turnstile，生成一次性令牌",
            "随机用户名、密码与密钥名称",
            "自动创建形如 `prod-swift-falcon-a1b2` 的 API 密钥",
            "增量写入 JSON + CSV（防崩溃）",
            "可选并发与每账号重试",
        ],
        "install_h": "安装",
        "quick_h": "快速开始",
        "quick": [
            ("单账号，显示浏览器", "tokenmix-bulk --count 1"),
            ("五个账号，自定义前缀", "tokenmix-bulk -n 5 --key-prefix prod"),
            ("无头批量并启用并发", "tokenmix-bulk -n 10 -c 2 --headless"),
            ("配置文件", "tokenmix-bulk --config config.example.json"),
        ],
        "output_h": "输出",
        "output_p": "每次运行都会写入 `accounts.json` 与 `accounts.csv`，包含每个账号的邮箱、密码、API 密钥和状态。",
        "usage_h": "使用生成的密钥",
        "usage_p": "TokenMix 兼容 OpenAI，基础地址为 `https://api.tokenmix.ai/v1`。",
        "dev_h": "开发",
        "license_h": "许可证",
        "license_p": "基于 MIT 许可证发布。",
    },
    "ja": {
        "title": "TokenMix 一括アカウント作成ツール",
        "tagline": "使い捨て受信トレイで TokenMix アカウントを一括作成し、ランダム名の API キーを自動生成します。",
        "why_h": "なぜブラウザが必要か",
        "why_p": "TokenMix は登録を **Cloudflare Turnstile** で保護しています。通常の HTTP クライアントは拒否されるため、本プロジェクトは Playwright で実ブラウザを操作し、チャレンジを自然に通過してから、認証済み REST 呼び出しをブラウザコンテキスト内で実行します。",
        "features_h": "機能",
        "features": [
            "アカウントごとに mail.tm の使い捨て受信トレイ",
            "Turnstile 対応の単発トークン生成",
            "ランダムなユーザー名・パスワード・キー名",
            "`prod-swift-falcon-a1b2` 形式の API キーを自動作成",
            "JSON + CSV の逐次出力（クラッシュ耐性）",
            "任意の並列実行とアカウント単位の再試行",
        ],
        "install_h": "インストール",
        "quick_h": "クイックスタート",
        "quick": [
            ("1アカウント・ブラウザ表示", "tokenmix-bulk --count 1"),
            ("5アカウント・接頭辞指定", "tokenmix-bulk -n 5 --key-prefix prod"),
            ("ヘッドレス並列バッチ", "tokenmix-bulk -n 10 -c 2 --headless"),
            ("設定ファイル", "tokenmix-bulk --config config.example.json"),
        ],
        "output_h": "出力",
        "output_p": "各実行は `accounts.json` と `accounts.csv` を書き出し、各アカウントのメール・パスワード・API キー・状態を含みます。",
        "usage_h": "生成したキーの使用",
        "usage_p": "TokenMix は OpenAI 互換で、ベース URL は `https://api.tokenmix.ai/v1` です。",
        "dev_h": "開発",
        "license_h": "ライセンス",
        "license_p": "MIT ライセンスで公開されています。",
    },
    "ko": {
        "title": "TokenMix 대량 계정 생성기",
        "tagline": "일회용 받은편지함으로 TokenMix 계정을 대량 생성하고 무작위 이름의 API 키를 자동 발급합니다.",
        "why_h": "왜 브라우저가 필요한가요?",
        "why_p": "TokenMix는 **Cloudflare Turnstile** 챌린지로 가입을 보호합니다. 일반 HTTP 클라이언트는 거부되므로, 이 프로젝트는 Playwright로 실제 브라우저를 구동해 챌린지를 자연스럽게 통과한 뒤 브라우저 컨텍스트에서 인증된 REST 호출을 수행합니다.",
        "features_h": "기능",
        "features": [
            "계정별 일회용 mail.tm 받은편지함",
            "Turnstile 대응 일회용 토큰 생성",
            "무작위 사용자명, 비밀번호, 키 이름",
            "`prod-swift-falcon-a1b2` 형식의 API 키 자동 생성",
            "JSON + CSV 점진적 저장(충돌 안전)",
            "선택적 병렬 처리 및 계정별 재시도",
        ],
        "install_h": "설치",
        "quick_h": "빠른 시작",
        "quick": [
            ("계정 1개, 브라우저 표시", "tokenmix-bulk --count 1"),
            ("계정 5개, 접두사 지정", "tokenmix-bulk -n 5 --key-prefix prod"),
            ("헤드리스 병렬 배치", "tokenmix-bulk -n 10 -c 2 --headless"),
            ("설정 파일", "tokenmix-bulk --config config.example.json"),
        ],
        "output_h": "출력",
        "output_p": "각 실행은 `accounts.json`과 `accounts.csv`를 기록하며 이메일, 비밀번호, API 키, 상태를 포함합니다.",
        "usage_h": "생성된 키 사용",
        "usage_p": "TokenMix는 OpenAI 호환이며 기본 URL은 `https://api.tokenmix.ai/v1`입니다.",
        "dev_h": "개발",
        "license_h": "라이선스",
        "license_p": "MIT 라이선스로 배포됩니다.",
    },
    "es": {
        "title": "TokenMix Bulk Account Creator",
        "tagline": "Crea cuentas de TokenMix en lote con bandejas desechables y genera automáticamente claves API con nombres aleatorios.",
        "why_h": "¿Por qué un navegador?",
        "why_p": "TokenMix protege el registro con un desafío de **Cloudflare Turnstile**. Un cliente HTTP simple es rechazado, así que este proyecto controla un navegador real con Playwright, resuelve el desafío de forma natural y luego ejecuta las llamadas REST autenticadas dentro de ese contexto.",
        "features_h": "Características",
        "features": [
            "Bandeja mail.tm desechable por cuenta",
            "Consciente de Turnstile con tokens de un solo uso",
            "Nombres de usuario, contraseñas y claves aleatorios",
            "Claves API automáticas como `prod-swift-falcon-a1b2`",
            "Salida JSON + CSV incremental (a prueba de fallos)",
            "Concurrencia opcional y reintentos por cuenta",
        ],
        "install_h": "Instalación",
        "quick_h": "Inicio rápido",
        "quick": [
            ("Una cuenta, navegador visible", "tokenmix-bulk --count 1"),
            ("Cinco cuentas, prefijo propio", "tokenmix-bulk -n 5 --key-prefix prod"),
            ("Lote headless con workers", "tokenmix-bulk -n 10 -c 2 --headless"),
            ("Archivo de configuración", "tokenmix-bulk --config config.example.json"),
        ],
        "output_h": "Salida",
        "output_p": "Cada ejecución escribe `accounts.json` y `accounts.csv` con el correo, la contraseña, la clave API y el estado de cada cuenta.",
        "usage_h": "Uso de una clave generada",
        "usage_p": "TokenMix es compatible con OpenAI y su URL base es `https://api.tokenmix.ai/v1`.",
        "dev_h": "Desarrollo",
        "license_h": "Licencia",
        "license_p": "Publicado bajo la Licencia MIT.",
    },
}


def render(code: str, t: dict, include_assets: bool) -> str:
    prefix = "" if code == "en" else "../"
    logo = f"{prefix}assets/logo.png" if include_assets else "assets/logo.png"
    banner = f"{prefix}assets/banner.png" if include_assets else "assets/banner.png"

    lines: list[str] = []
    lines.append(f'<p align="center"><a href="{prefix}README.md">')
    lines.append(f'  <img src="{logo}" alt="TokenMix Bulk Creator" width="150">')
    lines.append("</a></p>")
    lines.append("")
    lines.append(f'<p align="center"><img src="{banner}" alt="TokenMix Bulk Creator banner"></p>')
    lines.append("")
    lines.append(f'<p align="center">{badges(prefix)}</p>')
    lines.append("")
    lines.append(f"# {t['title']}")
    lines.append("")
    lines.append(f"> {t['tagline']}")
    lines.append("")
    lines.append(f"<p>{switcher(code)}</p>")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## {t['why_h']}")
    lines.append("")
    lines.append(t["why_p"])
    lines.append("")
    lines.append(f"## {t['features_h']}")
    lines.append("")
    for feature in t["features"]:
        lines.append(f"- {feature}")
    lines.append("")
    lines.append(f"## {t['install_h']}")
    lines.append("")
    lines.append("```bash")
    lines.append(f"git clone https://github.com/{REPO}.git")
    lines.append(f"cd {REPO.split('/')[-1]}")
    lines.append("python -m venv .venv && source .venv/bin/activate")
    lines.append("pip install -e .")
    lines.append("playwright install chromium")
    lines.append("```")
    lines.append("")
    lines.append(f"## {t['quick_h']}")
    lines.append("")
    for label, command in t["quick"]:
        lines.append(f"**{label}**")
        lines.append("")
        lines.append("```bash")
        lines.append(command)
        lines.append("```")
        lines.append("")
    lines.append(f"## {t['output_h']}")
    lines.append("")
    lines.append(t["output_p"])
    lines.append("")
    lines.append(f"## {t['usage_h']}")
    lines.append("")
    lines.append(t["usage_p"])
    lines.append("")
    lines.append("```bash")
    lines.append("curl https://api.tokenmix.ai/v1/chat/completions \\")
    lines.append('  -H "Authorization: Bearer sk-tm-..." \\')
    lines.append('  -H "Content-Type: application/json" \\')
    lines.append('  -d \'{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}\'')
    lines.append("```")
    lines.append("")
    lines.append(f"## {t['dev_h']}")
    lines.append("")
    lines.append("```bash")
    lines.append('pip install -e ".[dev]"')
    lines.append("python -m pytest")
    lines.append("```")
    lines.append("")
    lines.append(f"## {t['license_h']}")
    lines.append("")
    lines.append(t["license_p"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    (ROOT / "readme").mkdir(exist_ok=True)
    for code, template in TEMPLATES.items():
        include_assets = code != "en"
        content = render(code, template, include_assets)
        target = ROOT / "README.md" if code == "en" else ROOT / "readme" / f"README.{code}.md"
        target.write_text(content, encoding="utf-8")
        print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
