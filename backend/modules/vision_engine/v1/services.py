"""
Vision Engine — Service Layer
IA Vision analysis: species, sex, size, ALPHA scoring, trajectories
Uses LLM Vision (GPT Image 1) via Emergent LLM Key
"""
import os
import json
import uuid
import base64
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorDatabase

load_dotenv()
logger = logging.getLogger(__name__)

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

VISION_SYSTEM_PROMPT = """You are an expert wildlife photo analyst for Quebec hunting territory management.
Analyze the trail camera photo and return ONLY a JSON object (no markdown, no explanation) with these fields:
{
  "species": "string (orignal|cerf|ours_noir|caribou|dindon|chevreuil|loup|coyote|lynx|renard|castor|lièvre|inconnu|aucun_animal)",
  "sex": "string (male|femelle|indetermine)",
  "size_estimate": "string (very_large|large|medium|small|juvenile)",
  "antler_points": "integer or null (number of antler points if visible, null otherwise)",
  "alpha_score": "integer 1-99 (dominance score based on size, antlers, posture, muscle mass)",
  "behavior": "string (feeding|moving|resting|alert|rut|territorial|unknown)",
  "activity_level": "string (high|medium|low)",
  "individuals_count": "integer (number of animals visible)",
  "photo_quality": "integer 1-100",
  "confidence": "float 0.0-1.0",
  "description_fr": "string (brief French description of the scene)"
}
If no animal is visible, set species to "aucun_animal" and alpha_score to 0.
Return ONLY the JSON object, nothing else."""


