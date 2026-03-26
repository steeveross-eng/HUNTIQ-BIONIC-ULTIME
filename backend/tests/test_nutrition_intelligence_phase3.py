"""
Test Suite: HUNTIQ-V6 Nutrition Intelligence Phase 3
Tests for x6010-x6012, x6020, x6030, x7000 engines
BCE-4X / STEEVE-MAX V6

Modules tested:
- x6010: Product Quality Analyzer (12 criteria)
- x6011: Market Availability Engine (Canada/USA)
- x6012: Regulatory Compliance Engine (MAPAQ/ACIA/FDA/USDA/EPA)
- x6020: Terrain Solutions Engine
- x6030: Product Ecosystem Connector
- x7000: Supplier Product Pipeline
- SUPRA Panel enrichment with quality/availability/compliance/terrain_solutions
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
API_PREFIX = f"{BASE_URL}/api/v6/nutrition-intelligence"

# Product IDs for testing
PRODUCT_IDS = [
    "trophy_rock_four65", "pro_cal_lick", "biomineral_p_plus",
    "whitetail_k_source", "evolved_mag_mix", "purina_antlermax_zn",
    "ridley_se_vit", "sportsmans_fe_block", "bear_mineral_attract",
    "purina_antlermax_20"
]


class TestX6010ProductQualityAnalyzer:
    """x6010 — Product Quality Analyzer (12 criteria)"""

    def test_product_quality_single(self):
        """POST /products/quality — returns quality score, grade, 12 criteria"""
        response = requests.post(
            f"{API_PREFIX}/products/quality",
            json={"product_id": "trophy_rock_four65"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "product_id" in data
        assert data["product_id"] == "trophy_rock_four65"
        assert "score_qualite" in data
        assert "grade" in data
        assert "criteria" in data
        assert "cost_per_week_cad" in data
        assert "efficiency_ratio" in data
        assert "top_strengths" in data
        assert "weaknesses" in data
        
        # Verify 12 criteria
        assert len(data["criteria"]) == 12
        
        # Verify criteria structure
        for criterion in data["criteria"]:
            assert "key" in criterion
            assert "label" in criterion
            assert "score" in criterion
            assert "weight" in criterion
            assert "zone" in criterion
            assert criterion["zone"] in ["vert", "jaune", "rouge"]
        
        # Verify grade is valid
        assert data["grade"] in ["EXCELLENT", "BON", "MODERE", "INSUFFISANT"]
        
        # Verify score is in valid range
        assert 0 <= data["score_qualite"] <= 100

    def test_product_quality_all(self):
        """GET /products/quality/all — returns all products with average"""
        response = requests.get(f"{API_PREFIX}/products/quality/all")
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert "total" in data
        assert "average_quality" in data
        assert data["total"] == 10  # 10 products in catalog
        assert len(data["products"]) == 10
        
        # Verify products are sorted by score (descending)
        scores = [p["score_qualite"] for p in data["products"]]
        assert scores == sorted(scores, reverse=True)

    def test_product_quality_unknown_product(self):
        """POST /products/quality — unknown product returns error"""
        response = requests.post(
            f"{API_PREFIX}/products/quality",
            json={"product_id": "unknown_product_xyz"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data


class TestX6011MarketAvailabilityEngine:
    """x6011 — Market Availability Engine (Canada/USA)"""

    def test_product_availability_single(self):
        """POST /products/availability — returns Canada/USA availability"""
        response = requests.post(
            f"{API_PREFIX}/products/availability",
            json={"product_id": "trophy_rock_four65", "province": "QC"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "product_id" in data
        assert data["product_id"] == "trophy_rock_four65"
        assert "canada" in data
        assert "usa" in data
        assert "availability_score" in data
        assert "province_detail" in data
        
        # Verify Canada structure
        assert "available" in data["canada"]
        assert "provinces" in data["canada"]
        
        # Verify USA structure
        assert "available" in data["usa"]
        assert "states_restricted" in data["usa"]
        
        # Verify province detail
        assert data["province_detail"]["province"] == "QC"
        assert "status" in data["province_detail"]
        assert "distributeurs" in data["province_detail"]
        
        # Verify availability score
        assert "canada_score" in data["availability_score"]
        assert "usa_available" in data["availability_score"]

    def test_product_availability_all(self):
        """GET /products/availability/all — returns all products"""
        response = requests.get(f"{API_PREFIX}/products/availability/all")
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert "total" in data
        assert data["total"] == 10

    def test_product_availability_all_with_province_filter(self):
        """GET /products/availability/all?province=QC — filters by province"""
        response = requests.get(f"{API_PREFIX}/products/availability/all?province=QC")
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert "province_filter" in data
        assert data["province_filter"] == "QC"
        
        # Verify each product has province_detail for QC
        for product in data["products"]:
            assert "province_detail" in product
            assert product["province_detail"]["province"] == "QC"

    def test_provincial_restrictions(self):
        """GET /products/restrictions/{province} — returns provincial restrictions"""
        response = requests.get(f"{API_PREFIX}/products/restrictions/QC")
        assert response.status_code == 200
        data = response.json()
        
        assert "province" in data
        assert data["province"] == "QC"
        assert "restrictions" in data
        assert "total_restricted" in data
        
        # Verify restrictions structure
        for restriction in data["restrictions"]:
            assert "product_id" in restriction
            assert "status" in restriction
            assert "restrictions" in restriction


class TestX6012RegulatoryComplianceEngine:
    """x6012 — Regulatory Compliance Engine (MAPAQ/ACIA/FDA/USDA/EPA)"""

    def test_product_compliance_single(self):
        """POST /products/compliance — returns compliance score, certifications"""
        response = requests.post(
            f"{API_PREFIX}/products/compliance",
            json={"product_id": "purina_antlermax_zn"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "product_id" in data
        assert data["product_id"] == "purina_antlermax_zn"
        assert "score_compliance" in data
        assert "score_impact_global" in data
        assert "grade" in data
        assert "organisms" in data
        assert "certifications" in data
        assert "non_conforme" in data
        assert "attention" in data
        
        # Verify 5 organisms (MAPAQ, ACIA, FDA, USDA, EPA)
        assert len(data["organisms"]) == 5
        
        # Verify organism structure
        for org in data["organisms"]:
            assert "organisme" in org
            assert org["organisme"] in ["MAPAQ", "ACIA", "FDA", "USDA", "EPA"]
            assert "status" in org
            assert "category" in org
            assert "score" in org
            assert "weight" in org
        
        # Verify grade is valid
        assert data["grade"] in ["CONFORME", "ACCEPTABLE", "ATTENTION", "NON_CONFORME"]

    def test_product_compliance_all(self):
        """GET /products/compliance/all — returns all products"""
        response = requests.get(f"{API_PREFIX}/products/compliance/all")
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert "total" in data
        assert "average_compliance" in data
        assert data["total"] == 10

    def test_compliance_by_organism_mapaq(self):
        """GET /products/compliance/mapaq — filters by MAPAQ"""
        response = requests.get(f"{API_PREFIX}/products/compliance/mapaq")
        assert response.status_code == 200
        data = response.json()
        
        assert "organism" in data
        assert data["organism"] == "MAPAQ"
        assert "products" in data
        assert "total_conforme" in data
        assert "total_partiel" in data
        assert "total_non_conforme" in data

    def test_compliance_by_organism_acia(self):
        """GET /products/compliance/acia — filters by ACIA"""
        response = requests.get(f"{API_PREFIX}/products/compliance/acia")
        assert response.status_code == 200
        data = response.json()
        assert data["organism"] == "ACIA"

    def test_compliance_by_organism_fda(self):
        """GET /products/compliance/fda — filters by FDA"""
        response = requests.get(f"{API_PREFIX}/products/compliance/fda")
        assert response.status_code == 200
        data = response.json()
        assert data["organism"] == "FDA"

    def test_compliance_unknown_organism(self):
        """GET /products/compliance/{unknown} — returns error"""
        response = requests.get(f"{API_PREFIX}/products/compliance/unknown_org")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "valid_organisms" in data


class TestX6020TerrainSolutionsEngine:
    """x6020 — Terrain Solutions Engine"""

    def test_terrain_solutions_catalog(self):
        """GET /terrain/solutions — returns complete catalog"""
        response = requests.get(f"{API_PREFIX}/terrain/solutions")
        assert response.status_code == 200
        data = response.json()
        
        assert "solutions" in data
        assert "total" in data
        assert data["total"] > 0
        
        # Verify solution structure
        for sol in data["solutions"]:
            assert "deficit_key" in sol
            assert "deficit_label" in sol
            assert "type" in sol
            assert "name" in sol
            assert "description" in sol
            assert "placement" in sol
            assert "efficacy_months" in sol
            assert "cost_range_cad" in sol
            assert "priority" in sol
            assert sol["priority"] in ["CRITIQUE", "RECOMMANDE", "OPTIONNEL"]

    def test_terrain_solutions_compute(self):
        """POST /terrain/solutions/compute — computes solutions for deficits"""
        response = requests.post(
            f"{API_PREFIX}/terrain/solutions/compute",
            json={
                "species": "chevreuil",
                "season": "printemps",
                "soil_type": "mixte",
                "substrate": "bois_mou"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "solutions" in data
        assert "total" in data
        assert "critiques" in data
        assert "recommandees" in data
        assert "cost_estimate_min_cad" in data
        assert "cost_estimate_max_cad" in data
        assert "categories" in data
        
        # Verify categories
        assert "blocs_mineraux" in data["categories"]
        assert "champs_nourriciers" in data["categories"]
        assert "salines" in data["categories"]
        assert "attractifs" in data["categories"]


class TestX6030ProductEcosystemConnector:
    """x6030 — Product Ecosystem Connector"""

    def test_product_ecosystem_single(self):
        """POST /products/ecosystem — returns product interconnection"""
        response = requests.post(
            f"{API_PREFIX}/products/ecosystem",
            json={"product_id": "trophy_rock_four65"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "product_id" in data
        assert data["product_id"] == "trophy_rock_four65"
        assert "magasin" in data
        assert "fournisseur" in data
        assert "certifications" in data
        assert "recettes_associees" in data
        assert "modules_lies" in data
        assert "liens_ecosysteme" in data
        assert "connections_count" in data
        
        # Verify magasin structure
        assert "disponible_en_ligne" in data["magasin"]
        assert "url_magasin" in data["magasin"]
        assert "distributeurs" in data["magasin"]
        assert "prix_magasin_cad" in data["magasin"]
        
        # Verify fournisseur structure
        assert "nom" in data["fournisseur"]
        assert "pays" in data["fournisseur"]
        assert "delai_livraison_jours" in data["fournisseur"]
        
        # Verify liens_ecosysteme
        assert "intelligence" in data["liens_ecosysteme"]
        assert "comparez" in data["liens_ecosysteme"]
        assert "commander" in data["liens_ecosysteme"]
        assert "fiche_produit" in data["liens_ecosysteme"]

    def test_product_ecosystem_all(self):
        """GET /products/ecosystem/all — returns all ecosystems"""
        response = requests.get(f"{API_PREFIX}/products/ecosystem/all")
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert "total" in data
        assert data["total"] == 10

    def test_product_tracability(self):
        """POST /products/tracability — returns product tracability"""
        response = requests.post(
            f"{API_PREFIX}/products/tracability",
            json={"product_id": "purina_antlermax_zn"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "product_id" in data
        assert "fournisseur" in data
        assert "certifications" in data
        assert "modules_lies" in data
        assert "recettes_associees" in data
        assert "magasin" in data
        assert "tracabilite_complete" in data
        assert data["tracabilite_complete"] == True


class TestX7000SupplierProductPipeline:
    """x7000 — Supplier Product Pipeline (submit -> review -> activate)"""

    def test_supplier_submit_valid(self):
        """POST /supplier/submit — submits a valid product"""
        response = requests.post(
            f"{API_PREFIX}/supplier/submit",
            json={
                "supplier_name": "Test Supplier Inc.",
                "product_name": "Test Mineral Block Premium",
                "description": "High quality mineral block for deer with calcium and phosphorus enrichment",
                "category": "bloc_mineral",
                "price_cad": 29.99,
                "weight_kg": 4.5,
                "minerals": ["calcium", "phosphore", "sodium"],
                "certifications": ["ACIA enregistre"],
                "species_target": ["chevreuil", "orignal"],
                "brand": "TestBrand"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "submission_id" in data
        assert data["submission_id"].startswith("SUB-")
        assert "status" in data
        assert "auto_validation" in data
        assert "next_step" in data
        
        # Should pass auto-validation
        assert data["status"] == "validation_auto_ok"
        assert data["auto_validation"]["passed"] == True
        
        return data["submission_id"]

    def test_supplier_submit_invalid_missing_acia(self):
        """POST /supplier/submit — rejects product without ACIA certification"""
        response = requests.post(
            f"{API_PREFIX}/supplier/submit",
            json={
                "supplier_name": "Bad Supplier",
                "product_name": "Uncertified Block",
                "description": "A mineral block without proper certification",
                "category": "bloc_mineral",
                "price_cad": 15.00,
                "weight_kg": 2.0,
                "minerals": ["sodium"],
                "certifications": [],  # Missing ACIA
                "species_target": ["chevreuil"],
                "brand": ""
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "validation_auto_rejetee"
        assert data["auto_validation"]["passed"] == False
        assert data["next_step"] == "correction_et_resoumission"

    def test_supplier_pipeline_full_flow(self):
        """Full pipeline: submit -> review -> activate"""
        # Step 1: Submit
        submit_response = requests.post(
            f"{API_PREFIX}/supplier/submit",
            json={
                "supplier_name": "Pipeline Test Supplier",
                "product_name": "Pipeline Test Block",
                "description": "Testing the full supplier pipeline flow",
                "category": "supplement_mineral",
                "price_cad": 35.00,
                "weight_kg": 5.0,
                "minerals": ["zinc", "selenium"],
                "certifications": ["ACIA conforme"],
                "species_target": ["chevreuil"],
                "brand": "PipelineTest"
            }
        )
        assert submit_response.status_code == 200
        submit_data = submit_response.json()
        submission_id = submit_data["submission_id"]
        assert submit_data["status"] == "validation_auto_ok"
        
        # Step 2: Review (approve)
        review_response = requests.post(
            f"{API_PREFIX}/supplier/review",
            json={
                "submission_id": submission_id,
                "approved": True,
                "reviewer_notes": "Product meets all quality standards"
            }
        )
        assert review_response.status_code == 200
        review_data = review_response.json()
        assert review_data["status"] == "approuve"
        assert review_data["next_step"] == "activation_magasin"
        
        # Step 3: Activate
        activate_response = requests.post(
            f"{API_PREFIX}/supplier/activate",
            json={"submission_id": submission_id}
        )
        assert activate_response.status_code == 200
        activate_data = activate_response.json()
        assert activate_data["status"] == "actif_magasin"
        assert "Produit active avec succes" in activate_data["message"]

    def test_supplier_review_reject(self):
        """POST /supplier/review — rejects a submission"""
        # First submit
        submit_response = requests.post(
            f"{API_PREFIX}/supplier/submit",
            json={
                "supplier_name": "Reject Test",
                "product_name": "Reject Test Block",
                "description": "This product will be rejected in review",
                "category": "bloc_mineral",
                "price_cad": 20.00,
                "weight_kg": 3.0,
                "minerals": ["sodium"],
                "certifications": ["ACIA enregistre"],
                "species_target": ["chevreuil"],
                "brand": ""
            }
        )
        submission_id = submit_response.json()["submission_id"]
        
        # Reject
        review_response = requests.post(
            f"{API_PREFIX}/supplier/review",
            json={
                "submission_id": submission_id,
                "approved": False,
                "reviewer_notes": "Quality does not meet standards"
            }
        )
        assert review_response.status_code == 200
        data = review_response.json()
        assert data["status"] == "rejete"
        assert data["next_step"] == "archive"

    def test_supplier_activate_not_approved(self):
        """POST /supplier/activate — fails if not approved"""
        # Submit but don't review
        submit_response = requests.post(
            f"{API_PREFIX}/supplier/submit",
            json={
                "supplier_name": "No Review Test",
                "product_name": "No Review Block",
                "description": "This product will not be reviewed before activation attempt",
                "category": "bloc_mineral",
                "price_cad": 25.00,
                "weight_kg": 4.0,
                "minerals": ["calcium"],
                "certifications": ["ACIA conforme"],
                "species_target": ["chevreuil"],
                "brand": ""
            }
        )
        submission_id = submit_response.json()["submission_id"]
        
        # Try to activate without review
        activate_response = requests.post(
            f"{API_PREFIX}/supplier/activate",
            json={"submission_id": submission_id}
        )
        assert activate_response.status_code == 200
        data = activate_response.json()
        assert "error" in data

    def test_supplier_pipeline_stats(self):
        """GET /supplier/pipeline/stats — returns pipeline statistics"""
        response = requests.get(f"{API_PREFIX}/supplier/pipeline/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_submissions" in data
        assert "by_status" in data
        assert "auto_validation_criteria" in data
        
        # Verify auto_validation_criteria
        criteria = data["auto_validation_criteria"]
        assert "nom_produit_min_length" in criteria
        assert "description_min_length" in criteria
        assert "prix_min_cad" in criteria
        assert "prix_max_cad" in criteria
        assert "categories_valides" in criteria

    def test_supplier_get_submission(self):
        """GET /supplier/submission/{id} — retrieves a submission"""
        # First submit
        submit_response = requests.post(
            f"{API_PREFIX}/supplier/submit",
            json={
                "supplier_name": "Get Test",
                "product_name": "Get Test Block",
                "description": "Testing retrieval of submission",
                "category": "bloc_mineral",
                "price_cad": 22.00,
                "weight_kg": 3.5,
                "minerals": ["magnesium"],
                "certifications": ["ACIA enregistre"],
                "species_target": ["chevreuil"],
                "brand": ""
            }
        )
        submission_id = submit_response.json()["submission_id"]
        
        # Get submission
        get_response = requests.get(f"{API_PREFIX}/supplier/submission/{submission_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        
        assert data["submission_id"] == submission_id
        assert "status" in data
        assert "supplier" in data
        assert "product" in data
        assert "auto_validation" in data
        assert "pipeline_history" in data

    def test_supplier_list_submissions(self):
        """GET /supplier/submissions — lists all submissions"""
        response = requests.get(f"{API_PREFIX}/supplier/submissions")
        assert response.status_code == 200
        data = response.json()
        
        assert "submissions" in data
        assert "total" in data


class TestSupraPanelEnrichment:
    """SUPRA Panel enrichment with quality, availability, compliance, terrain_solutions"""

    def test_supra_panel_enriched(self):
        """POST /supra-panel — returns enriched data with x6010-x6020"""
        response = requests.post(
            f"{API_PREFIX}/supra-panel",
            json={
                "species": "chevreuil",
                "season": "printemps",
                "soil_type": "mixte",
                "substrate": "bois_mou"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify base SUPRA data
        assert "score" in data
        assert "recommendations" in data
        assert "energy_protein" in data
        assert "recipe" in data
        assert "evidence" in data
        assert "costs" in data
        assert "substrate_comparison" in data
        assert "products" in data
        assert "order" in data
        assert "ecozone" in data
        
        # Verify terrain_solutions (x6020)
        assert "terrain_solutions" in data
        assert "solutions" in data["terrain_solutions"]
        assert "total" in data["terrain_solutions"]
        assert "categories" in data["terrain_solutions"]
        
        # Verify products are enriched with quality/availability/compliance
        products = data["products"]["products"]
        assert len(products) > 0
        
        for product in products:
            # x6010 quality enrichment
            if product.get("quality"):
                assert "score" in product["quality"]
                assert "grade" in product["quality"]
                assert "efficiency_ratio" in product["quality"]
            
            # x6011 availability enrichment
            if product.get("availability"):
                assert "canada_score" in product["availability"]
                assert "province_status" in product["availability"]
                assert "usa_available" in product["availability"]
            
            # x6012 compliance enrichment
            if product.get("compliance"):
                assert "score" in product["compliance"]
                assert "grade" in product["compliance"]
                assert "certifications" in product["compliance"]


class TestAllProductIds:
    """Test all 10 product IDs work correctly"""

    @pytest.mark.parametrize("product_id", PRODUCT_IDS)
    def test_quality_for_all_products(self, product_id):
        """x6010 quality works for all products"""
        response = requests.post(
            f"{API_PREFIX}/products/quality",
            json={"product_id": product_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" not in data
        assert data["product_id"] == product_id

    @pytest.mark.parametrize("product_id", PRODUCT_IDS)
    def test_availability_for_all_products(self, product_id):
        """x6011 availability works for all products"""
        response = requests.post(
            f"{API_PREFIX}/products/availability",
            json={"product_id": product_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" not in data
        assert data["product_id"] == product_id

    @pytest.mark.parametrize("product_id", PRODUCT_IDS)
    def test_compliance_for_all_products(self, product_id):
        """x6012 compliance works for all products"""
        response = requests.post(
            f"{API_PREFIX}/products/compliance",
            json={"product_id": product_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" not in data
        assert data["product_id"] == product_id

    @pytest.mark.parametrize("product_id", PRODUCT_IDS)
    def test_ecosystem_for_all_products(self, product_id):
        """x6030 ecosystem works for all products"""
        response = requests.post(
            f"{API_PREFIX}/products/ecosystem",
            json={"product_id": product_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" not in data
        assert data["product_id"] == product_id
