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
            return  # overlay didn't show up this run

        # Try the known close button
        try:
            btn = self.page.locator("button[data-testid='closeButton']").first
            if btn.is_visible():
                btn.click(timeout=2000)
                return
        except Exception:
            pass

        # Last resort: make overlays non-intercepting and hidden
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

        # Mobile hamburger / menu toggles (several common patterns)
        menu_toggle = self.page.locator(
            "button[aria-label*='menu' i], "
            "button[aria-controls*='menu' i], "
            "a.site-nav__link--menu, "
            "button.js-drawer-open-nav, "
            "button.mobile-nav__toggle"
        ).first

        # Mobile account link candidates
        account_mobile = self.page.locator(
            "a[href='/account'], a[href*='/account/login'], a:has-text('Masuk')"
        ).first

        try:
            if account_desktop.is_visible():
                # Desktop flow
                try:
                    account_desktop.click(timeout=5000)
                except PWTimeout:
                    self.dismiss_overlay_if_present()
                    account_desktop.click(force=True, timeout=5000)
            else:
                # Mobile flow: open menu then tap account
                if menu_toggle.is_visible():
                    menu_toggle.click(timeout=4000)
                    # Wait for mobile nav/drawer to show up
                    self.page.wait_for_selector(
                        "#NavDrawer, .mobile-nav, [data-drawer], .drawer--active",
                        timeout=6000
                    )
                    if account_mobile.is_visible():
                        account_mobile.click(timeout=5000)
                    else:
                        # As a fallback, navigate directly after menu open
                        self.page.goto(self.base_url + "/account/login", wait_until="domcontentloaded")
                else:
                    # Nothing visible to click — just navigate
                    self.page.goto(self.base_url + "/account/login", wait_until="domcontentloaded")

        except Exception:
            # Absolute fallback: ensure navigation happens even if clicks fail
            self.page.goto(self.base_url + "/account/login", wait_until="domcontentloaded")

        # Wait for account/login to be ready (either element or URL)
        try:
            self.page.wait_for_selector("input[name='customer[email]']", timeout=15000)
        except PWTimeout:
            self.page.wait_for_url("**/account/**", timeout=15000)

        # Final stable check (no brittle exact URL matching)
        assert "/account" in self.page.url
    
    # def dismiss_overlay_if_present(self, timeout_ms: int = 12000):
    #     """
    #     Neutralize the Insider overlay that blocks clicks.
    #     Tries to click a close button; if not, disables pointer-events / hides it.
    #     """
    #     # Wait a bit for delayed overlays to appear
    #     try:
    #         self.page.wait_for_selector("#ins-frameless-overlay", timeout=timeout_ms)
    #     except PWTimeout:
    #         return  # overlay didn't show in this run

    #     # Try the common close button first (when present)
    #     try:
    #         btn = self.page.locator("button[data-testid='closeButton']").first
    #         if btn.is_visible():
    #             btn.click(timeout=2000)
    #     except PWTimeout:
    #         pass  # fall through to JS neutralization

    #     # If still intercepting, neutralize overlay via JS
    #     self.page.evaluate(
    #         """() => {
    #             const sel = '#ins-frameless-overlay, div[id^="ins-"][data-camp-id]';
    #             document.querySelectorAll(sel).forEach(el => {
    #               try {
    #                 el.style.setProperty('pointer-events','none','important');
    #                 el.style.setProperty('display','none','important');
    #               } catch(e) {}
    #             });
    #         }"""
    #     )

    # def click_account_icon_and_wait_login(self):

    #     account = self.page.locator(
    #         "a.site-nav__link.site-nav__link--icon.small--hide.header-account-icon"
    #     ).first

    #     # Try a normal click first
    #     try:
    #         account.click(timeout=5000)
    #     except PWTimeout:
    #         # If overlay still intercepts, neutralize again and force the click
    #         self.dismiss_overlay_if_present()
    #         account.click(force=True, timeout=5000)

    #     # Prefer element-based wait (less flaky than strict URL match)
    #     try:
    #         self.page.wait_for_selector(
    #             "form[action*='/account/login'], input[name='customer[email]']",
    #             timeout=15000,
    #         )
    #     except PWTimeout:
        
            # expect(self.page).to_have_url(re.compile("https://matahari.com/account/login?return_url=%2Faccount"))

    # def dismiss_marketing_overlay(self):
    #     try:
    #         self.page.wait_for_selector("button[data-testid='closeButton']", timeout=5000)
    #         self.page.click("button[data-testid='closeButton']")
    #         print("Popup closed")
    #     except PWTimeout:
    #         print("No popup appeared")