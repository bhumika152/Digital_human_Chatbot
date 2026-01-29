from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from database import SessionLocal
from models import Property
from schemas import PropertyCreateRequest
from auth import get_current_user

property_router = APIRouter(prefix="/properties", tags=["Properties"])
 

 
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
    user_id: int = Depends(get_current_user),
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
        owner_user_id=user_id  

    )
 
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
 
 
    return {
        "message": "Rent property added successfully",
        "property_id": new_property.property_id,
    }