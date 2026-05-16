from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from utils.test_data import TestData
from utils.helpers import take_screenshot


def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()

        login = LoginPage(page)

        login.navigate()
        login.login(TestData.USERNAME, TestData.PASSWORD)
        page.wait_for_timeout(5000)

        assert "dashboard" in page.url.lower()
        take_screenshot(page, "after_login")
        print("Login successful")

        browser.close()
