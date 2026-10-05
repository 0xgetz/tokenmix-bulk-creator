<p align="center"><a href="../README.md">
  <img src="../assets/logo.png" alt="TokenMix Bulk Creator" width="150">
</a></p>

<p align="center"><img src="../assets/banner.png" alt="TokenMix Bulk Creator banner"></p>

<p align="center"><a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a> <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/playwright-%E2%9C%94-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a> <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-22e6a5?style=for-the-badge" alt="MIT License"></a> <img src="https://img.shields.io/badge/tests-7%20passed-39d0ff?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"> <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-7c5cff?style=for-the-badge" alt="Platform"></p>

# TokenMix 대량 계정 생성기

> 일회용 받은편지함으로 TokenMix 계정을 대량 생성하고 무작위 이름의 API 키를 자동 발급합니다.

<p><a href="../README.md">English</a> · <a href="README.id.md">Indonesia</a> · <a href="README.zh.md">简体中文</a> · <a href="README.ja.md">日本語</a> · <strong>한국어</strong> · <a href="README.es.md">Español</a></p>

---

## 왜 브라우저가 필요한가요?

TokenMix는 **Cloudflare Turnstile** 챌린지로 가입을 보호합니다. 일반 HTTP 클라이언트는 거부되므로, 이 프로젝트는 Playwright로 실제 브라우저를 구동해 챌린지를 자연스럽게 통과한 뒤 브라우저 컨텍스트에서 인증된 REST 호출을 수행합니다.

## 기능

- 계정별 일회용 mail.tm 받은편지함
- Turnstile 대응 일회용 토큰 생성
- 무작위 사용자명, 비밀번호, 키 이름
- `prod-swift-falcon-a1b2` 형식의 API 키 자동 생성
- JSON + CSV 점진적 저장(충돌 안전)
- 선택적 병렬 처리 및 계정별 재시도

## 설치

```bash
git clone https://github.com/0xgetz/tokenmix-bulk-creator.git
cd tokenmix-bulk-creator
python -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium
```

## 빠른 시작

**계정 1개, 브라우저 표시**

```bash
tokenmix-bulk --count 1
```

**계정 5개, 접두사 지정**

```bash
tokenmix-bulk -n 5 --key-prefix prod
```

**헤드리스 병렬 배치**

```bash
tokenmix-bulk -n 10 -c 2 --headless
```

**설정 파일**

```bash
tokenmix-bulk --config config.example.json
```

## 출력

각 실행은 `accounts.json`과 `accounts.csv`를 기록하며 이메일, 비밀번호, API 키, 상태를 포함합니다.

## 생성된 키 사용

TokenMix는 OpenAI 호환이며 기본 URL은 `https://api.tokenmix.ai/v1`입니다.

```bash
curl https://api.tokenmix.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-tm-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}'
```

## 개발

```bash
pip install -e ".[dev]"
python -m pytest
```

## 라이선스

MIT 라이선스로 배포됩니다.
