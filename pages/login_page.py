from playwright.sync_api import Page


class LoginPage:

    def __init__(self, page: Page):

        self.page = page

        self.url = (
            "https://opensource-demo.orangehrmlive.com/" "web/index.php/auth/login"
        )

    def navigate(self):

        self.page.goto(self.url, timeout=90000, wait_until="domcontentloaded")

        self.page.wait_for_timeout(5000)

    def login(self, username, password):

        username_input = self.page.locator("input[name='username']")

        password_input = self.page.locator("input[name='password']")

        username_input.wait_for(state="visible", timeout=30000)

        username_input.fill(username)

        password_input.fill(password)

        self.page.get_by_role("button", name="Login").click()

        self.page.wait_for_timeout(8000)

        print("Login successful")
