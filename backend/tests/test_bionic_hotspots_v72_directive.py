"""
BIONIC V7.2 Hotspot Directive x7200 — Test Suite
=================================================
Tests for the V7.2 hotspot extraction engine with:
- Water exclusion (embedded database)
- Ecological constraints (species/latitude)
- Terrain-aware scoring
- 1.5km minimum dispersion
- BIONIC gradient colors

Conformite: BCE-4X GOLDEN | STEEVE-MAX x7200
"""

import pytest
import requests
import os
import math

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
HOTSPOT_API = f"{BASE_URL}/api/v1/admin/bionic-hotspots"

# Known water body coordinates from water_bodies_qc.py
LAC_SAINT_JEAN = (48.57, -72.06, 18000)  # lat, lng, radius_m
LAC_TEMISCOUATA = (47.67, -68.75, 5000)

# Latitude constraint for dindon_sauvage
DINDON_MAX_LATITUDE = 46.8

# Minimum inter-hotspot distance
MIN_DISPERSION_M = 1500


def haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate Haversine distance in meters between two GPS points."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def is_point_on_water(lat: float, lng: float, water_body: tuple) -> bool:
    """Check if a point is within a water body radius."""
    w_lat, w_lng, radius_m = water_body
    dist = haversine_distance_m(lat, lng, w_lat, w_lng)
    return dist <= radius_m


class TestHotspotExtractionV72:
    """Test hotspot extraction API with V7.2 features."""
    
    @pytest.fixture(scope="class")
    def extraction_result(self):
        """Run extraction once for all tests in this class."""
        response = requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        assert response.status_code == 200, f"Extraction failed: {response.text}"
        return response.json()
    
    def test_extraction_returns_success(self, extraction_result):
        """POST /api/v1/admin/bionic-hotspots/extract returns success."""
        assert extraction_result.get("success") is True
        print(f"✓ Extraction successful: {extraction_result.get('total_hotspots')} hotspots")
    
    def test_extraction_returns_hotspots(self, extraction_result):
        """Extraction returns hotspots (target: ~300 across 12 regions)."""
        total = extraction_result.get("total_hotspots", 0)
        assert total > 0, "No hotspots extracted"
        # Each region should have up to 25 hotspots, 12 regions = max 300
        assert total <= 300, f"Too many hotspots: {total} (max 300)"
        print(f"✓ Total hotspots: {total}")
    
    def test_extraction_covers_all_regions(self, extraction_result):
        """Extraction covers all 12 BIONIC regions."""
        regions_summary = extraction_result.get("regions_summary", [])
        assert len(regions_summary) == 12, f"Expected 12 regions, got {len(regions_summary)}"
        
        expected_regions = [
            "laurentides", "outaouais", "lanaudiere", "mauricie", "estrie",
            "saguenay", "capitale_nationale", "chaudiere_appalaches",
            "bas_saint_laurent", "abitibi", "cote_nord", "gaspesie"
        ]
        extracted_regions = [r["region_id"] for r in regions_summary]
        for region in expected_regions:
            assert region in extracted_regions, f"Missing region: {region}"
        print(f"✓ All 12 regions covered")


