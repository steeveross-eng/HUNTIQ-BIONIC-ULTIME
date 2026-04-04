"""
Cart Engine Router — V1 (legacy) + V2 (P5-OPTIMIZATION)
=========================================================
Directive x5400-F STEEVE-MAX
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

V1 endpoints (INCHANGES): /health, /stats, /session/{id}, POST /, PUT /{id}, DELETE /{id}, DELETE /session/{id}/clear
V2 endpoints (NOUVEAUX): /user/{user_id}, /user/{user_id}/items, etc.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from .models import CartItem, CartItemCreate, CartItemUpdate
from .service import get_cart_service

router = APIRouter(prefix="/api/v1/cart", tags=["Cart Engine"])


# ==============================================
# V2 MODELS — P5-OPTIMIZATION
# ==============================================

class AddItemRequest(BaseModel):
    product_type: str = Field(description="package | addon | feature")
    product_id: str
    name: str
    unit_price: float
    quantity: int = 1
    description: str = ""
    metadata: Optional[Dict] = None

class UpdateQuantityRequest(BaseModel):
    quantity: int

class ApplyPromoRequest(BaseModel):
    promo_code: str


# ==============================================
# V1 ENDPOINTS (ZERO LOSS — INCHANGES)
# ==============================================

class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    message: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    service = get_cart_service()
    stats = await service.get_stats()
    return HealthResponse(
        status="operational", engine="cart_engine", version="2.0.0",
        message=f"Engine operationnel - Cart V2 P5-OPTIMIZATION"
    )

@router.get("/stats")
async def get_stats():
    service = get_cart_service()
    return await service.get_stats()

@router.get("/session/{session_id}")
async def get_cart_v1(session_id: str):
    service = get_cart_service()
    return await service.get_by_session(session_id)

@router.post("/", response_model=CartItem)
async def add_to_cart_v1(item_input: CartItemCreate):
    service = get_cart_service()
    return await service.add_item(item_input)

@router.put("/{item_id}", response_model=CartItem)
async def update_cart_item_v1(item_id: str, update_data: CartItemUpdate):
    service = get_cart_service()
    item = await service.update_item(item_id, update_data)
    if not item:
        raise HTTPException(status_code=404, detail="Item non trouve")
    return item

@router.delete("/{item_id}")
async def delete_cart_item_v1(item_id: str):
    service = get_cart_service()
    success = await service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item non trouve")
    return {"success": True, "message": "Item supprime"}

@router.delete("/session/{session_id}/clear")
async def clear_cart_v1(session_id: str):
    service = get_cart_service()
    count = await service.clear_session(session_id)
    return {"success": True, "items_removed": count}


# ==============================================
# V2 ENDPOINTS — P5-A: CRUD PANIER UTILISATEUR
# ==============================================

from modules.cart_engine.services import cart_service as cs
from modules.cart_engine.services import cart_validator as cv
from modules.cart_engine.services import cart_promotions as cp
from modules.cart_engine.services import cart_sync_bridge as csb


@router.get("/user/{user_id}")
async def get_user_cart(user_id: str):
    """P5-A: Recuperer le panier actif d'un utilisateur."""
    cart = await cs.get_or_create_cart(user_id)
    return {
        "success": True,
        "cart": cart,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5A"
    }


@router.post("/user/{user_id}/items")
async def add_item_to_cart(user_id: str, item: AddItemRequest):
    """P5-A: Ajouter un article au panier."""
    cart = await cs.add_item(
        user_id=user_id,
        product_type=item.product_type,
        product_id=item.product_id,
        name=item.name,
        unit_price=item.unit_price,
        quantity=item.quantity,
        description=item.description,
        metadata=item.metadata
    )
    return {
        "success": True,
        "cart": cart,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5A"
    }


@router.patch("/user/{user_id}/items/{item_id}")
async def update_item_quantity(user_id: str, item_id: str, data: UpdateQuantityRequest):
    """P5-A: Modifier la quantite d'un article."""
    cart = await cs.update_quantity(user_id, item_id, data.quantity)
    if cart is None:
        raise HTTPException(status_code=404, detail="Article non trouve dans le panier")
    return {
        "success": True,
        "cart": cart,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5A"
    }


