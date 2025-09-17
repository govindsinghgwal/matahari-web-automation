from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        page = browser.new_page()

        # Go to home
        page.goto("https://matahari.com/")

        # Close popup if present
        try:
            page.get_by_role("button", name="Close").click(timeout=3000)
        except:
            pass

        # Click "Masuk"
        page.get_by_role("link", name="Masuk").click()

        # Sometimes a transparent overlay blocks clicks
        try:
            page.locator("#ins-frameless-overlay").click(timeout=2000)
        except:
            pass

        # Select India code +91
        page.locator("#CustomerLoginForm #MobileCountryCode").select_option("+91")

        # Fill phone number
        page.get_by_role("textbox", name="Telepon Telepon").fill("7088777287")

        # Fill password
        pw_field = page.locator("#CustomerLoginForm form").filter(
            has_text="Telepon Select a Country Code"
        ).locator("#CreatePassword")
        pw_field.fill("QWERTYUIOP")

        # Click Masuk
        page.get_by_role("button", name="Masuk").click()

        # Navigate to account page (after login succeeds)
        page.goto("https://matahari.com/account")

        # Click "Ubah Kontak" (first right-click, then normal click)
        page.get_by_role("button", name="Ubah Kontak").click(button="right")
        page.get_by_role("button", name="Ubah Kontak").click()

        # Keep browser open for a while
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    run()
