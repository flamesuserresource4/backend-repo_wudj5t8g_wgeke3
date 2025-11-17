import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="The Practice Bay API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# Models (response shapes)
# -----------------------
class ProductResponse(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    details: Optional[str] = None
    price: float
    rating: float = 4.8
    reviews_count: int = 127
    images: List[str] = []
    video: Optional[str] = None
    benefits: List[str] = []
    in_stock: bool = True
    category: str = "training"


class TestimonialResponse(BaseModel):
    name: str
    quote: str
    rating: float = 5.0
    photo: Optional[str] = None


class BundleResponse(BaseModel):
    title: str
    description: Optional[str] = None
    items: List[str]
    regular_price: float
    bundle_price: float
    savings_text: Optional[str] = None
    image: Optional[str] = None


# -----------------------
# Seed data
# -----------------------
SEED_PRODUCTS: List[dict] = [
    {
        "title": "Premium 10ft Putting Mat",
        "slug": "premium-putting-mat-10ft",
        "description": "Tournament-grade putting mat with auto-ball return.",
        "details": "Premium velvet surface, true roll, printed alignment guides.",
        "price": 129.0,
        "rating": 4.8,
        "reviews_count": 127,
        "images": [
            "https://images.unsplash.com/photo-1604490205019-95898235570d?q=80&w=1600&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?q=80&w=1600&auto=format&fit=crop"
        ],
        "benefits": [
            "Improves putting accuracy by 40%",
            "Professional auto-ball return system",
            "Premium velvet surface mimics real greens",
            "Non-slip backing for any floor",
            "Rolls up for easy storage"
        ],
        "in_stock": True,
        "category": "training"
    },
    {
        "title": "Swing Trainer Aid",
        "slug": "swing-trainer-aid",
        "description": "Build power and consistency with tempo training.",
        "details": "Weighted shaft for perfect tempo and plane.",
        "price": 69.0,
        "rating": 4.8,
        "reviews_count": 98,
        "images": [
            "https://images.unsplash.com/photo-1511715282685-5f1f1c9b1b97?q=80&w=1600&auto=format&fit=crop"
        ],
        "benefits": [
            "Builds a repeatable swing",
            "Improves sequencing and timing",
            "Warm-up tool before rounds"
        ],
        "in_stock": True,
        "category": "training"
    },
    {
        "title": "Alignment Sticks (3-Pack)",
        "slug": "alignment-sticks-3-pack",
        "description": "Versatile training for aim, swing plane, and setup.",
        "details": "Durable fiberglass with protective caps.",
        "price": 24.0,
        "rating": 4.9,
        "reviews_count": 213,
        "images": [
            "https://images.unsplash.com/photo-1549058912-e7564e5a7f66?q=80&w=1600&auto=format&fit=crop"
        ],
        "benefits": ["Immediate setup feedback", "Multi-use practice aid"],
        "in_stock": True,
        "category": "training"
    },
    {
        "title": "Chipping Practice Net",
        "slug": "chipping-practice-net",
        "description": "Foldable net for precision short-game training.",
        "details": "Targets at multiple heights, indoor/outdoor use.",
        "price": 49.0,
        "rating": 4.7,
        "reviews_count": 156,
        "images": [
            "https://images.unsplash.com/photo-1570951525721-50e756c1c8fe?q=80&w=1600&auto=format&fit=crop"
        ],
        "benefits": ["Dial in distance control", "Compact and portable"],
        "in_stock": True,
        "category": "training"
    },
    {
        "title": "Practice Balls (Dozen)",
        "slug": "practice-balls-dozen",
        "description": "Soft-flight practice balls safe for indoor use.",
        "details": "Realistic feel with reduced flight distance.",
        "price": 23.0,
        "rating": 4.6,
        "reviews_count": 87,
        "images": [
            "https://images.unsplash.com/photo-1502877338535-766e1452684a?q=80&w=1600&auto=format&fit=crop"
        ],
        "benefits": ["Safe indoors", "Durable construction"],
        "in_stock": True,
        "category": "training"
    }
]

SEED_TESTIMONIALS: List[dict] = [
    {
        "name": "Mike R.",
        "quote": "Dropped 5 strokes in 2 months!",
        "rating": 5,
        "photo": "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "Sarah K.",
        "quote": "My living room turned into a putting studio.",
        "rating": 5,
        "photo": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?q=80&w=1200&auto=format&fit=crop"
    },
    {
        "name": "Jamal D.",
        "quote": "Consistent practice finally feels easy.",
        "rating": 5,
        "photo": "https://images.unsplash.com/photo-1520975922215-cfe9366c67a8?q=80&w=1200&auto=format&fit=crop"
    }
]

SEED_BUNDLE: dict = {
    "title": "The Complete Home Training System",
    "description": "Everything you need to practice like a pro at home.",
    "items": [p["slug"] for p in SEED_PRODUCTS],
    "regular_price": 294.0,
    "bundle_price": 219.0,
    "savings_text": "Save $75!",
    "image": "https://images.unsplash.com/photo-1501706362039-c06b2d715385?q=80&w=1600&auto=format&fit=crop"
}


def seed_if_empty():
    if db is None:
        return
    # Products
    if db["product"].count_documents({}) == 0:
        db["product"].insert_many(SEED_PRODUCTS)
    # Testimonials
    if db["testimonial"].count_documents({}) == 0:
        db["testimonial"].insert_many(SEED_TESTIMONIALS)
    # Bundle
    if db["bundle"].count_documents({}) == 0:
        db["bundle"].insert_one(SEED_BUNDLE)


@app.on_event("startup")
async def on_startup():
    try:
        seed_if_empty()
    except Exception:
        pass


@app.get("/")
def read_root():
    return {"message": "The Practice Bay API running"}


@app.get("/api/products", response_model=List[ProductResponse])
def list_products():
    seed_if_empty()
    if db is None:
        return [ProductResponse(**p) for p in SEED_PRODUCTS]
    products = list(db["product"].find({}, {"_id": 0}))
    return products


@app.get("/api/products/{slug}", response_model=ProductResponse)
def get_product(slug: str):
    seed_if_empty()
    if db is None:
        for p in SEED_PRODUCTS:
            if p["slug"] == slug:
                return p
        raise HTTPException(status_code=404, detail="Product not found")
    p = db["product"].find_one({"slug": slug}, {"_id": 0})
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@app.get("/api/testimonials", response_model=List[TestimonialResponse])
def list_testimonials():
    seed_if_empty()
    if db is None:
        return [TestimonialResponse(**t) for t in SEED_TESTIMONIALS]
    return list(db["testimonial"].find({}, {"_id": 0}))


@app.get("/api/bundle", response_model=BundleResponse)
def get_bundle():
    seed_if_empty()
    if db is None:
        return BundleResponse(**SEED_BUNDLE)
    b = db["bundle"].find_one({}, {"_id": 0})
    return b


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
