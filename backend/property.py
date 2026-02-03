from fastapi import APIRouter, Depends, HTTPException
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
    limit: int =10,
    db: Session = Depends(get_db),
):
    results = (
        db.query(Property)
        .filter(
            Property.city.ilike(f"%{city}%"),
            Property.purpose == purpose,
            Property.price <= budget,
        )
        .limit(limit)
        .all()
    )
 
    if not results:
        return {"message": "No property found", "results": []}
 
    return {"message": "Property found", "count": len(results), "results": results}
 
# ✅ SAVE PROPERTY (REGION BASED)
@property_router.post("/")
def save_property(
    payload: PropertyCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_property = Property(
        title=payload.title,
        city=payload.city,
        locality=payload.locality,   # 👈 REGION
        purpose=payload.purpose,     # rent / buy
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
        "message": "Property saved successfully",
        "property_id": new_property.property_id
    }


# ✅ FETCH PROPERTIES BY REGION
@property_router.get("/region")
def fetch_properties_by_region(
    city: str,
    locality: str | None = None,
    purpose: str | None = None,
    max_budget: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Property).filter(
        Property.city.ilike(f"%{city}%")
    )

    if locality:
        query = query.filter(Property.locality.ilike(f"%{locality}%"))

    if purpose:
        query = query.filter(Property.purpose == purpose)

    if max_budget:
        query = query.filter(Property.price <= max_budget)

    results = query.all()

    return {
        "count": len(results),
        "results": results
    }


# ✅ UPDATE PROPERTY
@property_router.put("/{property_id}")
def update_property(
    property_id: int,
    payload: PropertyCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    property_obj = db.query(Property).filter(
        Property.property_id == property_id,
        Property.owner_user_id == user_id
    ).first()

    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found or unauthorized")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(property_obj, key, value)

    db.commit()
    db.refresh(property_obj)

    return {
        "message": "Property updated successfully",
        "property": property_obj
    }

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