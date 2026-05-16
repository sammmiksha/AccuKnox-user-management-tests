import os
from datetime import datetime


def take_screenshot(page, test_name):

    os.makedirs("screenshots", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    path = f"screenshots/" f"{test_name}_{timestamp}.png"

    page.screenshot(path=path)

    print(f"Screenshot saved: {path}")
