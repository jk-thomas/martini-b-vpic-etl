"""
Cleans up whitespace in names and removes duplicate rows.
"""
def clean_text(text):
    return " ".join(text.split())


def normalize_model_name(make_name, model_name):
    make_prefix = make_name.casefold()
    if model_name.casefold().startswith(make_prefix):
        suffix = model_name[len(make_name):]
        if len(suffix) == 1 and suffix.isdigit():
            return suffix
    return model_name


def normalize_rows(rows):
    cleaned_rows = []
    for row in rows:
        make_name = clean_text(row["make_name"])
        model_name = clean_text(row["model_name"])
        cleaned_row = {
            "make_id": row["make_id"],
            "make_name": make_name,
            "model_id": row["model_id"],
            "model_name": normalize_model_name(make_name, model_name),
            "year": row["year"],
        }
        cleaned_rows.append(cleaned_row)

    # Remove duplicates
    seen_keys = set()
    unique_rows = []
    for row in cleaned_rows:
        key = (row["make_id"], row["model_id"], row["year"])
        if key not in seen_keys:
            seen_keys.add(key)
            unique_rows.append(row)

    return unique_rows
