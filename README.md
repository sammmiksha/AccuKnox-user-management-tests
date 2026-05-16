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
├── playwright-automation/
│   ├── pages/
│   │   ├── login_page.py             # Page Object: Login screen
│   │   └── user_management_page.py  # Page Object: Admin > User Management
│   ├── tests/
│   │   └── test_user_management.py  # All automated test cases
│   ├── conftest.py                  # Shared fixtures and test data
│   ├── pytest.ini                   # Pytest config
│   └── requirements.txt
│
├── scripts/
│   ├── system_health_monitor.py     # Objective 1: System Health Monitor
│   └── app_health_checker.py        # Objective 4: Application Health Checker
│
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

The following core user management workflows are automated:

- Login as Admin and navigate to the Admin module
- Add a new user with valid data
- Validate required field errors when the form is submitted empty
- Validate duplicate username error
- Search for the newly created user by username
- Search with a username that does not exist (no results)
- Edit user details (role, status, username)
- Validate that updated details are saved correctly
- Delete a user and confirm removal
- Cancel a delete and confirm the user still exists

> **Note:** All 10 scenarios are written as individual test blocks. Some
> delete and search tests can be flaky on the shared public demo because
> other users may create or remove records between test steps — see the
> environment note at the bottom.

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/AccuKnox-user-management-tests.git
cd AccuKnox-user-management-tests/playwright-automation

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

# Run a single test by name
pytest tests/test_user_management.py::test_tc_um_01_navigate_to_admin_module

# Generate an HTML report
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

- The employee used in Add User tests (`Peter Mac Anderson`) must already
  exist in the PIM module. If another user deletes that record, those tests
  will fail at the autocomplete step.
- Delete and search tests can return unexpected results if someone else
  created or removed records between test steps.
- The demo site is occasionally slow or temporarily down, which causes timeout
  failures that are unrelated to the test logic itself.

In a real project this would be solved by running against a dedicated test
environment with seeded, controlled data. For this assessment the tests handle
the most common cases and include basic cleanup steps where practical.

---

## License

MIT
