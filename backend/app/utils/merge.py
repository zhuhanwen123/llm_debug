def merge_dict(defaults: dict | None, overrides: dict | None) -> dict:
    merged = dict(defaults or {})
    for key, value in (overrides or {}).items():
        merged[key] = value
    return merged
