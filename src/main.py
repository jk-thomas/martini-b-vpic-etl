"""
Run with: python -m src.main
"""
import logging
import os

from . import config, db
from .normalize import normalize_rows
from .quality_report import run_full_report
from .vpic_client import fetch_models_for_make_year

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("vpic_etl.main")


def run():
    log.info(
        "Starting pull: makes=%s years=%d-%d db=%s",
        config.MAKES, config.YEAR_START, config.YEAR_END, config.DB_PATH,
    )

    folder = os.path.dirname(config.DB_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    requests_made = 0
    requests_failed = 0
    rows_fetched = 0
    rows_after_dedupe = 0
    total_inserted = 0
    total_updated = 0
    total_unchanged = 0

    conn = db.open_db(config.DB_PATH)

    for make in config.MAKES:
        for year in range(config.YEAR_START, config.YEAR_END + 1):
            requests_made += 1
            raw_rows = fetch_models_for_make_year(make, year)

            if raw_rows is None:
                # The request failed.
                # Logged in vpic_client. Skip and continue.
                requests_failed += 1
                continue

            if len(raw_rows) == 0:
                log.info("%s %d: 0 results", make, year)
                continue

            rows_fetched += len(raw_rows)
            clean_rows = normalize_rows(raw_rows)
            rows_after_dedupe += len(clean_rows)

            stats = db.upsert_rows(conn, clean_rows)
            total_inserted += stats["inserted"]
            total_updated += stats["updated"]
            total_unchanged += stats["unchanged"]

            log.info(
                "%s %d: fetched=%d inserted=%d updated=%d unchanged=%d",
                make, year, len(raw_rows), stats["inserted"], stats["updated"], stats["unchanged"],
            )

    log.info("=== Run summary ===")
    log.info("Requests made:     %d", requests_made)
    log.info("Requests failed:   %d", requests_failed)
    log.info("Rows fetched:      %d", rows_fetched)
    log.info("Rows after dedupe: %d", rows_after_dedupe)
    log.info("Inserted:          %d", total_inserted)
    log.info("Updated:           %d", total_updated)
    log.info("Unchanged:         %d", total_unchanged)

    run_full_report(conn)

    conn.close()

    if requests_failed > 0:
        log.warning(
            "%d request(s) failed. Safe to rerun.",
            requests_failed,
        )


if __name__ == "__main__":
    run()
