# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import get_db
# from database import SessionLocal
# from models import Property
# from schemas import PropertyCreateRequest
# from auth import get_current_user

# property_router = APIRouter(prefix="/properties", tags=["Properties"])
 

 
# # ✅ SEARCH
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
#             Property.price <= budget,
#         )
        
#         .all()
#     )
 
#     if not results:
#         return {"message": "No property found", "results": []}
 
#     return {"message": "Property found", "count": len(results), "results": results}
 
# # ✅ SAVE PROPERTY (REGION BASED)
# @property_router.post("/")
# def save_property(
#     payload: PropertyCreateRequest,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     new_property = Property(
#         title=payload.title,
#         city=payload.city,
#         locality=payload.locality,   # 👈 REGION
#         purpose=payload.purpose,     # rent / buy
#         price=payload.price,
#         bhk=payload.bhk,
#         area_sqft=payload.area_sqft,
#         is_legal=payload.is_legal,
#         owner_name=payload.owner_name,
#         contact_phone=payload.contact_phone,
#         owner_user_id=user_id
#     )

#     db.add(new_property)
#     db.commit()
#     db.refresh(new_property)

#     return {
#         "message": "Property saved successfully",
#         "property_id": new_property.property_id
#     }


# # ✅ FETCH PROPERTIES BY REGION
# @property_router.get("/region")
# def fetch_properties_by_region(
#     city: str,
#     locality: str | None = None,
#     purpose: str | None = None,
#     max_budget: int | None = None,
#     db: Session = Depends(get_db),
# ):
#     query = db.query(Property).filter(
#         Property.city.ilike(f"%{city}%")
#     )

#     if locality:
#         query = query.filter(Property.locality.ilike(f"%{locality}%"))

#     if purpose:
#         query = query.filter(Property.purpose == purpose)

#     if max_budget:
#         query = query.filter(Property.price <= max_budget)

#     results = query.all()

#     return {
#         "count": len(results),
#         "results": results
#     }


# # ✅ UPDATE PROPERTY
# @property_router.put("/{property_id}")
# def update_property(
#     property_id: int,
#     payload: PropertyCreateRequest,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     property_obj = db.query(Property).filter(
#         Property.property_id == property_id,
#         Property.owner_user_id == user_id
#     ).first()

#     if not property_obj:
#         raise HTTPException(status_code=404, detail="Property not found or unauthorized")

#     update_data = payload.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(property_obj, key, value)

#     db.commit()
#     db.refresh(property_obj)

#     return {
#         "message": "Property updated successfully",
#         "property": property_obj
#     }

# # ✅ ADD RENT PROPERTY
# @property_router.post("/rent")
# def add_rent_property(
#     payload: PropertyCreateRequest,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     new_property = Property(
#         title=payload.title,
#         city=payload.city,
#         locality=payload.locality,
#         purpose="rent",
#         price=payload.price,
#         bhk=payload.bhk,
#         area_sqft=payload.area_sqft,
#         is_legal=payload.is_legal,
#         owner_name=payload.owner_name,
#         contact_phone=payload.contact_phone,
#         owner_user_id=user_id  

#     )
 
#     db.add(new_property)
#     db.commit()
#     db.refresh(new_property)
 
 
#     return {
#         "message": "Rent property added successfully",
#         "property_id": new_property.property_id,
#     }
# # Add Buy Property Api
# @property_router.post("/buy")
# def add_buy_property(
#     payload:PropertyCreateRequest,
#     user_id : int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     new_property = Property(
#         title=payload.title,
#         city=payload.city,
#         locality=payload.locality,
#         purpose="buy",  # FIXED AS BUY
#         price=payload.price,
#         bhk=payload.bhk,
#         area_sqft=payload.area_sqft,
#         is_legal=payload.is_legal,
#         owner_name=payload.owner_name,
#         contact_phone=payload.contact_phone,
#         owner_user_id=user_id
#     )
#     db.add(new_property)
#     db.commit()
#     db.refresh(new_property)

#     return {
#         "message": "Buy property added successfully",
#         "property_id": new_property.property_id,
#     }


 
# import logging
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
 
# from database import get_db
# from models import Property
# from schemas import PropertyCreateRequest
# from auth import get_current_user
# import time
 
 
# logger = logging.getLogger("property")
 
# property_router = APIRouter(
#     prefix="/properties",
#     tags=["Properties"]
# )
 
# # --------------------------------------------------
# # 🔍 SEARCH
# # --------------------------------------------------
 
# @property_router.get("/search")
# def search_properties(
#     city: str,
#     purpose: str,
#     budget: int,
#     db: Session = Depends(get_db),
# ):
# start = time.time()
#     results = (
#         db.query(Property)
#         .filter(
#             Property.city.ilike(f"%{city}%"),
#             Property.purpose == purpose,
#             Property.price <= budget,
#         )
#         .all()
#     )
 
#     if not results:
#         return {"message": "No property found", "results": []}
 
#     return {
#         "message": "Property found",
#         "count": len(results),
#         "results": results,
#     }
# end = time.time()
# logger.info(f"Search time: {(end - start) * 1000} milliseconds")
 
# # --------------------------------------------------
# # ➕ SAVE PROPERTY
# # --------------------------------------------------
 
# @property_router.post("/", status_code=status.HTTP_201_CREATED)
# def save_property(
#     payload: PropertyCreateRequest,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     logger.info(f"📥 Property create payload: {payload.dict()}")
 
