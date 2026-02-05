from property_fields import PROPERTY_REQUIRED_FIELDS


def find_missing_fields(payload: dict) -> list:
    missing = []
    for field in PROPERTY_REQUIRED_FIELDS:
        if payload.get(field) in (None, "", []):
            missing.append(field)
    return missing
