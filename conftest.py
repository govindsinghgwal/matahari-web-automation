import os
import pytest
from dotenv import load_dotenv

load_dotenv()

# def pytest_addoption(parser):
#     parser.addoption(
#         "--base-url",
#         action="store",
#         default=os.getenv("BASE_URL", "https://www.matahari.com"),
#         help="Base URL of the site under test",
#     )
#     parser.addoption(
#         "--browser",
#         action="store",
#         default=os.getenv("BROWSER", "chromium"),
#         help="Playwright browser: chromium|firefox|webkit",
#     )
#     parser.addoption(
#         "--headed",
#         action="store_true",
#         default=(os.getenv("HEADLESS", "true").lower() == "false"),
#         help="Run headed mode",
#     )

@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("--base-url")

@pytest.fixture(scope="session")
def browser_name(pytestconfig):
    return pytestconfig.getoption("--browser")

# Reuse pytest-playwright fixtures: browser_type, browser, context, page
# We override to plug in base_url and headed as needed.
@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    return {
        "headless": not pytestconfig.getoption("--headed"),
    }

@pytest.fixture(scope="session")
def context_kwargs(base_url):
    # Propagate base_url to the context for page.goto(relative_url) convenience.
    return {"base_url": base_url}

@pytest.fixture
def goto_base(page, base_url):
    def _go(path: str = "/"):
        url = base_url.rstrip("/") + path
        return page.goto(url, wait_until="domcontentloaded")
    return _go
