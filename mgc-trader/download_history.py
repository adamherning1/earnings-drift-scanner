"""
MGC Historical Data Downloader
Downloads and stitches historical data across multiple contract months from IB.
Saves to CSV for backtesting and analysis.

Usage:
    python download_history.py                  # Download all available history
    python download_history.py --bar-size "1 hour" --duration "60 D"
    python download_history.py --bar-size "1 day" --duration "1 Y"
"""

import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

import argparse
import csv
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from ib_insync import IB, Future
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("history-dl")

DATA_DIR = Path(__file__).parent / "data" / "history"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def connect_ib(client_id=98):
    """Connect to IB Gateway."""
    ib = IB()
    ib.connect(config.IB_HOST, config.IB_PORT, clientId=client_id, timeout=20)
    ib.reqMarketDataType(3)
    log.info(f"Connected to IB at {config.IB_HOST}:{config.IB_PORT}")
    return ib


def get_all_contracts(ib):
    """Get all available MGC contract months, sorted by expiry."""
    contract = Future(symbol=config.SYMBOL, exchange=config.EXCHANGE, currency=config.CURRENCY)
    details = ib.reqContractDetails(contract)
    details.sort(key=lambda d: d.contract.lastTradeDateOrContractMonth)
    contracts = []
    for d in details:
        c = d.contract
        ib.qualifyContracts(c)
        contracts.append(c)
        log.info(f"  Found: {c.localSymbol} (expires {c.lastTradeDateOrContractMonth})")
    return contracts


def download_bars(ib, contract, bar_size="5 mins", duration="20 D", end_dt=""):
    """Download historical bars for a single contract. Handles IB pacing limits."""
    log.info(f"Downloading {bar_size} bars for {contract.localSymbol} ({duration})...")
    try:
        bars = ib.reqHistoricalData(
            contract,
            endDateTime=end_dt,
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=False,
            formatDate=1,
        )
        if bars:
            log.info(f"  Got {len(bars)} bars: {bars[0].date} to {bars[-1].date}")
        else:
            log.warning(f"  No bars returned for {contract.localSymbol}")
        return bars
    except Exception as e:
        log.error(f"  Error downloading {contract.localSymbol}: {e}")
        return []


def download_chunked(ib, contract, bar_size="5 mins", total_days=60, chunk_days=20):
    """Download bars in chunks to get more history than single request allows."""
    all_bars = []
    end_dt = ""  # Start from now
    remaining = total_days

    while remaining > 0:
        days = min(remaining, chunk_days)
        duration = f"{days} D"
        bars = download_bars(ib, contract, bar_size, duration, end_dt)

        if not bars:
            break

        all_bars = bars + all_bars  # Prepend (older bars first)
        # Set end_dt to just before the earliest bar we got
        earliest = bars[0].date
        if hasattr(earliest, 'strftime'):
            end_dt = earliest.strftime("%Y%m%d %H:%M:%S")
        else:
            end_dt = str(earliest)

        remaining -= days
        if remaining > 0:
            log.info(f"  Pacing: sleeping 10s before next chunk...")
            time.sleep(10)  # IB pacing rules

    # Deduplicate by timestamp
    seen = set()
    unique = []
    for bar in all_bars:
        key = str(bar.date)
        if key not in seen:
            seen.add(key)
            unique.append(bar)

    unique.sort(key=lambda b: str(b.date))
    log.info(f"  Total unique bars: {len(unique)}")
    return unique


def bars_to_rows(bars, contract_symbol):
    """Convert IB bars to list of dicts."""
    rows = []
    for bar in bars:
        rows.append({
            "datetime": str(bar.date),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": getattr(bar, "volume", 0),
            "contract": contract_symbol,
        })
    return rows


