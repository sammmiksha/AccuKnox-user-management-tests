from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from pages.user_page import UserPage
from utils.test_data import TestData
from utils.helpers import take_screenshot


def test_edit_user():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()

        login = LoginPage(page)
        admin = AdminPage(page)
        user = UserPage(page)

        login.navigate()
        login.login(TestData.USERNAME, TestData.PASSWORD)

        admin.open_admin_module()

        user.search_user_by_username(TestData.TEST_USERNAME)

        user.click_edit_user()

        username_field = page.locator(
            ".oxd-input-group:has(label:text('Username')) input"
        )

        username_field.fill(TestData.UPDATED_USERNAME)

        admin.save_user()
        page.wait_for_timeout(5000)
        assert "viewSystemUsers" in page.url
        print("User edited successfully")
        take_screenshot(page, "after_edit_user")
        browser.close()
