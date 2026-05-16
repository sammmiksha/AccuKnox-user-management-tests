#!/usr/bin/env python3
"""
Application Health Checker
===========================
Checks the uptime and functional health of one or more web applications
by evaluating HTTP status codes and optional keyword validation.

Features:
  • Detects 'up' / 'degraded' / 'down' states
  • Measures response time (ms)
  • Optionally verifies a keyword is present in the response body
  • Outputs a clear summary report to console + optional log file
  • Supports checking multiple URLs in one run (via config or CLI)

Usage:
    python app_health_checker.py
    python app_health_checker.py --urls https://example.com https://google.com
    python app_health_checker.py --config urls.txt --log health.log
    python app_health_checker.py --once
"""
import argparse
import json
import logging
import sys
import time
from datetime import datetime
from typing import Optional
import urllib.request
import urllib.error

# ── Default URLs to monitor ───────────────────────────────────────────────────
DEFAULT_URLS = [
    {
        "url":     "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login",
        "name":    "OrangeHRM Demo",
        "keyword": "OrangeHRM",      # optional body keyword check
        "timeout": 10,
    },
    {
        "url":     "https://httpstat.us/200",
        "name":    "HTTPStat 200 (Control)",
        "keyword": "200",
        "timeout": 10,
    },
    {
        "url":     "https://httpstat.us/503",
        "name":    "HTTPStat 503 (Expected Down)",
        "keyword": None,
        "timeout": 10,
    },
]

BANNER   = "=" * 70
STATUS_SYMBOLS = {"up": "✔ UP", "degraded": "⚠ DEGRADED", "down": "✗ DOWN"}


def setup_logging(log_file: Optional[str]) -> logging.Logger:
    logger = logging.getLogger("AppHealthChecker")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


def check_app(entry: dict) -> dict:
    """
    Perform a single HTTP health check.

    Returns a result dict with:
        name, url, status, http_code, response_time_ms, keyword_found, error
    """
    url     = entry["url"]
    name    = entry.get("name", url)
    keyword = entry.get("keyword")
    timeout = entry.get("timeout", 10)

    result = {
        "name":             name,
        "url":              url,
        "status":           "down",
        "http_code":        None,
        "response_time_ms": None,
        "keyword_found":    None,
        "error":            None,
    }

    start = time.monotonic()
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AppHealthChecker/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed_ms = round((time.monotonic() - start) * 1000, 1)
            code       = resp.status
            body       = resp.read(4096).decode("utf-8", errors="ignore")

            result["http_code"]        = code
            result["response_time_ms"] = elapsed_ms

            # Determine status
            if 200 <= code < 300:
                result["status"] = "up"
            elif 300 <= code < 500:
                result["status"] = "degraded"
            else:
                result["status"] = "down"

            # Keyword check (optional)
            if keyword:
                result["keyword_found"] = keyword in body
                # Downgrade to degraded if keyword missing on an otherwise-up page
                if result["status"] == "up" and not result["keyword_found"]:
                    result["status"] = "degraded"

    except urllib.error.HTTPError as e:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        result["http_code"]        = e.code
        result["response_time_ms"] = elapsed_ms
        result["status"]           = "down" if e.code >= 500 else "degraded"
        result["error"]            = str(e)

    except urllib.error.URLError as e:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        result["response_time_ms"] = elapsed_ms
        result["status"]           = "down"
        result["error"]            = str(e.reason)

    except Exception as e:
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        result["response_time_ms"] = elapsed_ms
        result["status"]           = "down"
        result["error"]            = str(e)

    return result


def print_report(results: list[dict], logger: logging.Logger):
    """Print a formatted summary report."""
    logger.info(BANNER)
    logger.info("Application Health Report — %s",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info(BANNER)

    for r in results:
        sym  = STATUS_SYMBOLS.get(r["status"], r["status"].upper())
        code = r["http_code"] or "N/A"
        ms   = f"{r['response_time_ms']} ms" if r["response_time_ms"] else "N/A"
        kw   = ""
        if r["keyword_found"] is not None:
            kw = " | keyword: ✔" if r["keyword_found"] else " | keyword: ✗ MISSING"

        log_fn = logger.info if r["status"] == "up" else logger.warning
        log_fn("%-12s  %-10s  HTTP %-4s  %-12s%s",
               f"[{sym}]", r["name"][:20], code, ms, kw)

        if r["error"]:
            logger.warning("            Error: %s", r["error"])

    logger.info(BANNER)

    up_count       = sum(1 for r in results if r["status"] == "up")
    degraded_count = sum(1 for r in results if r["status"] == "degraded")
    down_count     = sum(1 for r in results if r["status"] == "down")

    logger.info("TOTAL: %d checked  |  ✔ Up: %d  |  ⚠ Degraded: %d  |  ✗ Down: %d",
                len(results), up_count, degraded_count, down_count)
    logger.info(BANNER)

    # Machine-readable JSON summary (useful for CI pipelines)
    print("\nJSON Summary:")
    print(json.dumps(results, indent=2))


def run_checks(targets: list[dict], logger: logging.Logger) -> list[dict]:
    results = []
    for entry in targets:
        logger.info("Checking: %s (%s)", entry.get("name", entry["url"]), entry["url"])
        r = check_app(entry)
        results.append(r)
    return results


def main():
    parser = argparse.ArgumentParser(description="Application Health Checker")
    parser.add_argument("--urls", nargs="+",
                        help="One or more URLs to check (overrides defaults)")
    parser.add_argument("--config", type=str,
                        help="Path to a text file with one URL per line")
    parser.add_argument("--log",    type=str, default="app_health.log",
                        help="Log file path (default: app_health.log)")
    parser.add_argument("--interval", type=int, default=60,
                        help="Seconds between checks in watch mode (default: 60)")
    parser.add_argument("--once", action="store_true",
                        help="Run a single check and exit")
    args = parser.parse_args()

    logger = setup_logging(args.log)

    # Build target list
    if args.urls:
        targets = [{"url": u, "name": u, "keyword": None, "timeout": 10}
                   for u in args.urls]
    elif args.config:
        with open(args.config) as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        targets = [{"url": u, "name": u, "keyword": None, "timeout": 10}
                   for u in lines]
    else:
        targets = DEFAULT_URLS

    logger.info("Monitoring %d application(s). Log: %s", len(targets), args.log)

    if args.once:
        results = run_checks(targets, logger)
        print_report(results, logger)
        # Exit with non-zero code if any app is down
        if any(r["status"] == "down" for r in results):
            sys.exit(1)
        return

    # Watch mode
    logger.info("Watch mode — checking every %d seconds. Ctrl+C to stop.", args.interval)
    try:
        while True:
            results = run_checks(targets, logger)
            print_report(results, logger)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Health Checker stopped.")


if __name__ == "__main__":
    main()
