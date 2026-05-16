from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from pages.user_page import UserPage
from utils.test_data import TestData
from utils.helpers import take_screenshot


def test_add_user():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False, slow_mo=1000)

        page = browser.new_page()

        login = LoginPage(page)
        admin = AdminPage(page)
        user = UserPage(page)

        login.navigate()

        login.login(TestData.USERNAME, TestData.PASSWORD)

        admin.open_admin_module()

        admin.click_add_user()

        user.fill_user_form(
            TestData.ROLE,
            TestData.EMPLOYEE_NAME,
            TestData.STATUS,
            TestData.TEST_USERNAME,
            TestData.TEST_PASSWORD,
        )

        admin.save_user()

        page.wait_for_timeout(5000)

        take_screenshot(page, "after_add_user")

        page.wait_for_timeout(5000)

        assert "viewSystemUsers" in page.url

        print("User added successfully")

        browser.close()
