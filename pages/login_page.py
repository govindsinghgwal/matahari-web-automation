
from __future__ import annotations
import re
from contextlib import suppress
from playwright.sync_api import Page, expect, TimeoutError as PWTimeout

LOGIN_URL = "https://matahari.com/account/login?return_url=%2Faccount"

class Loginpage:
    def __init__(self, page: Page, login_url: str = LOGIN_URL):
        self.page = page
        self.login_url = (login_url or LOGIN_URL).rstrip("/")

        self._root           = "#CustomerLoginForm"
        self._dial_select    = f"{self._root} #MobileCountryCode"
        self._phone_input    = f"{self._root} #AddressPhoneNew"
        self._email_input    = f"{self._root} #CustomerEmail"
        self._password_input = f"{self._root} #CreatePassword"
        self._submit_phone   = f"{self._root} form.phonenumber-login button[type='submit']"
        self._email_toggle   = ".btn.btn--full.btn--secondary.toggle-login"

        self._phone_form = lambda: self.page.locator(f"{self._root} form").filter(
            has=self.page.locator("#AddressPhoneNew")
        ).first
        self._email_form = lambda: self.page.locator(f"{self._root} form").filter(
            has=self.page.locator("#CustomerEmail")
        ).first

    def goto(self) -> None:
        self.page.goto(self.login_url, wait_until="domcontentloaded")
        with suppress(Exception):
            self.page.get_by_role("button", name=re.compile(r"close|tutup", re.I)).click(timeout=600)
        self._dismiss_banner_fast()

    def _dismiss_banner_fast(self) -> None:
        selectors = [
            "span.ins-web-opt-in-reminder-close-button",
            "[class*='ins-web-opt-in-reminder-close-button']",
            "button:has-text('Saya Mengerti')",
            "[aria-label='Close']",
            ".modal__close, .popup__close, .overlay-close, .btn-close",
        ]
        for sel in selectors:
            with suppress(Exception):
                self.page.locator(sel).first.click(timeout=300, force=True); return
            for fr in self.page.frames:
                with suppress(Exception):
                    fr.locator(sel).first.click(timeout=300, force=True); return

        with suppress(Exception):
            w = self.page.evaluate("() => innerWidth")
            h = self.page.evaluate("() => innerHeight")
            self.page.mouse.click(int(w*0.5), int(h*0.5))
        with suppress(Exception):
            self.page.keyboard.press("Escape")

    def is_loaded(self) -> bool:
        with suppress(PWTimeout):
            self.page.locator(f"{self._root} form").first.wait_for(timeout=4000)
        expect(self.page.locator("body")).to_be_visible()
        return True

    def select_dial_code(self, code: str = "+91") -> None:
        el = self.page.locator(self._dial_select)
        el.wait_for(state="visible", timeout=4000)
        with suppress(Exception):
            el.select_option(code); return
        with suppress(Exception):
            el.select_option(code.lstrip("+")); return
        with suppress(Exception):
            digits = re.sub(r"\D", "", code)
            el.select_option(label=re.compile(fr"\+?{re.escape(digits)}")); return
        raise AssertionError(f"Could not select dial code {code}")

    def switch_to_email_login(self) -> None:
        with suppress(Exception):
            self.page.locator(self._email_toggle).click(timeout=600); return
        with suppress(Exception):
            self.page.get_by_role("button", name=re.compile(r"masuk.*email", re.I)).click(timeout=800)

    def fill_phone(self, phone: str) -> None:
        self._phone_form().locator("#AddressPhoneNew").fill(phone)

    def fill_email(self, email: str) -> None:
        self._email_form().locator("#CustomerEmail").fill(email)

    def fill_password(self, password: str, *, mode: str = "phone") -> None:
        form = self._phone_form() if mode == "phone" else self._email_form()
        form.locator("#CreatePassword").fill(password)

    def wait_until_logged_in(self, timeout: int = 9000) -> None:
        self.page.wait_for_url(re.compile(r"/account(?!/login)"), timeout=timeout)

    def is_logged_in(self) -> bool:
        url = str(self.page.url)
        return "/account" in url and "/login" not in url

    def login_with_phone(self, phone: str, password: str, dial_code: str = "+91") -> None:
        self._dismiss_banner_fast()
        self.select_dial_code(dial_code)
        self.fill_phone(phone)
        self.fill_password(password, mode="phone")

        try:
            with self.page.expect_navigation(url=re.compile(r"/account(?!/login)"), timeout=9000):
                self._phone_form().locator("button[type='submit']").click()
        except Exception:
            with suppress(Exception):
                self.wait_until_logged_in(timeout=9000)

    def login_with_email(self, email: str, password: str) -> None:
        self._dismiss_banner_fast()
        self.switch_to_email_login()

        email_form = self._email_form()
        email_form.locator("#CustomerEmail").wait_for(state="visible", timeout=3000)
        email_form.locator("#CreatePassword").wait_for(state="visible", timeout=3000)

        email_form.locator("#CustomerEmail").fill(email)
        email_form.locator("#CreatePassword").fill(password)

        try:
            with self.page.expect_navigation(url=re.compile(r"/account(?!/login)"), timeout=9000):
                email_form.locator("button[type='submit']").click()
        except Exception:
            with suppress(Exception):
                self.wait_until_logged_in(timeout=9000)

