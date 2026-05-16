# AccuKnox-user-management-tests

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.44.0-green)](https://playwright.dev/python/)
[![Pytest](https://img.shields.io/badge/pytest-8.2.0-orange)](https://docs.pytest.org/)

End-to-end automated tests for the **OrangeHRM User Management Module** plus
**Linux system-health and application-health monitoring scripts**.

---

## Repository Structure

```
AccuKnox-user-management-tests/
│
├── playwright-automation/          # Problem Statement 1 — E2E Tests
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── login_page.py           # Page Object: Login
│   │   └── user_management_page.py # Page Object: Admin / User Management
│   ├── tests/
│   │   └── test_user_management.py # 10 test cases (TC-UM-01 to TC-UM-10)
│   ├── conftest.py                 # Fixtures & shared test data
│   ├── pytest.ini                  # Pytest configuration
│   └── requirements.txt            # Python dependencies
│
├── scripts/                        # Problem Statement 2 — Bash/Python Scripts
│   ├── system_health_monitor.py    # Objective 1: System Health Monitor
│   └── app_health_checker.py       # Objective 4: Application Health Checker
│
└── README.md
```

---

## Problem Statement 1 — User Management E2E Tests

### Application Under Test (AUT)

| Item       | Value                                                                 |
|------------|-----------------------------------------------------------------------|
| URL        | https://opensource-demo.orangehrmlive.com/web/index.php/auth/login   |
| Username   | `Admin`                                                               |
| Password   | `admin123`                                                            |

### Test Cases Automated

| ID        | Scenario                                       |
|-----------|------------------------------------------------|
| TC-UM-01  | Navigate to Admin Module                       |
| TC-UM-02  | Add a New User — Valid Data                    |
| TC-UM-03  | Add New User — Duplicate Username Validation   |
| TC-UM-04  | Add New User — Required Field Validation       |
| TC-UM-05  | Search Newly Created User by Username          |
| TC-UM-06  | Search User — No Results Found                 |
| TC-UM-07  | Edit User — Change Role, Status, Username      |
| TC-UM-08  | Validate Updated User Details Persist          |
| TC-UM-09  | Delete a Single User                           |
| TC-UM-10  | Cancel Delete Operation                        |

### Prerequisites

- **Python 3.11+** installed and available on your PATH
- **pip** package manager

### Project Setup Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/AccuKnox-user-management-tests.git
cd AccuKnox-user-management-tests/playwright-automation

# 2. Create and activate a virtual environment (recommended)
python -m venv venv

# On Linux / macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers (Chromium only is sufficient)
playwright install chromium

# 5. (Optional) Install system dependencies for Playwright on Linux
playwright install-deps chromium
```

### How to Run the Tests

```bash
# Navigate to the automation directory
cd playwright-automation

# Run all 10 tests (headless, verbose output)
pytest

# Run in headed mode (see the browser)
pytest --headed

# Run a specific test by ID
pytest tests/test_user_management.py::test_tc_um_01_navigate_to_admin_module

# Run tests and generate an HTML report
pytest --html=reports/test_report.html --self-contained-html

# Run with slower execution (good for demos)
pytest --headed --slowmo 500
```

### Playwright Version

```
playwright==1.44.0
pytest-playwright==0.5.0
```

Check installed version:
```bash
playwright --version
```

### Design Decisions

- **Page Object Model (POM)**: All selectors and actions are encapsulated in
  `pages/login_page.py` and `pages/user_management_page.py`.
- **Isolation**: Each test function gets a fresh browser context via the
  `page` fixture in `conftest.py` — no state leaks between tests.
- **Meaningful selectors**: Uses visible text, ARIA roles, and label-based
  selectors in preference to fragile CSS class names.
- **Waits**: `wait_for_load_state("networkidle")`, `wait_for_url()`, and
  `wait_for_selector()` are used instead of hard `sleep()` calls.
- **Cleanup**: TC-UM-02 cleans up any stale test user before creating a new
  one, making the suite idempotent.

---

## Problem Statement 2 — System Scripts

### Objective 1 — System Health Monitor

```bash
cd scripts

# Install dependency
pip install psutil

# Run once and exit
python system_health_monitor.py --once

# Monitor every 30 seconds, write alerts to custom log
python system_health_monitor.py --interval 30 --log my_health.log
```

**What it monitors:**

| Metric              | Default Threshold |
|---------------------|:-----------------:|
| CPU Usage (%)        | 80 %             |
| Memory Usage (%)     | 80 %             |
| Disk Usage (/)       | 85 %             |
| Running Processes    | 300              |

**Sample Output:**
```
2024-06-01 10:00:00 [INFO] =================================================================
2024-06-01 10:00:00 [INFO] System Health Check — 2024-06-01 10:00:00
2024-06-01 10:00:01 [INFO] ✔  OK    — CPU Usage: 23.4% (threshold: 80.0%)
2024-06-01 10:00:01 [INFO] ✔  OK    — Memory Usage: 61.2% (threshold: 80.0%)
2024-06-01 10:00:01 [INFO] ✔  OK    — Disk Usage (/): 54.0% (threshold: 85.0%)
2024-06-01 10:00:01 [WARNING] ⚠  ALERT — Running Processes: 312 (threshold: 300)
2024-06-01 10:00:01 [WARNING] SUMMARY: 1 alert(s) detected!
```

---

### Objective 4 — Application Health Checker

```bash
cd scripts

# Check default URLs (OrangeHRM + control endpoints)
python app_health_checker.py --once

# Check custom URLs
python app_health_checker.py --urls https://example.com https://myapp.io --once

# Watch mode — check every 60 seconds
python app_health_checker.py --interval 60 --log app_health.log

# Check URLs from a text file (one URL per line)
python app_health_checker.py --config urls.txt --once
```

**Status Definitions:**

| Status     | Meaning                                                  |
|------------|----------------------------------------------------------|
| `✔ UP`     | HTTP 2xx + optional keyword found in response body       |
| `⚠ DEGRADED` | HTTP 3xx/4xx, or keyword missing on an otherwise 200 page |
| `✗ DOWN`   | HTTP 5xx, connection refused, timeout, or DNS failure    |

**Sample Output:**
```
[✔ UP]       OrangeHRM Demo  HTTP 200   432.1 ms    | keyword: ✔
[✔ UP]       HTTPStat 200    HTTP 200   123.4 ms
[✗ DOWN]     HTTPStat 503    HTTP 503   89.2 ms
TOTAL: 3 checked  |  ✔ Up: 2  |  ⚠ Degraded: 0  |  ✗ Down: 1
```

Exit code is `1` if any application is DOWN (useful for CI/CD integration).

---

## Bugs / Observations Encountered During Testing

| # | Observation | Severity |
|---|-------------|----------|
| 1 | Employee Name auto-complete only accepts names of **existing PIM employees** — cannot type arbitrary names. Pre-condition: employee must exist in PIM. | Medium |
| 2 | Demo instance does not enforce password complexity rules (e.g., allows simple passwords). | Low |
| 3 | Confirmation dialog reads "Are you Sure?" (capital S in "Sure") — possible typo in OrangeHRM UI. | Info |
| 4 | Username search is case-insensitive — documented behaviour, not a defect. | Info |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-test`
3. Commit your changes: `git commit -m 'Add TC-UM-11'`
4. Push the branch: `git push origin feature/my-new-test`
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) for details.
