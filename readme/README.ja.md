<p align="center"><a href="../README.md">
  <img src="../assets/logo.png" alt="TokenMix Bulk Creator" width="150">
</a></p>

<p align="center"><img src="../assets/banner.png" alt="TokenMix Bulk Creator banner"></p>

<p align="center"><a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a> <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/playwright-%E2%9C%94-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a> <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-22e6a5?style=for-the-badge" alt="MIT License"></a> <img src="https://img.shields.io/badge/tests-7%20passed-39d0ff?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"> <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-7c5cff?style=for-the-badge" alt="Platform"></p>

# TokenMix 一括アカウント作成ツール

> 使い捨て受信トレイで TokenMix アカウントを一括作成し、ランダム名の API キーを自動生成します。

<p><a href="../README.md">English</a> · <a href="README.id.md">Indonesia</a> · <a href="README.zh.md">简体中文</a> · <strong>日本語</strong> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a></p>

---

## なぜブラウザが必要か

TokenMix は登録を **Cloudflare Turnstile** で保護しています。通常の HTTP クライアントは拒否されるため、本プロジェクトは Playwright で実ブラウザを操作し、チャレンジを自然に通過してから、認証済み REST 呼び出しをブラウザコンテキスト内で実行します。

## 機能

- アカウントごとに mail.tm の使い捨て受信トレイ
- Turnstile 対応の単発トークン生成
- ランダムなユーザー名・パスワード・キー名
- `prod-swift-falcon-a1b2` 形式の API キーを自動作成
- JSON + CSV の逐次出力（クラッシュ耐性）
- 任意の並列実行とアカウント単位の再試行

## インストール

```bash
git clone https://github.com/0xgetz/tokenmix-bulk-creator.git
cd tokenmix-bulk-creator
python -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium
```

## クイックスタート

**1アカウント・ブラウザ表示**

```bash
tokenmix-bulk --count 1
```

**5アカウント・接頭辞指定**

```bash
tokenmix-bulk -n 5 --key-prefix prod
```

**ヘッドレス並列バッチ**

```bash
tokenmix-bulk -n 10 -c 2 --headless
```

**設定ファイル**

```bash
tokenmix-bulk --config config.example.json
```

## 出力

各実行は `accounts.json` と `accounts.csv` を書き出し、各アカウントのメール・パスワード・API キー・状態を含みます。

## 生成したキーの使用

TokenMix は OpenAI 互換で、ベース URL は `https://api.tokenmix.ai/v1` です。

```bash
curl https://api.tokenmix.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-tm-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}'
```

## 開発

```bash
pip install -e ".[dev]"
python -m pytest
```

## ライセンス

MIT ライセンスで公開されています。
