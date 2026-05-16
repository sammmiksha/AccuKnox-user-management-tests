from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from pages.user_page import UserPage
from utils.test_data import TestData
from utils.helpers import take_screenshot


def test_search_user():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False, slow_mo=1000)

        page = browser.new_page()

        login = LoginPage(page)
        admin = AdminPage(page)
        user = UserPage(page)

        login.navigate()

        login.login(TestData.USERNAME, TestData.PASSWORD)

        admin.open_admin_module()

        # use stable existing username
        existing_user = "qa_user_6372"

        user.search_user_by_username(existing_user)

        page.wait_for_timeout(5000)

        result = page.locator(".oxd-table-body")

        assert existing_user in result.inner_text()

        take_screenshot(page, "after_search_user")

        print("User search successful")

        browser.close()
