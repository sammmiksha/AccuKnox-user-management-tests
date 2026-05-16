from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from pages.user_page import UserPage
from utils.helpers import take_screenshot


def test_validate_updated_user():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False, slow_mo=1000)

        page = browser.new_page()

        login = LoginPage(page)
        admin = AdminPage(page)
        user = UserPage(page)

        login.navigate()

        login.login("Admin", "admin123")

        admin.open_admin_module()

        user.search_user_by_username("Milan")

        page.wait_for_timeout(5000)

        table = page.locator(".oxd-table-body")

        table_text = table.inner_text()

        assert "Enabled" in table_text

        take_screenshot(page, "after_validate_updated_user")

        print("User validation successful")

        browser.close()