@router.delete("/user/{user_id}/items/{item_id}")
async def remove_cart_item(user_id: str, item_id: str):
    """P5-A: Supprimer un article du panier."""
    cart = await cs.remove_item(user_id, item_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Article non trouve dans le panier")
    return {
        "success": True,
        "cart": cart,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5A"
    }


@router.delete("/user/{user_id}/clear")
async def clear_user_cart(user_id: str):
    """P5-A: Vider le panier."""
    cart = await cs.clear_cart(user_id)
    return {
        "success": True,
        "cart": cart,
        "message": "Panier vide",
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5A"
    }


@router.get("/user/{user_id}/summary")
async def get_cart_summary(user_id: str):
    """P5-A: Resume du panier avec totaux."""
    summary = await cs.get_cart_summary(user_id)
    return {
        "success": True,
        "summary": summary,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5A"
    }


# ==============================================
# V2 ENDPOINTS — P5-B: VALIDATION & PROMOTIONS
# ==============================================

@router.post("/user/{user_id}/validate")
async def validate_user_cart(user_id: str):
    """P5-B: Validation pre-checkout."""
    cart = await cs.get_or_create_cart(user_id)
    validation = await cv.validate_cart(cart)
    eligibility = await cv.check_tier_eligibility(user_id, cart.get("items", []))
    return {
        "success": True,
        "validation": validation,
        "eligibility": eligibility,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5B"
    }


@router.post("/user/{user_id}/promotions")
async def apply_promo(user_id: str, data: ApplyPromoRequest):
    """P5-B: Appliquer un code promo."""
    result = await cp.apply_promotion(user_id, data.promo_code)
    if result.get("success"):
        cart = await cs.get_or_create_cart(user_id)
        result["cart"] = cart
    return {
        **result,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5B"
    }


@router.delete("/user/{user_id}/promotions/{promo_code}")
async def remove_promo(user_id: str, promo_code: str):
    """P5-B: Retirer un code promo."""
    result = await cp.remove_promotion(user_id, promo_code)
    if result.get("success"):
        cart = await cs.get_or_create_cart(user_id)
        result["cart"] = cart
    return {
        **result,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5B"
    }


@router.post("/user/{user_id}/checkout")
async def checkout_cart(user_id: str):
    """P5-B: Initier le checkout (cree commande, marque panier checked_out)."""
    cart = await cs.get_or_create_cart(user_id)

    validation = await cv.validate_cart(cart)
    if not validation["valid"]:
        return {
            "success": False,
            "error": "VALIDATION_FAILED",
            "validation": validation,
            "source": "cart_engine_v2",
            "directive": "x5400-F-P5B"
        }

    order_id = await csb.notify_cart_checkout(user_id, cart)
    await cs.set_cart_status(user_id, "checked_out")

    return {
        "success": True,
        "order_id": order_id,
        "total": cart.get("total", 0),
        "currency": cart.get("currency", "CAD"),
        "item_count": cart.get("item_count", 0),
        "message": "Commande creee. Paiement en attente.",
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5B"
    }


# ==============================================
# V2 ENDPOINTS — P5-C: SYNCHRONISATION
# ==============================================

@router.post("/user/{user_id}/sync")
async def sync_cart(user_id: str):
    """P5-C: Synchroniser panier avec quotas/tier."""
    freemium_status = await csb.sync_freemium_status(user_id)
    cart = await cs.get_or_create_cart(user_id)
    return {
        "success": True,
        "cart": cart,
        "freemium_status": freemium_status,
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5C"
    }


@router.get("/user/{user_id}/suggestions")
async def get_suggestions(user_id: str):
    """P5-C: Suggestions upsell basees sur le panier."""
    cart = await cs.get_or_create_cart(user_id)
    suggestions = await csb.get_upsell_suggestions(user_id, cart)
    return {
        "success": True,
        "suggestions": suggestions,
        "suggestion_count": len(suggestions),
        "source": "cart_engine_v2",
        "directive": "x5400-F-P5C"
    }
