# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from typing import Optional
# from database import SessionLocal
# from models import Property
# from schemas import PropertyCreateRequest
# property_router = APIRouter(prefix="/properties", tags=["Properties"])


# # ✅ DB dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @property_router.get("/search")
# def search_properties(
#     city: str,
#     purpose: str,
#     budget: int,
#     db: Session = Depends(get_db),
# ):
#     results = (
#         db.query(Property)
#         .filter(
#             Property.city.ilike(f"%{city}%"),
#             Property.purpose == purpose,
#             Property.price <= budget
#         )
#         .all()
#     )

#     if not results:
#         return {"message": "No property found", "results": []}

#     return {"message": "Property found", "count": len(results), "results": results}


# # for create new property

# @property_router.post("/rent")
# def add_rent_property(
#     payload: PropertyCreateRequest,
#     db: Session = Depends(get_db),
# ):
#     new_property = Property(
#         title=payload.title,
#         city=payload.city,
#         locality=payload.locality,
#         purpose="rent",   # ✅ fixed
#         price=payload.price,
#         bhk=payload.bhk,
#         area_sqft=payload.area_sqft,
#         is_legal=payload.is_legal,
#         owner_name=payload.owner_name,
#         contact_phone=payload.contact_phone,
#     )

#     db.add(new_property)
#     db.commit()
#     db.refresh(new_property)

#     return {"message": "Rent property added successfully", "property": new_property}



from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Property
from schemas import PropertyCreateRequest

property_router = APIRouter(prefix="/properties", tags=["Properties"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ SEARCH
@property_router.get("/search")
def search_properties(
    city: str,
    purpose: str,
    budget: int,
    db: Session = Depends(get_db),
):
    results = (
        db.query(Property)
        .filter(
            Property.city.ilike(f"%{city}%"),
            Property.purpose == purpose,
            Property.price <= budget,
        )
        .all()
    )

    if not results:
        return {"message": "No property found", "results": []}

    return {"message": "Property found", "count": len(results), "results": results}


# ✅ ADD RENT PROPERTY
@property_router.post("/rent")
def add_rent_property(
    payload: PropertyCreateRequest,
    db: Session = Depends(get_db),
):
    new_property = Property(
        title=payload.title,
        city=payload.city,
        locality=payload.locality,
        purpose="rent",
        price=payload.price,
        bhk=payload.bhk,
        area_sqft=payload.area_sqft,
        is_legal=payload.is_legal,
        owner_name=payload.owner_name,
        contact_phone=payload.contact_phone,
    )

    db.add(new_property)
    db.commit()
    db.refresh(new_property)


    return {
        "message": "Rent property added successfully",
        "property_id": new_property.property_id,
    }
