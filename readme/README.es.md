<p align="center"><a href="../README.md">
  <img src="../assets/logo.png" alt="TokenMix Bulk Creator" width="150">
</a></p>

<p align="center"><img src="../assets/banner.png" alt="TokenMix Bulk Creator banner"></p>

<p align="center"><a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a> <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/playwright-%E2%9C%94-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a> <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-22e6a5?style=for-the-badge" alt="MIT License"></a> <img src="https://img.shields.io/badge/tests-7%20passed-39d0ff?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests"> <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-7c5cff?style=for-the-badge" alt="Platform"></p>

# TokenMix Bulk Account Creator

> Crea cuentas de TokenMix en lote con bandejas desechables y genera automáticamente claves API con nombres aleatorios.

<p><a href="../README.md">English</a> · <a href="README.id.md">Indonesia</a> · <a href="README.zh.md">简体中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <strong>Español</strong></p>

---

## ¿Por qué un navegador?

TokenMix protege el registro con un desafío de **Cloudflare Turnstile**. Un cliente HTTP simple es rechazado, así que este proyecto controla un navegador real con Playwright, resuelve el desafío de forma natural y luego ejecuta las llamadas REST autenticadas dentro de ese contexto.

## Características

- Bandeja temp-mail.io desechable por cuenta
- Consciente de Turnstile con tokens de un solo uso
- Nombres de usuario, contraseñas y claves aleatorios
- Claves API automáticas como `prod-swift-falcon-a1b2`
- Salida JSON + CSV incremental (a prueba de fallos)
- Concurrencia opcional y reintentos por cuenta

## Instalación

```bash
git clone https://github.com/0xgetz/tokenmix-bulk-creator.git
cd tokenmix-bulk-creator
python -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium
```

## Inicio rápido

**Una cuenta, navegador visible**

```bash
tokenmix-bulk --count 1
```

**Cinco cuentas, prefijo propio**

```bash
tokenmix-bulk -n 5 --key-prefix prod
```

**Lote headless con workers**

```bash
tokenmix-bulk -n 10 -c 2 --headless
```

**Archivo de configuración**

```bash
tokenmix-bulk --config config.example.json
```

## Salida

Cada ejecución escribe `accounts.json` y `accounts.csv` con el correo, la contraseña, la clave API y el estado de cada cuenta.

## Uso de una clave generada

TokenMix es compatible con OpenAI y su URL base es `https://api.tokenmix.ai/v1`.

```bash
curl https://api.tokenmix.ai/v1/chat/completions \
  -H "Authorization: Bearer sk-tm-..." \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"hello"}]}'
```

## Desarrollo

```bash
pip install -e ".[dev]"
python -m pytest
```

## Licencia

Publicado bajo la Licencia MIT.
