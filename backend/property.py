import logging
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from database import get_db
from models import Property
from schemas import (
    PropertyCreateRequest,
    PropertyUpdateRequest,
    PropertySearchRequest,
)
from auth import get_current_user

logger = logging.getLogger("property")

property_router = APIRouter(
    prefix="/properties",
    tags=["Properties"]
)

# --------------------------------------------------
# 🔍 SEARCH PROPERTY (STRICT)
# --------------------------------------------------
@property_router.get("/search")
def search_properties(
    filters: PropertySearchRequest = Depends(),
    db: Session = Depends(get_db),
):
    try:
        results = (
            db.query(Property)
            .filter(
                Property.city.ilike(f"%{filters.city}%"),
                Property.purpose == filters.purpose,
                Property.price <= filters.budget,
            )
            .all()
        )

        return {
            "success": True,
            "count": len(results),
            "results": results,
        }

    except Exception as e:
        logger.exception("❌ Property search failed")
        return {
            "success": False,
            "message": "Search failed",
            "errors": [str(e)],
        }

@property_router.post("/", status_code=status.HTTP_201_CREATED)
def save_property(
    payload: PropertyCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = payload.dict(exclude_unset=True)

    # ❌ Last line of defense (never trust callers)
    required = [
        "title",
        "city",
        "locality",
        "purpose",
        "price",
        "is_legal",
        "owner_name",
        "contact_phone",
    ]

    missing = [f for f in required if f not in data]

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing)}",
        )

    try:
        new_property = Property(
            **data,
            owner_user_id=user_id,
        )

        db.add(new_property)
        db.commit()
        db.refresh(new_property)

        return {
            "success": True,
            "property_id": new_property.property_id,
        }

    except Exception:
        logger.exception("❌ Failed to save property")
        raise HTTPException(
            status_code=500,
            detail="Failed to save property",
        )


# --------------------------------------------------
# ✏️ UPDATE PROPERTY
# --------------------------------------------------
@property_router.put("/{property_id}")
def update_property(
    property_id: int,
    payload: PropertyUpdateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    property_obj = (
        db.query(Property)
        .filter(
            Property.property_id == property_id,
            Property.owner_user_id == user_id,
        )
        .first()
    )

    if not property_obj:
        raise HTTPException(
            status_code=404,
            detail="Property not found or unauthorized",
        )

    update_data = payload.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(property_obj, key, value)

    db.commit()
    db.refresh(property_obj)

    return {
        "success": True,
        "property": property_obj,
    }


# --------------------------------------------------
# ❌ DELETE PROPERTY
# --------------------------------------------------
@property_router.delete("/{property_id}")
def delete_property(
    property_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    property_obj = (
        db.query(Property)
        .filter(
            Property.property_id == property_id,
            Property.owner_user_id == user_id,
        )
        .first()
    )

    if not property_obj:
        raise HTTPException(
            status_code=404,
            detail="Property not found or unauthorized",
        )

    db.delete(property_obj)
    db.commit()

    return {"success": True}
