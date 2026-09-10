"""
Cleans up whitespace in names and removes duplicate rows.
"""
def clean_text(text):
    return " ".join(text.split())


def normalize_rows(rows):
    cleaned_rows = []
    for row in rows:
        cleaned_row = {
            "make_id": row["make_id"],
            "make_name": clean_text(row["make_name"]),
            "model_id": row["model_id"],
            "model_name": clean_text(row["model_name"]),
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
