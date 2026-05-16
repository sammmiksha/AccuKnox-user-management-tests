#!/usr/bin/env python3
"""
System Health Monitor
=====================
Monitors CPU, Memory, Disk, and Running Processes.
Logs alerts to console AND to a log file when thresholds are breached.

Usage:
    python system_health_monitor.py
    python system_health_monitor.py --interval 30 --log health.log
    python system_health_monitor.py --once          # Run a single check and exit
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    print("[ERROR] psutil is required. Install it with:  pip install psutil")
    sys.exit(1)

# ── Thresholds (%) ────────────────────────────────────────────────────────────
THRESHOLDS = {
    "cpu": 80.0,  # CPU usage %
    "memory": 80.0,  # RAM usage %
    "disk": 85.0,  # Disk usage %
    "procs": 300,  # Running process count
}

BANNER = "=" * 65


def setup_logging(log_file: str | None) -> logging.Logger:
    """Configure logging to console and optionally to a file."""
    logger = logging.getLogger("HealthMonitor")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler — always on
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler — optional
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def check_cpu(logger: logging.Logger) -> dict:
    """Check CPU usage. Returns metric dict."""
    # interval=1 → non-blocking first call returns 0.0; use interval=1 for accuracy
    usage = psutil.cpu_percent(interval=1)
    count = psutil.cpu_count()
    freq = psutil.cpu_freq()

    result = {
        "metric": "CPU Usage",
        "value": usage,
        "unit": "%",
        "threshold": THRESHOLDS["cpu"],
        "alert": usage > THRESHOLDS["cpu"],
        "details": (
            f"Cores: {count} | " f"Freq: {freq.current:.0f} MHz"
            if freq
            else "Freq: N/A"
        ),
    }
    _log_metric(logger, result)
    return result


def check_memory(logger: logging.Logger) -> dict:
    """Check RAM usage."""
    mem = psutil.virtual_memory()

    result = {
        "metric": "Memory Usage",
        "value": mem.percent,
        "unit": "%",
        "threshold": THRESHOLDS["memory"],
        "alert": mem.percent > THRESHOLDS["memory"],
        "details": (
            f"Total: {_bytes(mem.total)} | "
            f"Used: {_bytes(mem.used)} | "
            f"Available: {_bytes(mem.available)}"
        ),
    }
    _log_metric(logger, result)
    return result


def check_disk(logger: logging.Logger, path: str = "/") -> dict:
    """Check disk usage for the given mount path."""
    disk = psutil.disk_usage(path)

    result = {
        "metric": f"Disk Usage ({path})",
        "value": disk.percent,
        "unit": "%",
        "threshold": THRESHOLDS["disk"],
        "alert": disk.percent > THRESHOLDS["disk"],
        "details": (
            f"Total: {_bytes(disk.total)} | "
            f"Used: {_bytes(disk.used)} | "
            f"Free: {_bytes(disk.free)}"
        ),
    }
    _log_metric(logger, result)
    return result


def check_processes(logger: logging.Logger) -> dict:
    """Check total running processes."""
    procs = list(psutil.process_iter(["pid", "name", "status"]))
    count = len(procs)

    # Top 5 CPU-consuming processes
    top5 = []
    for p in procs:
        try:
            top5.append((p.info["name"], p.cpu_percent(interval=None)))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    top5 = sorted(top5, key=lambda x: x[1], reverse=True)[:5]
    top5_str = ", ".join(f"{n}({c:.1f}%)" for n, c in top5) or "N/A"

    result = {
        "metric": "Running Processes",
        "value": count,
        "unit": "procs",
        "threshold": THRESHOLDS["procs"],
        "alert": count > THRESHOLDS["procs"],
        "details": f"Top CPU consumers: {top5_str}",
    }
    _log_metric(logger, result)
    return result


def _bytes(n: int) -> str:
    """Human-readable byte size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _log_metric(logger: logging.Logger, r: dict):
    """Log a single metric — WARNING if alert, INFO otherwise."""
    line = (
        f"{r['metric']}: {r['value']:.1f}{r['unit']} "
        f"(threshold: {r['threshold']}{r['unit']}) | {r['details']}"
    )
    if r["alert"]:
        logger.warning("⚠  ALERT — %s", line)
    else:
        logger.info("✔  OK    — %s", line)


def run_check(logger: logging.Logger) -> list[dict]:
    """Run all checks and return list of results."""
    logger.info(BANNER)
    logger.info(
        "System Health Check — %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    logger.info(BANNER)

    results = [
        check_cpu(logger),
        check_memory(logger),
        check_disk(logger, path="/"),
        check_processes(logger),
    ]

    alerts = [r for r in results if r["alert"]]
    if alerts:
        logger.warning("SUMMARY: %d alert(s) detected!", len(alerts))
        for a in alerts:
            logger.warning(
                "  → %s at %.1f%s exceeds threshold %.1f%s",
                a["metric"],
                a["value"],
                a["unit"],
                a["threshold"],
                a["unit"],
            )
    else:
        logger.info("SUMMARY: All systems within normal thresholds. ✔")

    logger.info(BANNER)
    return results


def main():
    parser = argparse.ArgumentParser(description="System Health Monitor")
    parser.add_argument(
        "--interval", type=int, default=60, help="Seconds between checks (default: 60)"
    )
    parser.add_argument(
        "--log",
        type=str,
        default="system_health.log",
        help="Log file path (default: system_health.log)",
    )
    parser.add_argument(
        "--once", action="store_true", help="Run a single check and exit"
    )
    args = parser.parse_args()

    logger = setup_logging(args.log)
    logger.info("Health Monitor started. Log file: %s", args.log)

    if args.once:
        run_check(logger)
        return

    logger.info("Monitoring every %d seconds. Press Ctrl+C to stop.", args.interval)
    try:
        while True:
            run_check(logger)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logger.info("Health Monitor stopped by user.")


if __name__ == "__main__":
    main()
