"""
Fetches passenger-car models for one make/year from vPIC.
"""
import logging

import requests

from . import config

log = logging.getLogger("vpic_etl.client")


def fetch_models_for_make_year(make, year):
    """
    Returns a list of model dicts for one make/year.
    Returns an empty list if there are zero results.
    Returns None if the request itself failed
    so main.py can log it and move on instead of crashing.
    """
    url = config.BASE_URL + "/GetModelsForMakeYear/make/" + make
    url += "/modelyear/" + str(year) + "/vehicletype/" + config.VEHICLE_TYPE

    try:
        response = requests.get(url, params={"format": "json"}, timeout=config.REQUEST_TIMEOUT_SECONDS)
    except requests.RequestException as error:
        log.error("Request failed for %s %d: %s", make, year, error)
        return None

    if response.status_code != 200:
        log.error("Got status code %s for %s %d", response.status_code, make, year)
        return None

    data = response.json()
    raw_results = data.get("Results")
    if raw_results is None:
        raw_results = []

    # Keep only rows where the make name is an exact match
    good_rows = []
    dropped_count = 0
    for row in raw_results:
        row_make_name = str(row.get("Make_Name", "")).strip().lower()
        if row_make_name == make.lower():
            good_rows.append(row)
        else:
            dropped_count += 1

    if dropped_count > 0:
        log.info("%s %d: dropped %d row(s) that weren't an exact make match", make, year, dropped_count)

    # Build simple list of model dicts. Used general "make"
    # spelling instead of vPIC's Make_Name because
    # vPIC returns it inconsistently
    models = []
    for row in good_rows:
        model = {
            "make_id": row["Make_ID"],
            "make_name": make,
            "model_id": row["Model_ID"],
            "model_name": row["Model_Name"],
            "year": year,
        }
        models.append(model)

    return models
