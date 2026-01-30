from sqlalchemy.orm import Session
from models import Property

def search_properties(db: Session, city: str, purpose: str, budget: int):
    return db.query(Property).filter(
        Property.city.ilike(f"%{city}%"),
        Property.purpose == purpose,
        Property.price <= budget
    ).all()