#     try:
#         new_property = Property(
#             title=payload.title,
#             city=payload.city,
#             locality=payload.locality,
#             purpose=payload.purpose,
#             price=payload.price,
#             bhk=payload.bhk,
#             area_sqft=payload.area_sqft,
#             is_legal=payload.is_legal,
#             owner_name=payload.owner_name,
#             contact_phone=payload.contact_phone,
#             owner_user_id=user_id,
#         )
 
#         db.add(new_property)
#         db.commit()
#         db.refresh(new_property)
 
#         return {
#             "message": "Property saved successfully",
#             "property_id": new_property.property_id,
#         }
 
#     except Exception:
#         logger.exception("❌ Failed to save property")
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to save property",
#         )
 
 
# # --------------------------------------------------
# # 🌍 FETCH BY REGION
# # --------------------------------------------------
 
# @property_router.get("/region")
# def fetch_properties_by_region(
#     city: str,
#     locality: str | None = None,
#     purpose: str | None = None,
#     max_budget: int | None = None,
#     db: Session = Depends(get_db),
# ):
#     query = db.query(Property).filter(
#         Property.city.ilike(f"%{city}%")
#     )
 
#     if locality:
#         query = query.filter(Property.locality.ilike(f"%{locality}%"))
 
#     if purpose:
#         query = query.filter(Property.purpose == purpose)
 
#     if max_budget:
#         query = query.filter(Property.price <= max_budget)
 
#     results = query.all()
 
#     return {
#         "count": len(results),
#         "results": results,
#     }
 
 
# # --------------------------------------------------
# # ✏️ UPDATE PROPERTY
# # --------------------------------------------------
 
# @property_router.put("/{property_id}")
# def update_property(
#     property_id: int,
#     payload: PropertyCreateRequest,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     property_obj = (
#         db.query(Property)
#         .filter(
#             Property.property_id == property_id,
#             Property.owner_user_id == user_id,
#         )
#         .first()
#     )
 
#     if not property_obj:
#         raise HTTPException(
#             status_code=404,
#             detail="Property not found or unauthorized",
#         )
 
#     update_data = payload.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(property_obj, key, value)
 
#     db.commit()
#     db.refresh(property_obj)
 
#     return {
#         "message": "Property updated successfully",
#         "property": property_obj,
#     }
 
 
# # --------------------------------------------------
# # ❌ DELETE PROPERTY
# # --------------------------------------------------
 
# @property_router.delete("/{property_id}")
# def delete_property(
#     property_id: int,
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     property_obj = (
#         db.query(Property)
#         .filter(
#             Property.property_id == property_id,
#             Property.owner_user_id == user_id,
#         )
#         .first()
#     )
 
#     if not property_obj:
#         raise HTTPException(
#             status_code=404,
#             detail="Property not found or unauthorized",
#         )
 
#     db.delete(property_obj)
#     db.commit()
 
#     return {"message": "Property deleted successfully"}
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
 
from database import get_db
from models import Property
from schemas import PropertyCreateRequest, PropertyUpdateRequest , PropertySearchRequest
from auth import get_current_user
 
logger = logging.getLogger("property")
 
property_router = APIRouter(
    prefix="/properties",
    tags=["Properties"]
)
 
# --------------------------------------------------
# 🔍 SEARCH
# --------------------------------------------------
# @property_router.get("/search")
# def search_properties(
#     filters: PropertySearchRequest = Depends(),
#     # city: str,
#     # purpose: str,
#     # budget: int,
#     db: Session = Depends(get_db),
# ):
#     start = time.time()
 
#     results = (
#         db.query(Property)
#         .filter(
#             Property.city.ilike(f"%{city}%"),
#             Property.purpose == purpose,
#             Property.price <= budget,
#         )
#         .all()
#     )
 
#     end = time.time()
#     logger.info(f"🔍 Property search time: {(end - start) * 1000:.2f} ms")
 
#     if not results:
#         return {"message": "No property found", "results": []}
 
#     return {
#         "message": "Property found",
#         "count": len(results),
#         "results": results,
#     }

@property_router.get("/search")
def search_properties(
    filters: PropertySearchRequest = Depends(),
    db: Session = Depends(get_db),
):
    start = time.time()

    query = db.query(Property).filter(
        Property.city.ilike(f"%{filters.city}%")
    )

    if filters.purpose:
        query = query.filter(Property.purpose == filters.purpose)

    if filters.max_budget:
        query = query.filter(Property.price <= filters.max_budget)

    if filters.bhk:
        query = query.filter(Property.bhk == filters.bhk)

    if filters.locality:
        query = query.filter(Property.locality.ilike(f"%{filters.locality}%"))

    results = query.all()

    end = time.time()
    logger.info(f"🔍 Property search time: {(end - start) * 1000:.2f} ms")

    if not results:
        return {"message": "No property found", "results": []}

    return {
        "message": "Property found",
        "count": len(results),
        "results": results,
    }

 
# --------------------------------------------------
# ➕ SAVE PROPERTY
# --------------------------------------------------
@property_router.post("/", status_code=status.HTTP_201_CREATED)
def save_property(
    payload: PropertyCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"📥 Property create payload: {payload.dict()}")
 
    try:
        new_property = Property(
            **payload.dict(),
            owner_user_id=user_id,
        )
 
        db.add(new_property)
        db.commit()
        db.refresh(new_property)
 
        return {
            "message": "Property saved successfully",
            "property_id": new_property.property_id,
        }
 
    except Exception:
        logger.exception("❌ Failed to save property")
        raise HTTPException(
            status_code=500,
            detail="Failed to save property",
        )
 
# --------------------------------------------------
# 🌍 FETCH BY REGION
# --------------------------------------------------
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
        "results": results,
    }
 
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
        "message": "Property updated successfully",
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
 
    return {"message": "Property deleted successfully"}
 
 
    