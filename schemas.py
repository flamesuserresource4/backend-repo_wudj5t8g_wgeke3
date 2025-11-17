"""
Database Schemas

Pydantic models that map to MongoDB collections.
Each class name lowercased is the collection name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Product(BaseModel):
    """
    Collection: product
    """
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="URL-safe identifier")
    description: Optional[str] = Field(None, description="Short description")
    details: Optional[str] = Field(None, description="Full details/long description")
    price: float = Field(..., ge=0, description="Price in USD")
    rating: float = Field(4.8, ge=0, le=5, description="Average star rating")
    reviews_count: int = Field(0, ge=0, description="Number of reviews")
    images: List[HttpUrl] = Field(default_factory=list, description="Image URLs")
    video: Optional[HttpUrl] = Field(None, description="Optional product video URL")
    benefits: List[str] = Field(default_factory=list, description="Key benefits")
    in_stock: bool = Field(True)
    category: str = Field("training", description="Category name")


class Testimonial(BaseModel):
    """
    Collection: testimonial
    """
    name: str = Field(..., description="Customer first name and initial")
    quote: str = Field(..., description="Short quote")
    rating: float = Field(5.0, ge=0, le=5)
    photo: Optional[HttpUrl] = Field(None, description="Customer setup photo")


class Bundle(BaseModel):
    """
    Collection: bundle
    """
    title: str
    description: Optional[str] = None
    items: List[str] = Field(default_factory=list, description="List of product slugs included")
    regular_price: float
    bundle_price: float
    savings_text: Optional[str] = None
    image: Optional[HttpUrl] = None
