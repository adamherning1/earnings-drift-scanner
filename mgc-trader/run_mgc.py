#!/usr/bin/env python3
"""
MGC Day Trader — Runner Script
================================
Start:  python run_mgc.py
Detach: python run_mgc.py --detach

Connects to IB Gateway on port 4002 and trades MGC futures.
Logs to mgc-trader/logs/
"""

import asyncio
import signal
import sys
import os
import subprocess
from pathlib import Path

# Fix for Python 3.14+ asyncio (eventkit needs a loop at import time)
asyncio.set_event_loop(asyncio.new_event_loop())

SCRIPT_DIR = Path(__file__).parent
LOG_DIR = SCRIPT_DIR / "logs"


def main():
    if "--detach" in sys.argv:
        _start_detached()
        return

    # Foreground mode
    LOG_DIR.mkdir(exist_ok=True)
    pid_file = LOG_DIR / "mgc.pid"
    pid_file.write_text(str(os.getpid()))

    from trader import MGCTrader

    trader = MGCTrader()

    def shutdown(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        trader.running = False
        try:
            pid_file.unlink()
        except Exception:
            pass

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        trader.start()
    finally:
        try:
            pid_file.unlink()
        except Exception:
            pass


def _start_detached():
    LOG_DIR.mkdir(exist_ok=True)
    pid_file = LOG_DIR / "mgc.pid"
    log_file = LOG_DIR / "mgc_runner.log"

    # Check if already running
    if pid_file.exists():
        old_pid = pid_file.read_text().strip()
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {old_pid}", "/NH"],
                capture_output=True, text=True,
            )
            if f" {old_pid} " in result.stdout:
                print(f"MGC trader already running (PID {old_pid}). Kill it first.")
                sys.exit(1)
        except Exception:
            pass

    cmd = [sys.executable, str(Path(__file__).resolve())]
    if sys.platform == "win32":
        DETACHED = 0x00000008
        NEW_GROUP = 0x00000200
        proc = subprocess.Popen(
            cmd,
            creationflags=DETACHED | NEW_GROUP,
            stdout=open(log_file, "a"),
            stderr=subprocess.STDOUT,
            cwd=str(SCRIPT_DIR),
        )
    else:
        proc = subprocess.Popen(
            cmd,
            stdout=open(log_file, "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
            cwd=str(SCRIPT_DIR),
        )

    pid_file.write_text(str(proc.pid))
    print(f"MGC Day Trader started (PID {proc.pid})")
    print(f"Log: {log_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
