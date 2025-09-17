import pytest
from pages.login_page import Loginpage
from utils.config import settings




@pytest.mark.smoke
def test_can_open_loginpage(page):
    login = Loginpage(page, settings.login_url)
    login.goto()
    assert login.is_loaded()
    assert isinstance(page.title(), str) and len(page.title()) > 0

@pytest.mark.smoke
def test_login_with_phone_india(page):
    login = Loginpage(page, settings.login_url)
    login.goto()
    assert login.is_loaded()

    login.login_with_phone(phone=settings.phone, password=settings.password, dial_code="+91")
    assert login.is_logged_in(), f"Expected to be on account page, got {page.url}"

@pytest.mark.smoke
def test_login_with_email(page):
    login = Loginpage(page, settings.login_url)
    login.goto()
    assert login.is_loaded()

    login.login_with_email(email=settings.email, password=settings.password)
    assert login.is_logged_in(), f"Expected to be on account page, got {page.url}"
