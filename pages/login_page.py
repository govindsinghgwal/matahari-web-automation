from __future__ import annotations
import re
from contextlib import suppress
from playwright.sync_api import Page, expect, TimeoutError as PWTimeout

try:
    from utils.config import settings
except Exception:
    settings = None

class Loginpage:
    def __init__(self, page: Page, login_url: str | None = None):
        self.page = page
        if login_url:
            resolved = login_url
        elif settings and getattr(settings, "login_url", None):
            resolved = settings.login_url
        elif settings and getattr(settings, "base_url", None):
            base = settings.base_url.rstrip("/")
            resolved = f"{base}/account/login?return_url=%2Faccount"
        else:
            raise ValueError(
                "Login URL not provided and config.settings not available. "
                "Pass login_url explicitly or expose settings.login_url/base_url."
            )
        self.login_url = resolved.rstrip("/")

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

    # ---------- navigation ----------
    def goto(self) -> None:
        self.page.goto(self.login_url, wait_until="domcontentloaded")
        with suppress(Exception):
            self.page.get_by_role("button", name=re.compile(r"close|tutup", re.I)).click(timeout=600)
        self._dismiss_banner_fast()

    # ---------- banner handling ----------
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
        with suppress(Exception):
            h = self.page.evaluate("() => innerHeight")
        with suppress(Exception):
            self.page.mouse.click(int(w*0.5), int(h*0.5))
        with suppress(Exception):
            self.page.keyboard.press("Escape")

    # ---------- page state ----------
    def is_loaded(self) -> bool:
        with suppress(PWTimeout):
            self.page.locator(f"{self._root} form").first.wait_for(timeout=4000)
        expect(self.page.locator("body")).to_be_visible()
        return True

    # ---------- low-level actions ----------
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

    # ---------- helpers ----------
    def wait_until_logged_in(self, timeout: int = 9000) -> None:
        self.page.wait_for_url(re.compile(r"/account(?!/login)"), timeout=timeout)

    def is_logged_in(self) -> bool:
        url = str(self.page.url)
        return "/account" in url and "/login" not in url

    def _dump_login_errors(self) -> None:
        """Log common inline error messages shown by the site."""
        selectors = [
            ".form-message--error",
            ".field__message--error",
            ".errors",
            "[data-error]",
            "[role='alert']",
        ]
        for sel in selectors:
            with suppress(Exception):
                loc = self.page.locator(sel)
                if loc.first.is_visible():
                    texts = loc.all_inner_texts()
                    if texts:
                        print(f"[login error:{sel}]", " | ".join(t.strip() for t in texts if t.strip()))

    # ---------- flows (return bool) ----------
    def login_with_phone(self, phone: str, password: str, dial_code: str = "+91") -> bool:
        self._dismiss_banner_fast()
        self.select_dial_code(dial_code)
        self.fill_phone(phone)
        self.fill_password(password, mode="phone")

        # Try to observe the POST first (fast), then fall back to URL wait
        submitted = False
        with suppress(Exception):
            with self.page.expect_response(lambda r: r.request.method == "POST" and "/account/login" in r.url, timeout=10000):
                self._phone_form().locator("button[type='submit']").click()
                submitted = True
        if not submitted:
            self._phone_form().locator("button[type='submit']").click()

        with suppress(Exception):
            self.wait_until_logged_in(timeout=9000)

        ok = self.is_logged_in()
        if not ok:
            print("[login debug] still on:", self.page.url)
            self._dump_login_errors()
        return ok

    def login_with_email(self, email: str, password: str) -> bool:
        self._dismiss_banner_fast()
        self.switch_to_email_login()
        email_form = self._email_form()
        email_form.locator("#CustomerEmail").wait_for(state="visible", timeout=3000)
        email_form.locator("#CreatePassword").wait_for(state="visible", timeout=3000)
        email_form.locator("#CustomerEmail").fill(email)
        email_form.locator("#CreatePassword").fill(password)

        submitted = False
        with suppress(Exception):
            with self.page.expect_response(lambda r: r.request.method == "POST" and "/account/login" in r.url, timeout=10000):
                email_form.locator("button[type='submit']").click()
                submitted = True
        if not submitted:
            email_form.locator("button[type='submit']").click()

        with suppress(Exception):
            self.wait_until_logged_in(timeout=9000)

        ok = self.is_logged_in()
        if not ok:
            print("[login debug] still on:", self.page.url)
            self._dump_login_errors()
        return ok
