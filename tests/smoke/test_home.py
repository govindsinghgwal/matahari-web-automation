import re
import pytest
from pages.home_page import HomePage
import time

@pytest.mark.smoke
def test_can_open_homepage(page, base_url):
    home = HomePage(page, base_url)
    home.goto()
    assert home.is_loaded()
    title = page.title()
    assert isinstance(title, str) and len(title) > 0

@pytest.mark.smoke
def test_search_smoke(page, base_url):
    home = HomePage(page, base_url)
    home.goto()
    home.search("dress")
    assert "dress" in page.url or "search" in page.url

import time
import pytest
from pages.home_page import HomePage

@pytest.mark.smoke
def test_login_navigation(page, base_url):
    home = HomePage(page, base_url)
    home.goto()
    home.dismiss_overlay_if_present()
    # Click account icon and wait for login/account page to be ready
    home.click_account_icon_and_wait_login()

    # home.dismiss_marketing_overlay()

    # page.click("a.site-nav__link.site-nav__link--icon.small--hide.header-account-icon", timeout=10000)

    # page.wait_for_url("**/login", timeout=15000)
    # assert "login" in page.url