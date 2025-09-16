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

@pytest.mark.smoke
def test_login_navigation(page, base_url):
    home = HomePage(page, base_url)
    home.goto()
    home.go_to_login()
