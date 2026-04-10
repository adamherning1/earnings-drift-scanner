"""
MES (Micro E-mini S&P 500) Historical Data Downloader
Downloads 4H bars from IB and stitches into continuous series.
"""
import asyncio; asyncio.set_event_loop(asyncio.new_event_loop())

import csv
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from ib_insync import IB, Future

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("mes-dl")

DATA_DIR = Path(__file__).parent / "data" / "history"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# MES contract months to try (oldest first)
MES_CONTRACTS = [
    ("MESH5", "202503"),   # Mar 2025
    ("MESM5", "202506"),   # Jun 2025
    ("MESU5", "202509"),   # Sep 2025
    ("MESZ5", "202512"),   # Dec 2025
    ("MESH6", "202603"),   # Mar 2026
    ("MESM6", "202606"),   # Jun 2026
    ("MESU6", "202609"),   # Sep 2026
    ("MESZ6", "202612"),   # Dec 2026
    ("MESH7", "202703"),   # Mar 2027
]


def connect_ib():
    ib = IB()
    ib.connect("127.0.0.1", 4002, clientId=97, timeout=20)
    ib.reqMarketDataType(3)
    log.info("Connected to IB Gateway")
    return ib


def download_contract(ib, local_symbol, expiry):
    """Download 4H bars for a single MES contract."""
    contract = Future(symbol="MES", exchange="CME", currency="USD",
                      lastTradeDateOrContractMonth=expiry)
    try:
        qualified = ib.qualifyContracts(contract)
        if not qualified:
            log.warning(f"Could not qualify {local_symbol}")
            return None, []
        contract = qualified[0]
        log.info(f"Downloading {contract.localSymbol} (expiry {expiry})...")
    except Exception as e:
        log.warning(f"Qualify failed for {local_symbol}: {e}")
        return None, []

    try:
        bars = ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr="1 Y",
            barSizeSetting="4 hours",
            whatToShow="TRADES",
            useRTH=False,
            formatDate=1,
        )
        if bars:
            log.info(f"  {contract.localSymbol}: {len(bars)} bars ({bars[0].date} to {bars[-1].date})")
        else:
            log.warning(f"  {contract.localSymbol}: 0 bars (expired?)")
        return contract, bars
    except Exception as e:
        log.error(f"  Error downloading {local_symbol}: {e}")
        return contract, []


def bars_to_rows(bars, symbol):
    rows = []
    for bar in bars:
        rows.append({
            "datetime": str(bar.date),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": getattr(bar, "volume", 0),
            "contract": symbol,
        })
    return rows


def save_csv(rows, filename):
    if not rows:
        return
    filepath = DATA_DIR / filename
    fieldnames = ["datetime", "open", "high", "low", "close", "volume", "contract"]
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    log.info(f"Saved {len(rows)} bars to {filepath}")


def stitch_continuous(all_data):
    """Stitch contracts with ratio-based back-adjustment, rolling 7 days before expiry."""
    if not all_data:
        return []

    # Sort by expiry
    all_data.sort(key=lambda x: x["expiry"])

    # First pass: determine which contract covers which dates
    # Use front month, roll 7 days before expiry
    segments = []
    for i, cdata in enumerate(all_data):
        if not cdata["rows"]:
            continue
        exp_str = cdata["expiry"]
        if len(exp_str) == 6:
            exp_str += "01"
        expiry = datetime.strptime(exp_str, "%Y%m%d")
        roll_date = expiry - timedelta(days=7)

        seg_rows = []
        for row in cdata["rows"]:
            row_dt = row["datetime"][:10]
            try:
                row_date = datetime.strptime(row_dt, "%Y-%m-%d")
            except ValueError:
                continue
            if row_date < roll_date or i == len(all_data) - 1:
                seg_rows.append(row)

        if seg_rows:
            segments.append({
                "symbol": cdata["symbol"],
                "expiry": cdata["expiry"],
                "rows": seg_rows,
            })

    if not segments:
        return []

    # Calculate ratio adjustments between segments
    # Work backwards from most recent (no adjustment) to oldest
    adjustments = [1.0] * len(segments)
    for i in range(len(segments) - 2, -1, -1):
        # Find overlapping date between segment i and i+1
        seg_i_dates = {r["datetime"][:10]: r for r in segments[i]["rows"]}
        seg_next_dates = {r["datetime"][:10]: r for r in segments[i + 1]["rows"]}

        # Find first overlapping date
        overlap_close_i = None
        overlap_close_next = None
        for dt in sorted(seg_next_dates.keys()):
            if dt in seg_i_dates:
                overlap_close_i = float(seg_i_dates[dt]["close"])
                overlap_close_next = float(seg_next_dates[dt]["close"])
                break

        if overlap_close_i and overlap_close_next and overlap_close_i > 0:
            ratio = overlap_close_next / overlap_close_i
            adjustments[i] = adjustments[i + 1] * ratio
        else:
            adjustments[i] = adjustments[i + 1]  # No adjustment if no overlap

    # Apply adjustments and merge
    stitched = []
    for i, seg in enumerate(segments):
        adj = adjustments[i]
        for row in seg["rows"]:
            stitched.append({
                "datetime": row["datetime"],
                "open": round(float(row["open"]) * adj, 2),
                "high": round(float(row["high"]) * adj, 2),
                "low": round(float(row["low"]) * adj, 2),
                "close": round(float(row["close"]) * adj, 2),
                "volume": row["volume"],
                "contract": row["contract"],
            })

    # Deduplicate and sort
    seen = set()
    unique = []
    for row in stitched:
        if row["datetime"] not in seen:
            seen.add(row["datetime"])
            unique.append(row)
    unique.sort(key=lambda r: r["datetime"])

    log.info(f"Stitched {len(unique)} bars, adjustments: {[round(a,4) for a in adjustments]}")
    return unique


def main():
    ib = connect_ib()
    all_data = []

    try:
        for local_sym, expiry in MES_CONTRACTS:
            contract, bars = download_contract(ib, local_sym, expiry)
            if bars:
                actual_sym = contract.localSymbol if contract else local_sym
                rows = bars_to_rows(bars, actual_sym)
                all_data.append({
                    "symbol": actual_sym,
                    "expiry": expiry,
                    "rows": rows,
                })
                save_csv(rows, f"mes_{actual_sym}_4h.csv")

            log.info("  Pacing: sleeping 12s...")
            time.sleep(12)

        # Stitch continuous
        stitched = stitch_continuous(all_data)
        save_csv(stitched, "mes_continuous_4h.csv")
        log.info(f"\nDone! Total stitched bars: {len(stitched)}")

    finally:
        ib.disconnect()


if __name__ == "__main__":
    main()
