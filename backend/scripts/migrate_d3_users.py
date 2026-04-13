"""
D3 Migration Script — BCE-4X Phase P2
Migrate users from marketplace_sellers, land_owners, land_renters → users collection.
Deduplication by email. SHA256 hashes preserved (auto re-hash on first login via auth_engine).

Usage: python -m scripts.migrate_d3_users
"""
import asyncio
import os
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("D3-MIGRATION")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "bionic_territory")


async def migrate():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    stats = {"created": 0, "skipped_existing": 0, "roles_updated": 0, "errors": 0}
    now = datetime.now(timezone.utc)

    # --- 1. Marketplace sellers ---
    sellers = await db.marketplace_sellers.find({}, {"_id": 0}).to_list(length=10000)
    logger.info(f"Found {len(sellers)} marketplace sellers")

    for seller in sellers:
        email = seller.get("email", "").lower().strip()
        if not email:
            continue
        existing = await db.users.find_one({"email": email}, {"_id": 0})
        if existing:
            # Add role if missing
            roles = existing.get("roles", [])
            if "marketplace_seller" not in roles:
                roles.append("marketplace_seller")
                await db.users.update_one(
                    {"email": email},
                    {"$set": {"roles": roles, "marketplace_seller_id": seller.get("id")}}
                )
                stats["roles_updated"] += 1
                logger.info(f"  Updated roles for {email} (+marketplace_seller)")
            stats["skipped_existing"] += 1
            continue

        user_doc = {
            "user_id": f"user_{seller.get('id', '')[:12]}",
            "name": seller.get("name", "Vendeur"),
            "email": email,
            "phone": seller.get("phone"),
            "password_hash": seller.get("password_hash", ""),
            "auth_provider": "local",
            "role": "hunter",
            "roles": ["marketplace_seller"],
            "marketplace_seller_id": seller.get("id"),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        try:
            await db.users.insert_one(user_doc)
            stats["created"] += 1
            logger.info(f"  Created user for seller {email}")
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"  Error creating user for {email}: {e}")

    # --- 2. Land owners ---
    owners = await db.land_owners.find({}, {"_id": 0}).to_list(length=10000)
    logger.info(f"Found {len(owners)} land owners")

    for owner in owners:
        email = owner.get("email", "").lower().strip()
        if not email:
            continue
        existing = await db.users.find_one({"email": email}, {"_id": 0})
        if existing:
            roles = existing.get("roles", [])
            if "land_owner" not in roles:
                roles.append("land_owner")
                await db.users.update_one(
                    {"email": email},
                    {"$set": {"roles": roles, "land_owner_id": owner.get("id")}}
                )
                stats["roles_updated"] += 1
                logger.info(f"  Updated roles for {email} (+land_owner)")
            stats["skipped_existing"] += 1
            continue

        user_doc = {
            "user_id": f"user_{owner.get('id', '')[:12]}",
            "name": owner.get("name", "Proprietaire"),
            "email": email,
            "phone": owner.get("phone"),
            "password_hash": owner.get("hashed_password", ""),
            "auth_provider": "local",
            "role": "hunter",
            "roles": ["land_owner"],
            "land_owner_id": owner.get("id"),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        try:
            await db.users.insert_one(user_doc)
            stats["created"] += 1
            logger.info(f"  Created user for owner {email}")
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"  Error creating user for {email}: {e}")

    # --- 3. Land renters ---
    renters = await db.land_renters.find({}, {"_id": 0}).to_list(length=10000)
    logger.info(f"Found {len(renters)} land renters")

    for renter in renters:
        email = renter.get("email", "").lower().strip()
        if not email:
            continue
        existing = await db.users.find_one({"email": email}, {"_id": 0})
        if existing:
            roles = existing.get("roles", [])
            if "land_renter" not in roles:
                roles.append("land_renter")
                await db.users.update_one(
                    {"email": email},
                    {"$set": {"roles": roles, "land_renter_id": renter.get("id")}}
                )
                stats["roles_updated"] += 1
                logger.info(f"  Updated roles for {email} (+land_renter)")
            stats["skipped_existing"] += 1
            continue

        user_doc = {
            "user_id": f"user_{renter.get('id', '')[:12]}",
            "name": renter.get("name", "Locataire"),
            "email": email,
            "phone": renter.get("phone"),
            "password_hash": renter.get("hashed_password", ""),
            "auth_provider": "local",
            "role": "hunter",
            "roles": ["land_renter"],
            "land_renter_id": renter.get("id"),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        try:
            await db.users.insert_one(user_doc)
            stats["created"] += 1
            logger.info(f"  Created user for renter {email}")
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"  Error creating user for {email}: {e}")

    logger.info("=" * 60)
    logger.info(f"D3 MIGRATION COMPLETE")
    logger.info(f"  Created: {stats['created']}")
    logger.info(f"  Skipped (existing): {stats['skipped_existing']}")
    logger.info(f"  Roles updated: {stats['roles_updated']}")
    logger.info(f"  Errors: {stats['errors']}")
    logger.info("=" * 60)

    client.close()
    return stats


if __name__ == "__main__":
    asyncio.run(migrate())
