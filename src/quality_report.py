"""
Run against whatever's already
loaded in the database.
"""
import logging

log = logging.getLogger("vpic_etl.quality")


def find_models_with_name_changes(conn):
    cursor = conn.execute(
        "SELECT make_name, model_id, GROUP_CONCAT(DISTINCT model_name) "
        "FROM vehicle_models "
        "GROUP BY make_id, model_id "
        "HAVING COUNT(DISTINCT model_name) > 1"
    )
    return cursor.fetchall()


def find_names_reused_across_ids(conn):
    cursor = conn.execute(
        "SELECT make_name, model_name, GROUP_CONCAT(DISTINCT model_id) "
        "FROM vehicle_models "
        "GROUP BY make_id, model_name "
        "HAVING COUNT(DISTINCT model_id) > 1"
    )
    return cursor.fetchall()


def find_models_with_year_gaps(conn):
    all_models = conn.execute(
        "SELECT DISTINCT make_id, make_name, model_id, model_name "
        "FROM vehicle_models"
    ).fetchall()

    gapped_models = []
    for make_id, make_name, model_id, model_name in all_models:
        year_rows = conn.execute(
            "SELECT DISTINCT model_year "
            "FROM vehicle_models "
            "WHERE make_id=? AND model_id=?",
            (make_id, model_id),
        ).fetchall()

        years = []
        for (year,) in year_rows:
            years.append(year)
        years.sort()

        if len(years) < 2:
            continue

        missing_years = []
        for year in range(years[0], years[-1] + 1):
            if year not in years:
                missing_years.append(year)

        if missing_years:
            gapped_models.append((make_name, model_name, years, missing_years))

    return gapped_models


def run_full_report(conn):
    log.info("=== Data quality report ===")

    name_changes = find_models_with_name_changes(conn)
    log.info("Model IDs with a name that changed across years: %d", len(name_changes))
    for make_name, model_id, names in name_changes:
        log.info("  %s model_id=%s -> %s", make_name, model_id, names)

    reused_names = find_names_reused_across_ids(conn)
    log.info("Model names reused under more than one model_id for the same make: %d", len(reused_names))
    for make_name, model_name, ids in reused_names:
        log.info("  %s '%s' -> model_ids %s", make_name, model_name, ids)

    year_gaps = find_models_with_year_gaps(conn)
    log.info("Models with a gap in year coverage: %d", len(year_gaps))
    for make_name, model_name, years, missing_years in year_gaps:
        log.info("  %s %s: have %s, missing %s", make_name, model_name, years, missing_years)

    log.info(
        "Gap usually means a model was "
        "discontinued and brought back later."
    )
    log.info("=== End data quality report ===")
