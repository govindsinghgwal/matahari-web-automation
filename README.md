# Matahari Web UI Test Automation (Python + Playwright + Pytest)

A clean, production-ready starter for SDET-style UI automation.
Includes: Page Object Model, pytest, Playwright, GitHub Actions CI, Allure hooks, linting, and env config.

## Quickstart

1) **Prereqs**
   - Python 3.11+
   - Git
   - Chrome/Firefox installed (Playwright will download browsers too)
2) **Create & activate a virtual env** (use your preferred tool; example below uses `venv`):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```
3) **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install --with-deps
   ```
4) **Configure environment**
   - Copy `.env.example` to `.env` and set `BASE_URL` for the site under test (e.g., https://www.matahari.com).
5) **Run a smoke test (headless)**
   ```bash
   pytest -m smoke --base-url="$BASE_URL"
   ```
   Or headed:
   ```bash
   pytest -m smoke --base-url="$BASE_URL" --headed
   ```

## Project Layout

```text
matahari-tests/
├─ pages/              # Page Object Model classes
├─ tests/              # Tests grouped by suite (smoke/regression)
├─ utils/              # Helpers: config, waits, data factories
├─ .github/workflows/  # CI: GitHub Actions
├─ conftest.py         # Pytest fixtures & hooks
├─ pytest.ini          # Pytest config: markers, addopts
├─ requirements.txt    # Python deps
├─ .env.example        # Sample env vars for local/dev/ci
└─ README.md
```

## Useful Commands

- Run tests in parallel (auto-detect cores):
  ```bash
  pytest -n auto --base-url="$BASE_URL"
  ```
- Only smoke tests:
  ```bash
  pytest -m smoke --base-url="$BASE_URL"
  ```
- Generate Allure results locally:
  ```bash
  pytest --alluredir=allure-results --base-url="$BASE_URL"
  ```

## Next Steps (suggested)
- Create page objects for Home, Search, Product Details, Cart, Checkout.
- Add stable selectors (prefer ARIA roles or `data-testid` if available).
- Expand smoke coverage: open home, search, add to cart.
- Wire this repo to GitHub, enable CI with the included workflow.
- Add API helpers and fixtures for creating test data when needed.