class VisionAnalysisService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.analyses = db["vision_analyses"]
        self.individuals = db["vision_individuals"]
        self.trajectories = db["vision_trajectories"]
        self.hotspots = db["vision_hotspots"]

    async def analyze_photo(self, user_id: str, photo_id: str, camera_id: str,
                            image_data: bytes, mime_type: str = "image/jpeg",
                            gps_lat: Optional[float] = None, gps_lon: Optional[float] = None,
                            event_id: Optional[str] = None) -> dict:
        """Analyze a photo using LLM Vision and store results."""
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

        analysis_id = str(uuid.uuid4())

        try:
            # Encode image to base64
            img_b64 = base64.b64encode(image_data).decode("utf-8")

            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id=f"vision_{analysis_id}",
                system_message=VISION_SYSTEM_PROMPT
            ).with_model("openai", "gpt-4o")

            image_content = ImageContent(image_base64=img_b64)
            user_msg = UserMessage(
                text="Analyze this trail camera photo. Return ONLY the JSON object.",
                file_contents=[image_content]
            )

            raw_response = await chat.send_message(user_msg)

            # Parse JSON from response
            analysis = self._parse_vision_response(raw_response)

        except Exception as e:
            logger.error(f"Vision API error: {e}")
            # Fallback to simulated analysis
            analysis = self._simulated_analysis(photo_id)
            analysis["_fallback"] = True

        # Build location
        location = None
        if gps_lat and gps_lon:
            location = {"type": "Point", "coordinates": [gps_lon, gps_lat]}

        doc = {
            "id": analysis_id,
            "user_id": user_id,
            "photo_id": photo_id,
            "event_id": event_id,
            "camera_id": camera_id,
            "species": analysis.get("species", "inconnu"),
            "sex": analysis.get("sex", "indetermine"),
            "size_estimate": analysis.get("size_estimate", "medium"),
            "antler_points": analysis.get("antler_points"),
            "alpha_score": analysis.get("alpha_score", 50),
            "behavior": analysis.get("behavior", "unknown"),
            "activity_level": analysis.get("activity_level", "medium"),
            "individuals_count": analysis.get("individuals_count", 1),
            "photo_quality": analysis.get("photo_quality", 50),
            "confidence": analysis.get("confidence", 0.5),
            "description_fr": analysis.get("description_fr", ""),
            "gps_lat": gps_lat,
            "gps_lon": gps_lon,
            "location": location,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "model_version": "gpt-4o",
            "is_fallback": analysis.get("_fallback", False),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        await self.analyses.insert_one(doc)
        doc.pop("_id", None)
        logger.info(f"Vision analysis {analysis_id}: {doc['species']} score={doc['alpha_score']}")
        return doc

    def _parse_vision_response(self, raw: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [line for line in lines if not line.startswith("```")]
            text = "\n".join(lines)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            logger.warning(f"Could not parse vision response: {text[:200]}")
            return {"species": "inconnu", "alpha_score": 50, "confidence": 0.0}

    def _simulated_analysis(self, photo_id: str) -> dict:
        """Fallback simulated analysis when API unavailable."""
        h = hash(photo_id) % 1000
        species_list = ["orignal", "cerf", "ours_noir", "caribou", "dindon", "chevreuil"]
        return {
            "species": species_list[h % len(species_list)],
            "sex": "male" if h % 3 != 0 else "femelle",
            "size_estimate": ["large", "medium", "very_large"][h % 3],
            "antler_points": (h % 14) + 2 if h % 3 != 0 else None,
            "alpha_score": min(99, max(20, 50 + (h % 45))),
            "behavior": ["feeding", "moving", "resting", "alert"][h % 4],
            "activity_level": ["high", "medium", "low"][h % 3],
            "individuals_count": 1 + (h % 3),
            "photo_quality": 60 + (h % 35),
            "confidence": 0.7,
            "description_fr": "Analyse simulee (API indisponible)"
        }

    async def get_analyses(self, user_id: str, camera_id: Optional[str] = None,
                           species: Optional[str] = None, limit: int = 100) -> list:
        """Get vision analyses for a user."""
        query = {"user_id": user_id}
        if camera_id:
            query["camera_id"] = camera_id
        if species:
            query["species"] = species
        cursor = self.analyses.find(query, {"_id": 0}).sort("analyzed_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def generate_hotspots(self, user_id: str) -> list:
        """Generate ALPHA hotspots from vision analyses."""
        analyses = await self.get_analyses(user_id, limit=500)
        # Group by approximate location (0.01 degree grid ~ 1km)
        grids = {}
        for a in analyses:
            if not a.get("gps_lat") or a.get("species") == "aucun_animal":
                continue
            key = f"{round(a['gps_lat'], 2)}_{round(a['gps_lon'], 2)}"
            if key not in grids:
                grids[key] = {"lat": a["gps_lat"], "lon": a["gps_lon"], "analyses": []}
            grids[key]["analyses"].append(a)

        hotspots = []
        for key, g in grids.items():
            aa = g["analyses"]
            species_set = list(set(a["species"] for a in aa))
            avg_score = sum(a.get("alpha_score", 0) for a in aa) / len(aa)
            alpha_count = sum(1 for a in aa if a.get("alpha_score", 0) >= 85)
            peak_hours = self._compute_peak_hours(aa)

            hs = {
                "id": f"hs_{str(uuid.uuid4())[:8]}",
                "user_id": user_id,
                "gps_lat": g["lat"],
                "gps_lon": g["lon"],
                "location": {"type": "Point", "coordinates": [g["lon"], g["lat"]]},
                "score": round(avg_score),
                "species": species_set,
                "dominant_species": max(set(a["species"] for a in aa), key=lambda s: sum(1 for x in aa if x["species"] == s)),
                "alpha_count": alpha_count,
                "total_sightings": len(aa),
                "activity_level": "extreme" if len(aa) >= 10 else "high" if len(aa) >= 5 else "moderate",
                "peak_hours": peak_hours,
                "radius_m": 800 if any(s in ["orignal", "caribou"] for s in species_set) else 600,
                "last_activity": max(a.get("analyzed_at", "") for a in aa),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            hotspots.append(hs)

        # Store hotspots
        if hotspots:
            await self.hotspots.delete_many({"user_id": user_id})
            await self.hotspots.insert_many(hotspots)
            # Remove _id from returned docs
            for hs in hotspots:
                hs.pop("_id", None)

        return sorted(hotspots, key=lambda h: h["score"], reverse=True)

    async def get_hotspots(self, user_id: str) -> list:
        """Get stored ALPHA hotspots."""
        cursor = self.hotspots.find({"user_id": user_id}, {"_id": 0}).sort("score", -1)
        return await cursor.to_list(length=100)

    async def generate_trajectories(self, user_id: str, days: int = 30) -> list:
        """Generate trajectories from multi-camera temporal sequences."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        analyses = await self.analyses.find(
            {"user_id": user_id, "analyzed_at": {"$gte": cutoff}, "species": {"$ne": "aucun_animal"}},
            {"_id": 0}
        ).sort("analyzed_at", 1).to_list(length=1000)

        if len(analyses) < 2:
            return []

        # Group by species, find sequential camera transitions
        by_species = {}
        for a in analyses:
            sp = a.get("species", "inconnu")
            if sp not in by_species:
                by_species[sp] = []
            by_species[sp].append(a)

        trajectories = []
        for species, events in by_species.items():
            for i in range(len(events) - 1):
                e1, e2 = events[i], events[i + 1]
                if e1["camera_id"] == e2["camera_id"]:
                    continue
                if not (e1.get("gps_lat") and e2.get("gps_lat")):
                    continue

                # Calculate distance and direction
                import math
                dlat = e2["gps_lat"] - e1["gps_lat"]
                dlon = e2["gps_lon"] - e1["gps_lon"]
                dist_m = math.sqrt(dlat ** 2 + dlon ** 2) * 111000
                direction_deg = math.degrees(math.atan2(dlon, dlat)) % 360
                cardinals = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
                cardinal = cardinals[round(direction_deg / 45) % 8]

                traj = {
                    "id": f"traj_{str(uuid.uuid4())[:8]}",
                    "user_id": user_id,
                    "species": species,
                    "segments": [{
                        "from_camera_id": e1["camera_id"],
                        "to_camera_id": e2["camera_id"],
                        "from_lat": e1["gps_lat"],
                        "from_lon": e1["gps_lon"],
                        "to_lat": e2["gps_lat"],
                        "to_lon": e2["gps_lon"],
                        "timestamp_from": e1["analyzed_at"],
                        "timestamp_to": e2["analyzed_at"],
                        "direction_deg": round(direction_deg),
                        "direction_cardinal": cardinal,
                        "distance_m": round(dist_m)
                    }],
                    "confidence": min(e1.get("confidence", 0.5), e2.get("confidence", 0.5)),
                    "total_distance_m": round(dist_m),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                trajectories.append(traj)

        # Store
        if trajectories:
            await self.trajectories.delete_many({"user_id": user_id})
            await self.trajectories.insert_many(trajectories)
            for t in trajectories:
                t.pop("_id", None)

        return trajectories

    async def get_trajectories(self, user_id: str) -> list:
        cursor = self.trajectories.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1)
        return await cursor.to_list(length=200)

    def _compute_peak_hours(self, analyses: list) -> list:
        hours = {}
        for a in analyses:
            ts = a.get("analyzed_at", "")
            if "T" in ts:
                try:
                    h = int(ts.split("T")[1][:2])
                    hours[h] = hours.get(h, 0) + 1
                except (ValueError, IndexError):
                    pass
        if not hours:
            return ["05:00-07:00", "17:00-19:00"]
        sorted_h = sorted(hours.items(), key=lambda x: x[1], reverse=True)
        peaks = []
        for h, _ in sorted_h[:2]:
            peaks.append(f"{h:02d}:00-{(h + 2) % 24:02d}:00")
        return peaks

    # ============================================
    # H1-H6: COMMERCIAL VALUE SERVICES
    # ============================================

    async def compute_territory_scores(self, user_id: str) -> list:
        """H2: Generate territory scores from vision analyses and hotspots."""
        analyses = await self.get_analyses(user_id, limit=1000)
        hotspots = await self.get_hotspots(user_id)
        trajectories = await self.get_trajectories(user_id)

        if not analyses and not hotspots:
            return []

        # Group analyses by camera location grid (0.02 degree ~ 2km)
        territories = {}
        for a in analyses:
            lat, lon = a.get("gps_lat"), a.get("gps_lon")
            if not lat or not lon or a.get("species") == "aucun_animal":
                continue
            key = f"{round(lat, 2)}_{round(lon, 2)}"
            if key not in territories:
                territories[key] = {
                    "lat": lat, "lon": lon, "analyses": [],
                    "alpha_count": 0, "species": set(), "total_score": 0
                }
            territories[key]["analyses"].append(a)
            territories[key]["species"].add(a.get("species", ""))
            territories[key]["total_score"] += a.get("alpha_score", 0)
            if a.get("alpha_score", 0) >= 85:
                territories[key]["alpha_count"] += 1

        results = []
        for key, t in territories.items():
            n = len(t["analyses"])
            avg_score = t["total_score"] / n if n > 0 else 0
            alpha_ratio = t["alpha_count"] / n if n > 0 else 0
            species_diversity = len(t["species"])

            # H2: Territory ALPHA score
            territory_score = min(99, round(
                avg_score * 0.4 +
                alpha_ratio * 100 * 0.25 +
                min(n, 20) * 2 * 0.2 +
                species_diversity * 8 * 0.15
            ))

            # H3: Quality tier
            if territory_score >= 85:
                quality_tier = "ALPHA"
            elif territory_score >= 70:
                quality_tier = "Or"
            elif territory_score >= 50:
                quality_tier = "Argent"
            else:
                quality_tier = "Bronze"

            # H3: Frequency index (based on recent activity)
            recent = sum(1 for a in t["analyses"] if a.get("activity_level") == "high")
            freq_index = min(100, round(recent / max(n, 1) * 100))

            # H3: Dominance index
            dominant_scores = [a["alpha_score"] for a in t["analyses"] if a.get("alpha_score", 0) >= 65]
            dominance_index = round(sum(dominant_scores) / len(dominant_scores)) if dominant_scores else 0

            # Trajectory count for this territory
            traj_count = sum(1 for tr in trajectories if any(
                abs(seg.get("from_lat", 0) - t["lat"]) < 0.02
                for seg in tr.get("segments", [])
            ))

            results.append({
                "id": f"terr_{key}",
                "user_id": user_id,
                "gps_lat": t["lat"],
                "gps_lon": t["lon"],
                "location": {"type": "Point", "coordinates": [t["lon"], t["lat"]]},
                "territory_score": territory_score,
                "quality_tier": quality_tier,
                "frequency_index": freq_index,
                "dominance_index": dominance_index,
                "alpha_count": t["alpha_count"],
                "total_sightings": n,
                "species": list(t["species"]),
                "species_diversity": species_diversity,
                "trajectory_count": traj_count,
                "avg_alpha_score": round(avg_score),
                "peak_hours": self._compute_peak_hours(t["analyses"]),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        results.sort(key=lambda r: r["territory_score"], reverse=True)
        return results

    async def detect_anomalies(self, user_id: str) -> list:
        """H6: Detect anomalies in territory activity."""
        analyses = await self.get_analyses(user_id, limit=500)
        anomalies = []

        if len(analyses) < 5:
            return anomalies

        # Group by camera
        by_cam = {}
        for a in analyses:
            cid = a.get("camera_id", "")
            if cid not in by_cam:
                by_cam[cid] = []
            by_cam[cid].append(a)

        for cid, cam_analyses in by_cam.items():
            if len(cam_analyses) < 3:
                continue
            scores = [a.get("alpha_score", 0) for a in cam_analyses]

            # Check for activity drop (last 3 vs rest)
            if len(scores) >= 6:
                recent_avg = sum(scores[-3:]) / 3
                older_avg = sum(scores[:-3]) / len(scores[:-3])
                if older_avg > 0 and recent_avg < older_avg * 0.5:
                    anomalies.append({
                        "type": "activity_drop",
                        "camera_id": cid,
                        "severity": "high",
                        "detail": f"Baisse activite: {round(older_avg)} -> {round(recent_avg)}",
                        "detected_at": datetime.now(timezone.utc).isoformat()
                    })

            # Check for ALPHA disappearance
            alphas = [a for a in cam_analyses if a.get("alpha_score", 0) >= 85]
            if len(alphas) >= 2:
                last_alpha = max(a.get("analyzed_at", "") for a in alphas)
                last_any = max(a.get("analyzed_at", "") for a in cam_analyses)
                if last_alpha < last_any:
                    anomalies.append({
                        "type": "alpha_disappearance",
                        "camera_id": cid,
                        "severity": "medium",
                        "detail": f"ALPHA non revu depuis {last_alpha[:10]}",
                        "detected_at": datetime.now(timezone.utc).isoformat()
                    })

        return anomalies

    async def generate_commercial_report(self, user_id: str) -> dict:
        """H4: Generate commercial report for territories."""
        scores = await self.compute_territory_scores(user_id)
        anomalies = await self.detect_anomalies(user_id)
        analyses = await self.get_analyses(user_id, limit=100)
        hotspots = await self.get_hotspots(user_id)

        alpha_analyses = [a for a in analyses if a.get("alpha_score", 0) >= 85]
        species_counts = {}
        for a in analyses:
            sp = a.get("species", "inconnu")
            if sp != "aucun_animal":
                species_counts[sp] = species_counts.get(sp, 0) + 1

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "summary": {
                "total_territories": len(scores),
                "alpha_territories": sum(1 for s in scores if s["quality_tier"] == "ALPHA"),
                "gold_territories": sum(1 for s in scores if s["quality_tier"] == "Or"),
                "total_analyses": len(analyses),
                "total_alphas": len(alpha_analyses),
                "total_hotspots": len(hotspots),
                "species_detected": species_counts,
                "anomalies_count": len(anomalies)
            },
            "territories": scores[:20],
            "anomalies": anomalies,
            "top_alphas": sorted(alpha_analyses, key=lambda a: a.get("alpha_score", 0), reverse=True)[:10]
        }


    # ============================================
    # VIS-B: INDIVIDUAL CLUSTERING
    # ============================================

    async def cluster_individuals(self, user_id: str) -> list:
        """VIS-B: Cluster analyses into pseudo-individuals by species+camera proximity+time."""
        analyses = await self.get_analyses(user_id, limit=1000)
        if not analyses:
            return []

        # Group by species + camera
        groups = {}
        for a in analyses:
            sp = a.get("species", "inconnu")
            if sp == "aucun_animal":
                continue
            cam = a.get("camera_id", "")
            key = f"{sp}_{cam}"
            if key not in groups:
                groups[key] = []
            groups[key].append(a)

        individuals = []
        for key, group in groups.items():
            sp = group[0].get("species", "inconnu")
            scores = [a.get("alpha_score", 0) for a in group]
            cameras_seen = list(set(a.get("camera_id", "") for a in group))
            lats = [a["gps_lat"] for a in group if a.get("gps_lat")]
            lons = [a["gps_lon"] for a in group if a.get("gps_lon")]

            ind = {
                "id": f"ind_{str(uuid.uuid4())[:8]}",
                "user_id": user_id,
                "species": sp,
                "sex": group[0].get("sex", "indetermine"),
                "estimated_age": "adult" if max(scores) >= 60 else "juvenile",
                "alpha_score_avg": round(sum(scores) / len(scores)),
                "alpha_score_max": max(scores),
                "sightings_count": len(group),
                "first_seen": min(a.get("analyzed_at", "") for a in group),
                "last_seen": max(a.get("analyzed_at", "") for a in group),
                "cameras_seen": cameras_seen,
                "photo_ids": [a.get("photo_id", "") for a in group][:20],
                "analysis_ids": [a.get("id", "") for a in group][:20],
                "is_alpha": max(scores) >= 85,
                "is_recurring": len(group) >= 3,
                "territory_center": {
                    "type": "Point",
                    "coordinates": [sum(lons) / len(lons), sum(lats) / len(lats)]
                } if lats and lons else None,
                "territory_radius_m": 2000 if len(cameras_seen) > 1 else 800,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            individuals.append(ind)

        # Store
        if individuals:
            await self.individuals.delete_many({"user_id": user_id})
            await self.individuals.insert_many(individuals)
            for ind in individuals:
                ind.pop("_id", None)

        return sorted(individuals, key=lambda i: i["alpha_score_avg"], reverse=True)

    async def get_individuals(self, user_id: str, species: Optional[str] = None, alpha_only: bool = False) -> list:
        query = {"user_id": user_id}
        if species:
            query["species"] = species
        if alpha_only:
            query["is_alpha"] = True
        cursor = self.individuals.find(query, {"_id": 0}).sort("alpha_score_avg", -1)
        return await cursor.to_list(length=200)

    # ============================================
    # VIS-E: NOTIFICATIONS IA
    # ============================================

    async def generate_notifications(self, user_id: str) -> list:
        """Generate IA notifications based on analyses, hotspots, trajectories."""
        notifications = []
        analyses = await self.get_analyses(user_id, limit=50)
        hotspots = await self.get_hotspots(user_id)
        trajectories = await self.get_trajectories(user_id)
        anomalies = await self.detect_anomalies(user_id)

        # 1. Alpha detected
        for a in analyses:
            if a.get("alpha_score", 0) >= 85:
                notifications.append({
                    "id": f"notif_{str(uuid.uuid4())[:8]}",
                    "type": "alpha_detected",
                    "priority": "high",
                    "title": f"ALPHA detecte: {a.get('species', 'inconnu')}",
                    "detail": f"Score {a['alpha_score']} — Camera {a.get('camera_id', '')[:8]}",
                    "gps_lat": a.get("gps_lat"),
                    "gps_lon": a.get("gps_lon"),
                    "timestamp": a.get("analyzed_at"),
                    "read": False
                })

        # 2. Active corridors (trajectories)
        if trajectories:
            notifications.append({
                "id": f"notif_{str(uuid.uuid4())[:8]}",
                "type": "corridor_active",
                "priority": "medium",
                "title": f"{len(trajectories)} trajectoire(s) active(s)",
                "detail": "Corridors detectes entre vos cameras",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "read": False
            })

        # 3. Activity spike (hotspots with high activity)
        for hs in hotspots:
            if hs.get("activity_level") == "extreme":
                notifications.append({
                    "id": f"notif_{str(uuid.uuid4())[:8]}",
                    "type": "activity_spike",
                    "priority": "high",
                    "title": f"Activite extreme: {hs.get('dominant_species', 'multi-especes')}",
                    "detail": f"{hs.get('total_sightings', 0)} observations",
                    "gps_lat": hs.get("gps_lat"),
                    "gps_lon": hs.get("gps_lon"),
                    "timestamp": hs.get("last_activity"),
                    "read": False
                })

        # 4. Anomalies
        for anom in anomalies:
            notifications.append({
                "id": f"notif_{str(uuid.uuid4())[:8]}",
                "type": f"anomaly_{anom['type']}",
                "priority": anom.get("severity", "medium"),
                "title": anom.get("detail", "Anomalie detectee"),
                "detail": f"Camera {anom.get('camera_id', '')[:8]}",
                "timestamp": anom.get("detected_at"),
                "read": False
            })

        return sorted(notifications, key=lambda n: n.get("timestamp", ""), reverse=True)[:50]

    # ============================================
    # SECTION 3: ADVANCED ANOMALIES
    # ============================================

    async def detect_advanced_anomalies(self, user_id: str) -> list:
        """Section 3: Extended anomaly detection including camera security."""
        base_anomalies = await self.detect_anomalies(user_id)

        # Camera offline detection
        cameras = await self.db["cameras"].find(
            {"user_id": user_id}, {"_id": 0}
        ).to_list(length=100)

        for cam in cameras:
            if cam.get("status") == "offline":
                base_anomalies.append({
                    "type": "camera_offline",
                    "camera_id": cam.get("id", ""),
                    "severity": "medium",
                    "detail": f"Camera {cam.get('name', '')} hors-ligne",
                    "detected_at": datetime.now(timezone.utc).isoformat()
                })

        # Behavioral change: species diversity drop
        analyses = await self.get_analyses(user_id, limit=200)
        if len(analyses) >= 10:
            recent = analyses[:10]
            older = analyses[10:]
            recent_species = set(a.get("species") for a in recent if a.get("species") != "aucun_animal")
            older_species = set(a.get("species") for a in older if a.get("species") != "aucun_animal")
            disappeared = older_species - recent_species
            for sp in disappeared:
                base_anomalies.append({
                    "type": "species_disappearance",
                    "camera_id": "",
                    "severity": "low",
                    "detail": f"Espece '{sp}' non detectee recemment",
                    "detected_at": datetime.now(timezone.utc).isoformat()
                })

        return base_anomalies