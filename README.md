# AccuKnox-user-management-tests

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.44.0-green)](https://playwright.dev/python/)
[![Pytest](https://img.shields.io/badge/pytest-8.2.0-orange)](https://docs.pytest.org/)

Automation assessment project for the AccuKnox QA Trainee role.
Covers E2E test automation for the OrangeHRM User Management module and two
Linux system-monitoring scripts written in Python.

---

## Project Overview

**Problem Statement 1** — Automate user management workflows on a public demo
of OrangeHRM using Playwright + Pytest (Python), following the Page Object
Model pattern.

**Problem Statement 2** — Write Python scripts for system health monitoring
and application uptime checking.

---

## Tech Stack

- Python 3.11+
- Playwright 1.44.0
- pytest 8.2.0 / pytest-playwright 0.5.0
- psutil (for system monitoring scripts)

---

## Repository Structure

```
AccuKnox-user-management-tests/
│
├── pages/
│   ├── admin_page.py         # Page Object: Admin module
│   ├── login_page.py         # Page Object: Login screen
│   └── user_page.py          # Page Object: User form and actions
│
├── tests/
│   ├── test_login.py         # TC-UM-01: Navigate to Admin module
│   ├── test_add_user.py      # TC-UM-02 to TC-UM-04: Add user scenarios
│   ├── test_search_user.py   # TC-UM-05 to TC-UM-06: Search scenarios
│   ├── test_edit_user.py     # TC-UM-07: Edit user details
│   ├── test_validate_user.py # TC-UM-08: Validate updated details
│   └── test_delete_user.py   # TC-UM-09 to TC-UM-10: Delete scenarios
│
├── utils/
│   ├── helpers.py            # Shared helper functions
│   └── test_data.py          # Centralised test data
│
├── manual_test_cases/        # Manual test case document (Excel)
├── reports/                  # Pytest HTML reports (generated on run)
├── screenshots/              # Screenshots captured during test runs
│
├── scripts/
│   ├── system_health_monitor.py   # Problem 2, Obj 1: System Health Monitor
│   └── app_health_checker.py      # Problem 2, Obj 4: App Health Checker
│
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Problem Statement 1 — E2E Test Automation

### Application Under Test

| | |
|---|---|
| URL | https://opensource-demo.orangehrmlive.com/web/index.php/auth/login |
| Username | `Admin` |
| Password | `admin123` |

### Automated Test Scenarios

Tests are split into one file per feature area for clarity:

| File | Scenarios Covered |
|---|---|
| `test_login.py` | Login as Admin, navigate to Admin module |
| `test_add_user.py` | Add user with valid data, duplicate username error, required field validation |
| `test_search_user.py` | Search by username (found), search with no results |
| `test_edit_user.py` | Edit user role, status, and username |
| `test_validate_user.py` | Verify updated details persist after save |
| `test_delete_user.py` | Delete user and confirm removal, cancel delete |

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/sammmiksha/AccuKnox-user-management-tests.git
cd AccuKnox-user-management-tests

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright's Chromium browser
playwright install chromium

# On Linux you may also need:
playwright install-deps chromium
```

### Running the Tests

```bash
# Run all tests (headless by default)
pytest

# Run with a visible browser — good for demos and debugging
pytest --headed

# Slow the browser down so you can follow what's happening
pytest --headed --slowmo 500

# Run a single test file
pytest tests/test_add_user.py

# Run a single test by name
pytest tests/test_login.py::test_navigate_to_admin_module

# Generate an HTML report (saved to reports/)
pytest --html=reports/test_report.html --self-contained-html
```

### Playwright Version

```
playwright==1.44.0
```

Verify locally:
```bash
playwright --version
```

### Design Approach

**Page Object Model** — selectors and actions for each page live in their own
class under `pages/`. Tests import those classes and call methods rather than
writing raw Playwright code directly in the test file.

**One test file per feature** — splitting tests across `test_add_user.py`,
`test_search_user.py`, etc. makes it easier to run only the area you're
working on and keeps individual files short.

**Centralised test data** — `utils/test_data.py` holds usernames, passwords,
and other values used across tests. Changing test data means editing one file,
not hunting through every test.

**Selectors** — prefer visible text, ARIA roles, and label-based locators over
CSS class names where possible, since OrangeHRM's class names are sometimes
auto-generated and unreliable.

**Waits** — use `wait_for_load_state("networkidle")` and `wait_for_url()`
instead of `time.sleep()` to avoid brittle fixed delays.

---

## Problem Statement 2 — Python Scripts

### Objective 1 — System Health Monitor

Monitors CPU, memory, disk, and running process count against configurable
thresholds. Prints an alert to the console and writes to a log file when any
metric is exceeded.

```bash
cd scripts
pip install psutil

# Single check and exit
python system_health_monitor.py --once

# Continuous monitoring every 30 seconds, log to file
python system_health_monitor.py --interval 30 --log health.log
```

| Metric | Alert Threshold |
|---|:---:|
| CPU usage | > 80% |
| Memory usage | > 80% |
| Disk usage (`/`) | > 85% |
| Running processes | > 300 |

Sample output:
```
2024-06-01 10:00:01 [INFO]    ✔  OK    — CPU Usage: 23.4% (threshold: 80.0%)
2024-06-01 10:00:01 [INFO]    ✔  OK    — Memory Usage: 61.2% (threshold: 80.0%)
2024-06-01 10:00:01 [INFO]    ✔  OK    — Disk Usage (/): 54.0% (threshold: 85.0%)
2024-06-01 10:00:01 [WARNING] ⚠  ALERT — Running Processes: 312 (threshold: 300)
2024-06-01 10:00:01 [WARNING] SUMMARY: 1 alert(s) detected!
```

### Objective 4 — Application Health Checker

Checks one or more URLs by HTTP status code and classifies each as UP,
DEGRADED, or DOWN. Optionally verifies a keyword is present in the response
body. Outputs a plain-text summary and a JSON result.

```bash
# Check the default URLs (OrangeHRM demo + two control endpoints)
python app_health_checker.py --once

# Check custom URLs
python app_health_checker.py --urls https://example.com https://myapp.io --once

# Continuous watch mode
python app_health_checker.py --interval 60 --log app_health.log
```

| Status | Meaning |
|---|---|
| `✔ UP` | HTTP 2xx received (and keyword found, if one is configured) |
| `⚠ DEGRADED` | HTTP 3xx/4xx, or keyword missing on an otherwise-200 response |
| `✗ DOWN` | HTTP 5xx, connection refused, timeout, or DNS failure |

Exits with code `1` if any target is DOWN — works as a basic CI health gate.

---

## Bugs and Observations

Things noticed while manually exploring the AUT and writing the automation:

| # | Observation | Severity |
|---|---|---|
| 1 | The Employee Name field uses an autocomplete that only matches employees already in the PIM module. You cannot type a free-form name — the employee record must exist first. This is a required pre-condition for any Add User test. | Medium |
| 2 | The public demo does not enforce password complexity. Simple passwords like `Test@1234` are accepted without error. | Low |
| 3 | The delete confirmation dialog text reads "Are you Sure?" — the capital S looks like a UI typo in OrangeHRM itself. | Info |
| 4 | Username search is case-insensitive. Searching `ADMIN` returns the `Admin` account. Documented as observed behaviour, not a defect. | Info |

---

## Demo Environment Note

All tests run against the **public OrangeHRM demo** at
`opensource-demo.orangehrmlive.com`. This instance is shared with anyone on
the internet, so its data changes constantly and without warning.

A few things this causes in practice:

- The employee used in Add User tests must already exist in the PIM module.
  If another user deletes that record, the autocomplete step will fail.
- Delete and search tests can return unexpected results if someone else
  created or removed records between test steps.
- The demo site is occasionally slow or temporarily down, which causes timeout
  failures unrelated to the test logic itself.

In a real project this would be solved by running against a dedicated test
environment with seeded, controlled data.

---

## License

MIT