class TestHotspotListV72:
    """Test hotspot list API with V7.2 enriched fields."""
    
    @pytest.fixture(scope="class")
    def hotspots_list(self):
        """Fetch hotspots list (requires prior extraction)."""
        # First ensure extraction is done
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        
        response = requests.get(f"{HOTSPOT_API}/list?limit=300", timeout=30)
        assert response.status_code == 200, f"List failed: {response.text}"
        return response.json()
    
    def test_list_returns_hotspots(self, hotspots_list):
        """GET /api/v1/admin/bionic-hotspots/list returns hotspots."""
        hotspots = hotspots_list.get("hotspots", [])
        assert len(hotspots) > 0, "No hotspots in list"
        print(f"✓ List returned {len(hotspots)} hotspots")
    
    def test_hotspots_have_v72_metadata(self, hotspots_list):
        """Each hotspot has V7.2 metadata fields."""
        hotspots = hotspots_list.get("hotspots", [])
        assert len(hotspots) > 0, "No hotspots to test"
        
        v72_fields = [
            "habitat_type", "water_proximity", "ecological_coherence",
            "intensity", "terrain_factors"
        ]
        
        for h in hotspots[:10]:  # Check first 10
            for field in v72_fields:
                assert field in h, f"Missing V7.2 field '{field}' in hotspot {h.get('id')}"
        
        print(f"✓ V7.2 metadata fields present: {v72_fields}")
    
    def test_hotspots_have_intensity_values(self, hotspots_list):
        """Hotspots have valid intensity values (EXTREME/INTENSE/MODERE/FAIBLE)."""
        hotspots = hotspots_list.get("hotspots", [])
        valid_intensities = ["EXTREME", "INTENSE", "MODERE", "FAIBLE"]
        
        for h in hotspots:
            intensity = h.get("intensity")
            assert intensity in valid_intensities, f"Invalid intensity '{intensity}' for {h.get('id')}"
        
        print(f"✓ All hotspots have valid intensity values")
    
    def test_hotspots_have_habitat_type(self, hotspots_list):
        """Hotspots have valid habitat_type values."""
        hotspots = hotspots_list.get("hotspots", [])
        valid_habitats = ["taiga", "boreal", "mixte", "feuillu", "agricole"]
        
        for h in hotspots:
            habitat = h.get("habitat_type")
            assert habitat in valid_habitats, f"Invalid habitat '{habitat}' for {h.get('id')}"
        
        print(f"✓ All hotspots have valid habitat_type values")
    
    def test_water_proximity_in_range(self, hotspots_list):
        """Water proximity values are in [0.0, 1.0] range."""
        hotspots = hotspots_list.get("hotspots", [])
        
        for h in hotspots:
            wp = h.get("water_proximity")
            assert wp is not None, f"Missing water_proximity for {h.get('id')}"
            assert 0.0 <= wp <= 1.0, f"Invalid water_proximity {wp} for {h.get('id')}"
        
        print(f"✓ All water_proximity values in [0.0, 1.0]")


class TestWaterExclusionV72:
    """Test that no hotspot centers are on water bodies."""
    
    @pytest.fixture(scope="class")
    def hotspots_list(self):
        """Fetch hotspots list."""
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        response = requests.get(f"{HOTSPOT_API}/list?limit=300", timeout=30)
        assert response.status_code == 200
        return response.json()
    
    def test_no_hotspot_on_lac_saint_jean(self, hotspots_list):
        """No hotspot center should be on Lac Saint-Jean (48.57, -72.06)."""
        hotspots = hotspots_list.get("hotspots", [])
        
        for h in hotspots:
            center = h.get("center", [])
            if len(center) >= 2:
                lat, lng = center[0], center[1]
                on_water = is_point_on_water(lat, lng, LAC_SAINT_JEAN)
                assert not on_water, f"Hotspot {h.get('id')} is on Lac Saint-Jean at ({lat}, {lng})"
        
        print(f"✓ No hotspots on Lac Saint-Jean")
    
    def test_no_hotspot_on_lac_temiscouata(self, hotspots_list):
        """No hotspot center should be on Lac Temiscouata (47.67, -68.75)."""
        hotspots = hotspots_list.get("hotspots", [])
        
        for h in hotspots:
            center = h.get("center", [])
            if len(center) >= 2:
                lat, lng = center[0], center[1]
                on_water = is_point_on_water(lat, lng, LAC_TEMISCOUATA)
                assert not on_water, f"Hotspot {h.get('id')} is on Lac Temiscouata at ({lat}, {lng})"
        
        print(f"✓ No hotspots on Lac Temiscouata")
    
    def test_water_proximity_not_zero_for_all(self, hotspots_list):
        """Hotspots should have water_proximity > 0 (not directly on water)."""
        hotspots = hotspots_list.get("hotspots", [])
        
        for h in hotspots:
            wp = h.get("water_proximity", 0)
            # water_proximity = 0.0 means directly on water
            assert wp > 0, f"Hotspot {h.get('id')} has water_proximity=0 (on water)"
        
        print(f"✓ All hotspots have water_proximity > 0")


