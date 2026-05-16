import random


class TestData:

    BASE_URL = "https://opensource-demo.orangehrmlive.com/" "web/index.php/auth/login"

    USERNAME = "Admin"
    PASSWORD = "admin123"

    ROLE = "ESS"
    EMPLOYEE_NAME = "sara"
    STATUS = "Enabled"

    RANDOM_ID = random.randint(1000, 9999)

    TEST_USERNAME = f"qa_user_{RANDOM_ID}"

    UPDATED_USERNAME = f"qa_updated_{RANDOM_ID}"

    TEST_PASSWORD = "Test@12345"
