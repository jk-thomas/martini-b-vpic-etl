# MartiniWorks Passenger Car Catalog ETL

Pulls passenger-car models for 8 makes, 2010–2025, from NHTSA's vPIC API
into a SQLite database, with dedupe, upserts, and a data quality report.

## Running it

```
docker compose up --build
```

Writes `./data/vpic.sqlite` on the host. Safe to run again, no dupes.

## Two required queries

```
sqlite3 data/vpic.sqlite
```

```sql
-- What passenger cars did Mazda sell in 2021?
SELECT model_name FROM vehicle_models
WHERE make_name = 'Mazda' AND model_year = 2021;

-- How many models did each make have per year?
SELECT make_name, model_year, COUNT(*) FROM vehicle_models
GROUP BY make_name, model_year 
ORDER BY make_name, model_year;
```

## Schema

One table, one row per `(make_id, model_id, model_year)`
Keeps vPIC's IDs

```
vehicle_models(make_id, make_name, model_id, model_name, model_year, updated_at)
PRIMARY KEY (make_id, model_id, model_year)
```

## Problems

1. **Make names are partial matches.** Asking for "Ford" can return rows
   for anything vPIC's `LIKE` match happens to catch. Handled in
   `vpic_client.py`: after every request, rows are kept only if their
   `Make_Name` equals the make was asked for.
2. **Vehicle type filtering.** `GetModelsForMakeYear` takes an optional
   `vehicletype` segment; `car` matches vPIC's "Passenger Car" type and
   nothing else in their list, so it's used to filter.

## Bug found

vPIC's own `Make_Name` field is inconsistently cased 
(`BMW` correct, `HONDA`/`NISSAN` in all-caps for the same field). 
`vpic_client.py` uses my own casing instead of trusting vPIC's.

## Style

Everything here is simple functions and dicts, 
priority was getting the logic right and explainable

## Data quality report

Three checks required, run against the loaded table after
each load (`quality_report.py`):

1. Model IDs whose name changed across years.
2. Model names that show up under more than one model_id for the same make.
3. Models with a gap in year coverage.

## Assumptions

- **The make list has an issue**: it's stated once as 8 makes,
  then a second "Makes:" line later adds Lexus for 9. I went with
  the 8-make list as it reads as the real requirement.
- No hard rate limit is documented for vPIC, so I didn't add a delay 
  between request, the run itself takes under a minute with no failures.
- "Passenger cars only" is whatever vPIC's own `vehicletype=car` filter
  returns.

## What's not built (ran out of time)

- **Retries with backoff** on request failure: right now a failed
  request is logged and skipped, not retried. 
- **Config via env vars** (makes/years/vehicle type): currently
  hardcoded in `config.py`. Would make the Lexus addition easy.
- **"What changed" report on a second run**: would need to snapshot database
  before a run and diff after.
- **Extending to MPVs**: the vehicle type filter is a single hardcoded
  string right now, would need to become a list and the schema would need
  a `vehicle_type` column.