class TestEcologicalConstraintsV72:
    """Test ecological constraints (species/latitude)."""
    
    @pytest.fixture(scope="class")
    def hotspots_list(self):
        """Fetch hotspots list."""
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        response = requests.get(f"{HOTSPOT_API}/list?limit=300", timeout=30)
        assert response.status_code == 200
        return response.json()
    
    def test_no_dindon_sauvage_above_46_8N(self, hotspots_list):
        """No dindon_sauvage species should appear at latitude > 46.8N."""
        hotspots = hotspots_list.get("hotspots", [])
        
        violations = []
        for h in hotspots:
            species = h.get("dominant_species")
            center = h.get("center", [])
            if species == "dindon_sauvage" and len(center) >= 2:
                lat = center[0]
                if lat > DINDON_MAX_LATITUDE:
                    violations.append({
                        "id": h.get("id"),
                        "lat": lat,
                        "region": h.get("region_name")
                    })
        
        assert len(violations) == 0, f"Found {len(violations)} dindon_sauvage above 46.8N: {violations}"
        print(f"✓ No dindon_sauvage above latitude 46.8N")
    
    def test_ecological_coherence_present(self, hotspots_list):
        """All hotspots have ecological_coherence object."""
        hotspots = hotspots_list.get("hotspots", [])
        
        for h in hotspots:
            eco = h.get("ecological_coherence")
            assert eco is not None, f"Missing ecological_coherence for {h.get('id')}"
            assert "latitude_valid" in eco, f"Missing latitude_valid in ecological_coherence"
            assert "habitat_match" in eco, f"Missing habitat_match in ecological_coherence"
            assert "coherence_score" in eco, f"Missing coherence_score in ecological_coherence"
        
        print(f"✓ All hotspots have ecological_coherence object")
    
    def test_saguenay_bas_saint_laurent_cote_nord_no_dindon(self, hotspots_list):
        """Saguenay, Bas-Saint-Laurent, Cote-Nord regions should have no dindon_sauvage."""
        hotspots = hotspots_list.get("hotspots", [])
        northern_regions = ["saguenay", "bas_saint_laurent", "cote_nord"]
        
        violations = []
        for h in hotspots:
            region_id = h.get("region_id")
            species = h.get("dominant_species")
            if region_id in northern_regions and species == "dindon_sauvage":
                violations.append({
                    "id": h.get("id"),
                    "region": region_id,
                    "lat": h.get("center", [None])[0]
                })
        
        assert len(violations) == 0, f"Found dindon_sauvage in northern regions: {violations}"
        print(f"✓ No dindon_sauvage in Saguenay/Bas-Saint-Laurent/Cote-Nord")


