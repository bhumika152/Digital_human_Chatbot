PROPERTY_ACTION_CONTRACT = {
    "search": {
        "required": ["city", "purpose", "budget"],
        "ask_message": "To search properties, I need",
    },
    "add": {
        "required": [
            "title",
            "city",
            "locality",
            "purpose",
            "price",
            "is_legal",
            "owner_name",
            "contact_phone",
        ],
        "ask_message": "Before saving the property, please provide",
    },
    "update": {
        "required": ["property_id"],
        "ask_message": "To update a property, I need",
    },
    "delete": {
        "required": ["property_id"],
        "ask_message": "To delete a property, I need",
    },
}

def get_missing_fields(contract, action: str, payload: dict):
    if action not in contract:
        return []

    required_fields = contract[action]["required"]
    missing = []

    for field in required_fields:
        if payload.get(field) in (None, "", []):
            missing.append(field)

    return missing
