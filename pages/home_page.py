from playwright.sync_api import Page, expect
from playwright.sync_api import TimeoutError as PWTimeout

import re

class HomePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto(self):
        self.page.goto(self.base_url + "/", wait_until="domcontentloaded")

    def is_loaded(self):
        expect(self.page.locator("body")).to_be_visible()
        return True
    def close_popup(self, timeout_ms: int = 7000) -> None:
        overlay = self.page.locator("#ins-frameless-overlay")
        try:
           
            overlay.wait_for(state="attached", timeout=timeout_ms)
        except PWTimeout:
            return  

       
        try:
            btn = self.page.locator("button[data-testid='closeButton']").first
            if btn.is_visible():
                btn.click(timeout=2000)
                return
        except Exception:
            pass

        
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
        except Exception:
            pass


    # def close_popup(self):
    #     try:
    #         self.page.wait_for_selector('button[data-testid="closeButton"]', timeout=6000)
    #         self.page.click('button[data-testid="closeButton"]')
    #         print("✅ Popup closed")
    #     except TimeoutError:
    #         print("ℹ️ No popup appeared, continuing...")

    def search(self, term):
        self.page.fill("input[type='search'], input[name*='search' i]", term)
        self.page.press("input[type='search'], input[name*='search' i]", "Enter")

    def go_to_login(self) -> None:
        self.close_popup()

        account_icon = "a.site-nav__link.site-nav__link--icon.small--hide.header-account-icon"

        
        try:
            self.page.click(account_icon, timeout=5000)
        except Exception:
           
            self.close_discount_popup()
            self.page.keyboard.press("Escape")
            self.page.click(account_icon, force=True, timeout=5000)

       
        try:
            self.page.wait_for_selector(
                "form[action*='/account/login'], input[name='customer[email]']",
                timeout=15000,
            )
        except PWTimeout:
           
            self.page.wait_for_url("**/account/**", timeout=15000)

       
        assert "/account" in self.page.url

