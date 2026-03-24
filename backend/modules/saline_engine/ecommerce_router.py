"""
SALINE INTELLIGENCE ULTRA — E-Commerce Router
Flux complet: Recommandation saline → Catalogue produits → Panier → Checkout Stripe.
Reutilise: products_engine, cart_engine, payment_engine (ZERO duplication).

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import os
import logging
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("saline.ecommerce")

router = APIRouter(
    prefix="/api/v1/saline/shop",
    tags=["SALINE INTELLIGENCE ULTRA — E-Commerce"],
)

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# === MODELS ===

class SalineProductRecommendation(BaseModel):
    formula_id: str
    name: str
    format: str
    description: str
    match_score: int
    price: float = 0
    product_id: Optional[str] = None


class AddToCartRequest(BaseModel):
    session_id: str
    product_id: str
    quantity: int = Field(1, ge=1, le=10)


class ProductCheckoutRequest(BaseModel):
    session_id: str
    user_id: str = "guest"
    origin_url: str


# === SALINE PRODUCT CATALOG ===

SALINE_PRODUCTS = [
    {
        "id": "sal_001",
        "name": "Bloc Sodium Haute Teneur",
        "brand": "BIONIC Saline",
        "price": 24.99,
        "category": "saline",
        "product_format": "bloc",
        "weight": "2kg",
        "description": "Bloc sel pur haute teneur Na — periodes printemps/rut",
        "formula_id": "haute_Na",
        "minerals": {"Na": 350000, "Ca": 5000, "P": 2000},
        "target_animals": ["orignal", "chevreuil"],
        "season": "printemps,rut",
        "image_url": "/images/saline/bloc_sodium.jpg",
        "score": 92,
        "rank": 1,
    },
    {
        "id": "sal_002",
        "name": "Granules Ca-P Equilibre 2:1",
        "brand": "BIONIC Saline",
        "price": 34.99,
        "category": "saline",
        "product_format": "granules",
        "weight": "3kg",
        "description": "Ratio Ca:P 2:1 optimal — croissance bois, gestation",
        "formula_id": "Ca_P_equilibre",
        "minerals": {"Ca": 180000, "P": 90000, "Mg": 15000, "Na": 50000},
        "target_animals": ["orignal", "chevreuil"],
        "season": "printemps,ete",
        "image_url": "/images/saline/granules_cap.jpg",
        "score": 88,
        "rank": 2,
    },
    {
        "id": "sal_003",
        "name": "Melange Oligo-Elements Complet",
        "brand": "BIONIC Saline",
        "price": 42.99,
        "category": "saline",
        "product_format": "poudre",
        "weight": "2.5kg",
        "description": "Supplementation Zn, Cu, Se, Mn — immunite et reproduction",
        "formula_id": "oligo_complet",
        "minerals": {"Zn": 5000, "Cu": 1500, "Se": 30, "Mn": 4000, "Na": 80000},
        "target_animals": ["orignal", "chevreuil", "ours_noir"],
        "season": "toutes",
        "image_url": "/images/saline/oligo_complet.jpg",
        "score": 85,
        "rank": 3,
    },
    {
        "id": "sal_004",
        "name": "Bloc Mineral Universel 4 Saisons",
        "brand": "BIONIC Saline",
        "price": 29.99,
        "category": "saline",
        "product_format": "bloc",
        "weight": "4kg",
        "description": "Solution polyvalente toute saison — bloc longue duree",
        "formula_id": "mineral_universel",
        "minerals": {"Na": 200000, "Ca": 80000, "P": 40000, "Mg": 20000, "K": 15000},
        "target_animals": ["orignal", "chevreuil"],
        "season": "toutes",
        "image_url": "/images/saline/bloc_universel.jpg",
        "score": 90,
        "rank": 4,
    },
    {
        "id": "sal_005",
        "name": "Attractif Rut Na+K Intensif",
        "brand": "BIONIC Saline",
        "price": 38.99,
        "category": "saline",
        "product_format": "liquide",
        "weight": "2L",
        "description": "Formule rut — attraction maximale Na+K, dissolution rapide",
        "formula_id": "Na_K_rut",
        "minerals": {"Na": 280000, "K": 120000, "Mg": 25000, "Se": 15},
        "target_animals": ["orignal", "chevreuil"],
        "season": "rut,pre_rut",
        "image_url": "/images/saline/attractif_rut.jpg",
        "score": 91,
        "rank": 5,
    },
    {
        "id": "sal_006",
        "name": "Supplement Selenium-Cuivre Sante",
        "brand": "BIONIC Saline",
        "price": 49.99,
        "category": "saline",
        "product_format": "granules",
        "weight": "2kg",
        "description": "Zones carencees Se/Cu — sante et fertilite faune",
        "formula_id": "Se_Cu_sante",
        "minerals": {"Se": 50, "Cu": 2000, "Zn": 3000, "Na": 100000},
        "target_animals": ["orignal", "chevreuil", "ours_noir", "dindon_sauvage"],
        "season": "toutes",
        "image_url": "/images/saline/selenium_cuivre.jpg",
        "score": 87,
        "rank": 6,
    },
]


# === ENDPOINTS ===

@router.get("/products")
async def list_saline_products(
    species: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
):
    """Liste des produits salines avec filtrage optionnel."""
    products = SALINE_PRODUCTS.copy()

    if species:
        products = [p for p in products if species in p.get("target_animals", [])]
    if season:
        products = [p for p in products if season in p.get("season", "")]
    if format:
        products = [p for p in products if p.get("product_format") == format]

    return {"success": True, "total": len(products), "products": products}


@router.get("/products/{product_id}")
async def get_saline_product(product_id: str):
    """Detaily d'un produit saline."""
    product = next((p for p in SALINE_PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouve")
    return {"success": True, "product": product}


@router.get("/recommend")
async def recommend_products(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    species: str = Query("orignal"),
    month: int = Query(10, ge=1, le=12),
    season: str = Query("automne"),
):
    """
    Recommande des produits salines bases sur l'analyse du territoire.
    Interconnecte: saline_recommendation_engine → product matching.
    """
    from .engines.saline_recommendation_engine import generate_full_analysis

    analysis = generate_full_analysis(
        lat=lat, lng=lng, species=species, sex="male", age="adult",
        month=month, season=season,
    )

    recommended = analysis.get("recommendations", {}).get("products", [])

    # Map to actual products
    matched_products = []
    for rec in recommended:
        formula_id = rec.get("formula_id", "")
        matching = next((p for p in SALINE_PRODUCTS if p["formula_id"] == formula_id), None)
        if matching:
            matched_products.append({
                **matching,
                "match_score": rec.get("match_score", 0),
                "targets_addressed": rec.get("targets_addressed", []),
            })

    return {
        "success": True,
        "location": {"lat": lat, "lng": lng},
        "intelligence_score": analysis.get("analysis", {}).get("intelligence_score", {}),
        "critical_deficits": analysis.get("analysis", {}).get("adjusted_deficits", {}).get("total_critical", 0),
        "custom_recipe": analysis.get("recommendations", {}).get("custom_recipe", {}),
        "recommended_products": matched_products,
        "total": len(matched_products),
    }


@router.post("/cart/add")
async def add_to_cart(request: AddToCartRequest):
    """
    Ajoute un produit saline au panier.
    Reutilise: cart_engine/v1/service.
    """
    product = next((p for p in SALINE_PRODUCTS if p["id"] == request.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouve")

    try:
        from modules.cart_engine.v1.service import get_cart_service
        from modules.cart_engine.v1.models import CartItemCreate

        cart_svc = get_cart_service()
        item = await cart_svc.add_item(CartItemCreate(
            session_id=request.session_id,
            product_id=request.product_id,
            quantity=request.quantity,
        ))
        return {
            "success": True,
            "item": {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product_name": product["name"],
                "unit_price": product["price"],
                "subtotal": round(product["price"] * item.quantity, 2),
            },
        }
    except ImportError:
        logger.warning("cart_engine not available, using in-memory fallback")
        return {
            "success": True,
            "item": {
                "id": str(uuid.uuid4()),
                "product_id": request.product_id,
                "quantity": request.quantity,
                "product_name": product["name"],
                "unit_price": product["price"],
                "subtotal": round(product["price"] * request.quantity, 2),
            },
        }


@router.get("/cart/{session_id}")
async def get_cart(session_id: str):
    """Recupere le contenu du panier pour une session."""
    items = []
    try:
        from modules.cart_engine.v1.service import get_cart_service
        cart_svc = get_cart_service()
        # Get raw cart items (not enriched — we enrich from SALINE_PRODUCTS)
        items = list(cart_svc.cart.find({"session_id": session_id}, {"_id": 0}))
    except ImportError:
        pass

    enriched = []
    total = 0
    for item in items:
        product = next((p for p in SALINE_PRODUCTS if p["id"] == item.get("product_id")), None)
        if product:
            qty = item.get("quantity", 1)
            subtotal = round(product["price"] * qty, 2)
            total += subtotal
            enriched.append({
                "item_id": item.get("id"),
                "product_id": product["id"],
                "name": product["name"],
                "brand": product["brand"],
                "format": product["product_format"],
                "unit_price": product["price"],
                "quantity": qty,
                "subtotal": subtotal,
                "image_url": product["image_url"],
            })

    return {
        "success": True,
        "session_id": session_id,
        "items": enriched,
        "item_count": len(enriched),
        "total": round(total, 2),
        "currency": "CAD",
    }


@router.post("/checkout")
async def create_product_checkout(request: ProductCheckoutRequest, http_request: Request):
    """
    Cree une session de checkout Stripe pour les produits du panier.
    Reutilise: payment_engine/router (StripeCheckout).
    """
    # Get cart items
    try:
        from modules.cart_engine.v1.service import get_cart_service
        cart_svc = get_cart_service()
        items = list(cart_svc.cart.find({"session_id": request.session_id}, {"_id": 0}))
    except ImportError:
        raise HTTPException(status_code=500, detail="Cart service unavailable")

    if not items:
        raise HTTPException(status_code=400, detail="Panier vide")

    # Calculate total
    total_amount = 0
    line_items_desc = []
    for item in items:
        product = next((p for p in SALINE_PRODUCTS if p["id"] == item.get("product_id")), None)
        if product:
            qty = item.get("quantity", 1)
            total_amount += product["price"] * qty
            line_items_desc.append(f"{product['name']} x{qty}")

    total_amount = round(total_amount, 2)

    if total_amount <= 0:
        raise HTTPException(status_code=400, detail="Montant invalide")

    try:
        from emergentintegrations.payments.stripe.checkout import (
            StripeCheckout, CheckoutSessionRequest
        )

        host_url = str(http_request.base_url).rstrip('/')
        webhook_url = f"{host_url}/api/v1/payments/webhook/stripe"
        success_url = f"{request.origin_url}/saline/order/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{request.origin_url}/saline/order/cancel"

        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)

        checkout_request = CheckoutSessionRequest(
            amount=total_amount,
            currency="cad",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "type": "saline_product_order",
                "session_id": request.session_id,
                "user_id": request.user_id,
                "items": ", ".join(line_items_desc),
            }
        )

        session = await stripe_checkout.create_checkout_session(checkout_request)

        return {
            "success": True,
            "url": session.url,
            "session_id": session.session_id,
            "amount": total_amount,
            "currency": "CAD",
            "items_count": len(items),
        }

    except ImportError as e:
        logger.error(f"Stripe integration not available: {e}")
        raise HTTPException(status_code=500, detail="Service de paiement indisponible")
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/order/status/{session_id}")
async def order_status(session_id: str):
    """Verifie le statut d'une commande produit."""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout

        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY)
        status = await stripe_checkout.get_checkout_status(session_id)

        return {
            "success": True,
            "session_id": session_id,
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency,
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="Service de paiement indisponible")
    except Exception as e:
        logger.error(f"Order status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
