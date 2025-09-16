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

    def close_popup(self):
        try:
            self.page.wait_for_selector('button[data-testid="closeButton"]', timeout=6000)
            self.page.click('button[data-testid="closeButton"]')
            print("✅ Popup closed")
        except TimeoutError:
            print("ℹ️ No popup appeared, continuing...")

    def search(self, term):
        self.page.fill("input[type='search'], input[name*='search' i]", term)
        self.page.press("input[type='search'], input[name*='search' i]", "Enter")

    def dismiss_overlay_if_present(self, timeout_ms: int = 8000) -> None:
        """Close/neutralize the marketing overlay if it appears so it can't intercept clicks."""
        try:
            self.page.wait_for_selector("#ins-frameless-overlay", timeout=timeout_ms)
        except PWTimeout:
            return 

       
        try:
            btn = self.page.locator("button[data-testid='closeButton']").first
            if btn.is_visible():
                btn.click(timeout=2000)
                return
        except Exception:
            pass

        self.page.evaluate(
            """() => {
                const sel = '#ins-frameless-overlay, div[id^="ins-"][data-camp-id]';
                document.querySelectorAll(sel).forEach(el => {
                  el.style.setProperty('pointer-events','none','important');
                  el.style.setProperty('display','none','important');
                });
            }"""
        )

    def click_account_icon_and_wait_login(self) -> None:
        """
        Click the account nav (desktop or mobile). If UI is blocked, fall back to direct URL.
        Must end on /account* without throwing.
        """
        self.dismiss_overlay_if_present()

        # Desktop account icon
        account_desktop = self.page.locator(
            "a.site-nav__link.site-nav__link--icon.small--hide.header-account-icon"
        ).first

        menu_toggle = self.page.locator(
            "button[aria-label*='menu' i], "
            "button[aria-controls*='menu' i], "
            "a.site-nav__link--menu, "
            "button.js-drawer-open-nav, "
            "button.mobile-nav__toggle"
        ).first

        account_mobile = self.page.locator(
            "a[href='/account'], a[href*='/account/login'], a:has-text('Masuk')"
        ).first

        try:
            if account_desktop.is_visible():
                try:
                    account_desktop.click(timeout=5000)
                except PWTimeout:
                    self.dismiss_overlay_if_present()
                    account_desktop.click(force=True, timeout=5000)
            else:
                if menu_toggle.is_visible():
                    menu_toggle.click(timeout=4000)
                    self.page.wait_for_selector(
                        "#NavDrawer, .mobile-nav, [data-drawer], .drawer--active",
                        timeout=6000
                    )
                    if account_mobile.is_visible():
                        account_mobile.click(timeout=5000)
                    else:
                        self.page.goto(self.base_url + "/account/login", wait_until="domcontentloaded")
                else:
                    self.page.goto(self.base_url + "/account/login", wait_until="domcontentloaded")

        except Exception:
            self.page.goto(self.base_url + "/account/login", wait_until="domcontentloaded")

        try:
            self.page.wait_for_selector("input[name='customer[email]']", timeout=15000)
        except PWTimeout:
            self.page.wait_for_url("**/account/**", timeout=15000)
        assert "/account" in self.page.url
    
 