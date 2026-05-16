from playwright.sync_api import Page


class UserPage:

    def __init__(self, page: Page):
        self.page = page

    def fill_user_form(
        self,
        role,
        employee_name,
        status,
        username,
        password,
    ):

        dropdowns = self.page.locator(".oxd-select-text")

        # USER ROLE

        dropdowns.nth(0).click()

        self.page.locator(f".oxd-select-option:has-text('{role}')").click()

        self.page.wait_for_timeout(1000)

        # EMPLOYEE NAME

        employee_input = self.page.locator(".oxd-autocomplete-text-input input")

        employee_input.click()

        employee_input.fill(employee_name)

        print("Typed employee name")

        # wait for autocomplete suggestions
        self.page.wait_for_timeout(5000)

        # keyboard selection
        employee_input.press("ArrowDown")

        self.page.wait_for_timeout(1000)

        employee_input.press("Enter")

        print("Selected employee from dropdown")

        self.page.wait_for_timeout(2000)

        # STATUS

        dropdowns.nth(1).click()

        self.page.locator(f".oxd-select-option:has-text('{status}')").click()

        self.page.wait_for_timeout(1000)

        # USERNAME

        username_input = self.page.locator(
            ".oxd-input-group:has(label:text('Username')) input"
        )

        username_input.fill(username)

        # PASSWORD

        password_fields = self.page.locator("input[type='password']")

        password_fields.first.fill(password)

        password_fields.nth(1).fill(password)

        self.page.wait_for_timeout(1000)

    def search_user_by_username(self, username):

        search_box = self.page.get_by_role("textbox").first

        search_box.fill(username)

        self.page.get_by_role("button", name="Search").click()

        self.page.wait_for_timeout(3000)

    def click_edit_user(self):

        self.page.locator("i.bi-pencil-fill").first.click()

    def click_delete_user(self):
        delete_button = self.page.locator("button:has(i.bi-trash)").first

        delete_button.scroll_into_view_if_needed()

        self.page.wait_for_timeout(2000)

        delete_button.click(force=True)

        print("Clicked delete icon")

        # wait for modal container
        self.page.wait_for_selector(".oxd-dialog-container", timeout=10000)

        print("Delete popup appeared")

    def confirm_delete(self):
        confirm_btn = self.page.locator(
            ".oxd-dialog-container button:has-text('Yes, Delete')"
        )

        confirm_btn.wait_for(state="visible", timeout=15000)

        confirm_btn.click(force=True)

        print("Delete confirmed")

        self.page.wait_for_timeout(5000)

    def get_success_message(self):

        toast = self.page.locator(".oxd-toast-content")

        toast.wait_for(timeout=10000)

        return toast.inner_text()
