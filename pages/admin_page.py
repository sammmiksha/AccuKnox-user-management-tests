from playwright.sync_api import Page


class AdminPage:

    def __init__(self, page: Page):

        self.page = page

    def open_admin_module(self):

        self.page.wait_for_timeout(5000)

        admin_menu = self.page.get_by_role("link", name="Admin")

        admin_menu.wait_for(timeout=30000)

        # force click bypasses UI overlay issues
        admin_menu.click(force=True)

        print("Clicked Admin menu")

        self.page.wait_for_timeout(5000)

    def click_add_user(self):

        add_button = self.page.get_by_role("button", name="Add")

        add_button.wait_for(timeout=30000)

        add_button.click(force=True)

        print("Clicked Add button")

        self.page.wait_for_timeout(3000)

    def save_user(self):

        save_button = self.page.get_by_role("button", name="Save")

        save_button.wait_for(timeout=30000)

        save_button.click(force=True)

        print("Clicked Save")

        self.page.wait_for_timeout(5000)