class TestDispersionV72:
    """Test 1.5km minimum dispersion between hotspots."""
    
    @pytest.fixture(scope="class")
    def hotspots_by_region(self):
        """Fetch hotspots grouped by region."""
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        response = requests.get(f"{HOTSPOT_API}/list?limit=300", timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Group by region
        by_region = {}
        for h in data.get("hotspots", []):
            region = h.get("region_id")
            if region not in by_region:
                by_region[region] = []
            by_region[region].append(h)
        
        return by_region
    
    def test_hotspots_dispersion_1500m(self, hotspots_by_region):
        """All hotspot pairs within the same region should be >= 1500m apart."""
        violations = []
        
        for region_id, hotspots in hotspots_by_region.items():
            for i, h1 in enumerate(hotspots):
                for h2 in hotspots[i+1:]:
                    c1 = h1.get("center", [])
                    c2 = h2.get("center", [])
                    if len(c1) >= 2 and len(c2) >= 2:
                        dist = haversine_distance_m(c1[0], c1[1], c2[0], c2[1])
                        if dist < MIN_DISPERSION_M:
                            violations.append({
                                "region": region_id,
                                "h1": h1.get("id"),
                                "h2": h2.get("id"),
                                "distance_m": round(dist, 1)
                            })
        
        assert len(violations) == 0, f"Found {len(violations)} pairs < 1500m apart: {violations[:5]}"
        print(f"✓ All hotspot pairs >= 1500m apart")


class TestBCE4XReportV72:
    """Test BCE-4X compliance report."""
    
    @pytest.fixture(scope="class")
    def bce_report(self):
        """Fetch BCE-4X report (requires prior extraction)."""
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        response = requests.get(f"{HOTSPOT_API}/report/bce4x", timeout=30)
        assert response.status_code == 200, f"BCE report failed: {response.text}"
        return response.json()
    
    def test_bce_report_returns_pass(self, bce_report):
        """GET /api/v1/admin/bionic-hotspots/report/bce4x returns PASS status."""
        overall = bce_report.get("overall")
        assert overall == "PASS", f"BCE-4X report failed: {overall}"
        print(f"✓ BCE-4X report: PASS")
    
    def test_bce_report_has_checks(self, bce_report):
        """BCE report includes validation checks."""
        total_checks = bce_report.get("total_checks", 0)
        passed = bce_report.get("passed", 0)
        failed = bce_report.get("failed", 0)
        
        assert total_checks > 0, "No checks in BCE report"
        assert passed > 0, "No passed checks"
        assert failed == 0, f"BCE report has {failed} failed checks"
        
        print(f"✓ BCE-4X checks: {passed}/{total_checks} passed")
    
    def test_bce_report_includes_water_exclusion(self, bce_report):
        """BCE report confirms water exclusion is active."""
        water_active = bce_report.get("water_exclusion_active")
        assert water_active is True, "Water exclusion not active in BCE report"
        print(f"✓ Water exclusion active in BCE report")
    
    def test_bce_report_includes_v72_rules(self, bce_report):
        """BCE report includes V7.2 rules (WATER-001, ECO-001)."""
        checks = bce_report.get("checks", [])
        rules = [c.get("rule") for c in checks]
        
        # V7.2 added WATER-001 and ECO-001 rules
        assert "WATER-001" in rules, "Missing WATER-001 rule in BCE report"
        assert "ECO-001" in rules, "Missing ECO-001 rule in BCE report"
        
        print(f"✓ V7.2 rules (WATER-001, ECO-001) present in BCE report")


class TestTerrainFactorsV72:
    """Test terrain_factors object in hotspots."""
    
    @pytest.fixture(scope="class")
    def hotspots_list(self):
        """Fetch hotspots list."""
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        response = requests.get(f"{HOTSPOT_API}/list?limit=300", timeout=30)
        assert response.status_code == 200
        return response.json()
    
    def test_terrain_factors_present(self, hotspots_list):
        """All hotspots have terrain_factors object."""
        hotspots = hotspots_list.get("hotspots", [])
        
        for h in hotspots:
            tf = h.get("terrain_factors")
            assert tf is not None, f"Missing terrain_factors for {h.get('id')}"
            assert "water_exclusion" in tf, "Missing water_exclusion in terrain_factors"
            assert "urban_exclusion" in tf, "Missing urban_exclusion in terrain_factors"
            assert "habitat_match" in tf, "Missing habitat_match in terrain_factors"
            assert "latitude_valid" in tf, "Missing latitude_valid in terrain_factors"
        
        print(f"✓ All hotspots have terrain_factors object")
    
    def test_water_exclusion_true_for_all(self, hotspots_list):
        """All hotspots should have water_exclusion=True (not on water)."""
        hotspots = hotspots_list.get("hotspots", [])
        
        for h in hotspots:
            tf = h.get("terrain_factors", {})
            water_ok = tf.get("water_exclusion")
            assert water_ok is True, f"Hotspot {h.get('id')} has water_exclusion=False"
        
        print(f"✓ All hotspots have water_exclusion=True")


class TestAPIEndpoints:
    """Test API endpoint availability and basic responses."""
    
    def test_regions_endpoint(self):
        """GET /api/v1/admin/bionic-hotspots/regions returns regions."""
        response = requests.get(f"{HOTSPOT_API}/regions", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("total") == 12
        print(f"✓ Regions endpoint: 12 regions")
    
    def test_stats_endpoint(self):
        """GET /api/v1/admin/bionic-hotspots/stats returns statistics."""
        # Ensure extraction first
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        
        response = requests.get(f"{HOTSPOT_API}/stats", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "total_hotspots" in data or "error" not in data
        print(f"✓ Stats endpoint working")
    
    def test_export_geojson_endpoint(self):
        """GET /api/v1/admin/bionic-hotspots/export/geojson returns GeoJSON."""
        requests.post(f"{HOTSPOT_API}/extract", timeout=180)
        
        response = requests.get(f"{HOTSPOT_API}/export/geojson", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("type") == "FeatureCollection"
        print(f"✓ GeoJSON export endpoint working")
    
    def test_scheduler_status_endpoint(self):
        """GET /api/v1/admin/bionic-hotspots/scheduler/status returns status."""
        response = requests.get(f"{HOTSPOT_API}/scheduler/status", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        print(f"✓ Scheduler status endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
