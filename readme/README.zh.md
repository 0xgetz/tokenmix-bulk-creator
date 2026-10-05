<p align="center"><a href="../README.md">
  <img src="../assets/logo.png" alt="TokenMix Bulk Creator" width="150">
</a></p>

<p align="center"><img src="../assets/banner.png" alt="TokenMix Bulk Creator banner"></p>

<p align="center"><a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a> <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/playwright-%E2%9C%94-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a> <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-22e6a5?style=for-the-badge" alt="MIT License"></a> <img src="https://img.shields.io/badge/tests-7%20passed-39d0ff?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"> <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-7c5cff?style=for-the-badge" alt="Platform"></p>

# TokenMix 批量账号创建器

> 使用一次性邮箱批量创建 TokenMix 账号，并自动生成随机命名的 API 密钥。

<p><a href="../README.md">English</a> · <a href="README.id.md">Indonesia</a> · <strong>简体中文</strong> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a></p>

---

## 为什么需要浏览器？

TokenMix 使用 **Cloudflare Turnstile** 验证来保护注册。普通 HTTP 客户端会被拒绝，因此本项目通过 Playwright 驱动真实浏览器，自然通过验证，然后在浏览器上下文中执行带认证的 REST 调用。

## 特性

- 为每个账号创建一次性 mail.tm 邮箱
- 感知 Turnstile，生成一次性令牌
- 随机用户名、密码与密钥名称
- 自动创建形如 `prod-swift-falcon-a1b2` 的 API 密钥
- 增量写入 JSON + CSV（防崩溃）
- 可选并发与每账号重试

## 安装

```bash
git clone https://github.com/0xgetz/tokenmix-bulk-creator.git
cd tokenmix-bulk-creator
python -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium
```

## 快速开始

**单账号，显示浏览器**

```bash
tokenmix-bulk --count 1
```

**五个账号，自定义前缀**

```bash
tokenmix-bulk -n 5 --key-prefix prod
```

**无头批量并启用并发**

```bash
tokenmix-bulk -n 10 -c 2 --headless
```

**配置文件**

```bash
tokenmix-bulk --config config.example.json
```

## 输出

每次运行都会写入 `accounts.json` 与 `accounts.csv`，包含每个账号的邮箱、密码、API 密钥和状态。

## 使用生成的密钥

TokenMix 兼容 OpenAI，基础地址为 `https://api.tokenmix.ai/v1`。

```bash
curl https://api.tokenmix.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-tm-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}'
```

## 开发

```bash
pip install -e ".[dev]"
python -m pytest
```

## 许可证

基于 MIT 许可证发布。
