
import re
import pytest
from playwright.sync_api import expect
from pages.login_page import Loginpage, LOGIN_URL

# Credentials you asked to use
PHONE_NUMBER = "7088777287"
EMAIL = "govindsinghgwal16@gmail.com"
PASSWORD = "QWERTYUIOP"

@pytest.mark.smoke
def test_can_open_loginpage(page):
    login = Loginpage(page, LOGIN_URL)
    login.goto()
    assert login.is_loaded()
    title = page.title()
    assert isinstance(title, str) and len(title) > 0

@pytest.mark.smoke
def test_login_with_phone_india(page):
    login = Loginpage(page, LOGIN_URL)
    login.goto()
    assert login.is_loaded()

    login.login_with_phone(phone=PHONE_NUMBER, password=PASSWORD, dial_code="+91")
    assert login.is_logged_in(), f"Expected to be on account page, got {page.url}"

@pytest.mark.smoke
def test_login_with_email(page):
    login = Loginpage(page, LOGIN_URL)
    login.goto()
    assert login.is_loaded()

    login.login_with_email(email=EMAIL, password=PASSWORD)
    assert login.is_logged_in(), f"Expected to be on account page, got {page.url}"