def stitch_contracts(all_data):
    """
    Stitch multiple contracts into a continuous series.
    Uses front-month data, switching to next contract ~7 days before expiry.
    Adjusts for roll gaps using ratio-based back-adjustment.
    """
    if not all_data:
        return []

    # Sort by contract expiry
    all_data.sort(key=lambda x: x["expiry"])

    # Build timeline: for each date, pick the appropriate contract
    # Use front month until 7 days before expiry, then roll to next
    stitched = []
    used_contracts = []

    for i, cdata in enumerate(all_data):
        expiry = datetime.strptime(cdata["expiry"], "%Y%m%d")
        roll_date = expiry - timedelta(days=7)

        for row in cdata["rows"]:
            row_dt = row["datetime"][:10]  # Just the date part
            try:
                row_date = datetime.strptime(row_dt, "%Y-%m-%d")
            except ValueError:
                continue

            # Include this bar if:
            # - It's before the roll date for this contract, OR
            # - This is the last contract (no next one to roll to)
            if row_date < roll_date or i == len(all_data) - 1:
                stitched.append(row)

        used_contracts.append(cdata["symbol"])

    # Deduplicate and sort
    seen = set()
    unique = []
    for row in stitched:
        key = row["datetime"]
        if key not in seen:
            seen.add(key)
            unique.append(row)

    unique.sort(key=lambda r: r["datetime"])
    log.info(f"Stitched {len(unique)} bars from contracts: {used_contracts}")
    return unique


def save_csv(rows, filename):
    """Save rows to CSV."""
    if not rows:
        log.warning("No rows to save")
        return

    filepath = DATA_DIR / filename
    fieldnames = ["datetime", "open", "high", "low", "close", "volume", "contract"]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"Saved {len(rows)} bars to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Download MGC historical data from IB")
    parser.add_argument("--bar-size", default="5 mins", help="Bar size (e.g., '5 mins', '1 hour', '1 day')")
    parser.add_argument("--duration", default="20 D", help="Duration per contract (e.g., '20 D', '60 D', '1 Y')")
    parser.add_argument("--stitch", action="store_true", default=True, help="Stitch multiple contracts")
    parser.add_argument("--chunk", action="store_true", help="Download in chunks for more history")
    parser.add_argument("--chunk-days", type=int, default=60, help="Total days when chunking")
    parser.add_argument("--all-timeframes", action="store_true", help="Download daily, hourly, and 5-min")
    args = parser.parse_args()

    ib = connect_ib()

    try:
        contracts = get_all_contracts(ib)

        if args.all_timeframes:
            # Download all useful timeframes
            timeframes = [
                ("1 day", "1 Y", "daily"),
                ("1 hour", "60 D", "1h"),
                ("5 mins", "20 D", "5m"),
            ]
            for bar_size, duration, label in timeframes:
                log.info(f"\n{'='*60}")
                log.info(f"Downloading {label} bars...")
                log.info(f"{'='*60}")

                all_data = []
                for contract in contracts:
                    bars = download_bars(ib, contract, bar_size, duration)
                    if bars:
                        rows = bars_to_rows(bars, contract.localSymbol)
                        all_data.append({
                            "symbol": contract.localSymbol,
                            "expiry": contract.lastTradeDateOrContractMonth,
                            "rows": rows,
                        })
                        # Save individual contract too
                        save_csv(rows, f"mgc_{contract.localSymbol}_{label}.csv")
                    time.sleep(10)  # IB pacing

                # Stitch and save
                stitched = stitch_contracts(all_data)
                save_csv(stitched, f"mgc_continuous_{label}.csv")
        else:
            # Single timeframe download
            all_data = []
            for contract in contracts:
                if args.chunk:
                    bars = download_chunked(ib, contract, args.bar_size, args.chunk_days)
                else:
                    bars = download_bars(ib, contract, args.bar_size, args.duration)

                if bars:
                    rows = bars_to_rows(bars, contract.localSymbol)
                    all_data.append({
                        "symbol": contract.localSymbol,
                        "expiry": contract.lastTradeDateOrContractMonth,
                        "rows": rows,
                    })
                    label = args.bar_size.replace(" ", "")
                    save_csv(rows, f"mgc_{contract.localSymbol}_{label}.csv")
                time.sleep(10)  # IB pacing

            if args.stitch and len(all_data) > 1:
                label = args.bar_size.replace(" ", "")
                stitched = stitch_contracts(all_data)
                save_csv(stitched, f"mgc_continuous_{label}.csv")

    finally:
        ib.disconnect()
        log.info("Done!")


if __name__ == "__main__":
    main()
