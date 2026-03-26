"""
Test Suite: Nutrition Intelligence SUPRA x5000 + x6000
Tests all endpoints for the HUNTIQ-V6 SUPRA Phase 2 feature.
BCE-4X / STEEVE-MAX V6
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://huntiq-restore.preview.emergentagent.com')


class TestSupraPanelEndpoint:
    """Tests for POST /api/v6/nutrition-intelligence/supra-panel"""
    
    def test_supra_panel_chevreuil_printemps(self):
        """Test SUPRA panel with chevreuil species in printemps season"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/supra-panel", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte",
            "substrate": "bois_mou"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify all required fields are present
        assert "score" in data, "Missing 'score' in response"
        assert "recipe" in data, "Missing 'recipe' in response"
        assert "products" in data, "Missing 'products' in response"
        assert "evidence" in data, "Missing 'evidence' in response"
        assert "costs" in data, "Missing 'costs' in response"
        assert "ecozone" in data, "Missing 'ecozone' in response"
        
        # Verify score structure
        score = data["score"]
        assert "score_global" in score
        assert "grade" in score
        assert "scores_par_mineral" in score
        assert isinstance(score["score_global"], int)
        assert score["score_global"] >= 0 and score["score_global"] <= 100
        
    def test_supra_panel_orignal(self):
        """Test SUPRA panel with orignal species"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/supra-panel", json={
            "species": "orignal",
            "season": "ete",
            "soil_type": "acide",
            "substrate": "bois_dur"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["score"]["species"] == "orignal"
        
    def test_supra_panel_ours_noir(self):
        """Test SUPRA panel with ours_noir species (new species added)"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/supra-panel", json={
            "species": "ours_noir",
            "season": "printemps",
            "soil_type": "mixte",
            "substrate": "bois_mou"
        })
        assert response.status_code == 200
        data = response.json()
        # ours_noir should be recognized
        assert "score" in data
        assert "ecozone" in data


class TestProductScoreEndpoints:
    """Tests for x6000 Product Score endpoints"""
    
    def test_product_score_individual(self):
        """POST /api/v6/nutrition-intelligence/products/score - individual product score"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/products/score", json={
            "product_id": "trophy_rock_four65",
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        data = response.json()
        assert "score_global" in data
        assert "name" in data
        assert data["product_id"] == "trophy_rock_four65"
        assert isinstance(data["score_global"], int)
        
    def test_product_score_invalid_product(self):
        """Test with invalid product ID"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/products/score", json={
            "product_id": "invalid_product_xyz",
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        
    def test_products_all_ranking(self):
        """POST /api/v6/nutrition-intelligence/products/all - all products ranking"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/products/all", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert isinstance(data["products"], list)
        assert data["total"] > 0
        # Verify products are sorted by score (descending)
        scores = [p["score_global"] for p in data["products"]]
        assert scores == sorted(scores, reverse=True), "Products should be sorted by score descending"
        
    def test_products_compare(self):
        """POST /api/v6/nutrition-intelligence/products/compare - compare 2-4 products"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/products/compare", json={
            "product_ids": ["trophy_rock_four65", "pro_cal_lick", "bear_mineral_attract"],
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "best_product" in data
        assert "best_score" in data
        assert len(data["products"]) == 3
        
    def test_products_shop(self):
        """POST /api/v6/nutrition-intelligence/products/shop - filtered shop"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/products/shop", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte",
            "min_score": 70,
            "product_type": None
        })
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "filters" in data
        # All products should have score >= 70
        for p in data["products"]:
            assert p["score_global"] >= 70, f"Product {p['name']} has score {p['score_global']} < 70"


class TestEcozonesEndpoint:
    """Tests for GET /api/v6/nutrition-intelligence/ecozones"""
    
    def test_ecozones_orignal(self):
        """GET ecozones for orignal species"""
        response = requests.get(f"{BASE_URL}/api/v6/nutrition-intelligence/ecozones", params={
            "species": "orignal"
        })
        assert response.status_code == 200
        data = response.json()
        assert "species" in data
        assert "data" in data
        assert data["species"] == "orignal"
        assert "nom_commun" in data["data"]
        assert "habitat_principal" in data["data"]
        assert "zones_ecologiques" in data["data"]
        assert "comportement_saisonnier" in data["data"]
        
    def test_ecozones_chevreuil(self):
        """GET ecozones for chevreuil species"""
        response = requests.get(f"{BASE_URL}/api/v6/nutrition-intelligence/ecozones", params={
            "species": "chevreuil"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "chevreuil"
        assert "Cerf de Virginie" in data["data"]["nom_commun"]
        
    def test_ecozones_ours_noir(self):
        """GET ecozones for ours_noir species"""
        response = requests.get(f"{BASE_URL}/api/v6/nutrition-intelligence/ecozones", params={
            "species": "ours_noir"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "ours_noir"
        assert "Ours noir" in data["data"]["nom_commun"]
        
    def test_ecozones_all_species(self):
        """GET ecozones for all species (no filter)"""
        response = requests.get(f"{BASE_URL}/api/v6/nutrition-intelligence/ecozones")
        assert response.status_code == 200
        data = response.json()
        assert "all_species" in data
        assert "chevreuil" in data["all_species"]
        assert "orignal" in data["all_species"]
        assert "ours_noir" in data["all_species"]


class TestMineralScoreEndpoint:
    """Tests for POST /api/v6/nutrition-intelligence/score"""
    
    def test_score_chevreuil(self):
        """Test mineral score for chevreuil"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/score", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        data = response.json()
        assert "score_global" in data
        assert "grade" in data
        assert "scores_par_mineral" in data
        assert "zones_resume" in data
        
    def test_score_ours_noir(self):
        """Test mineral score accepts ours_noir as species"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/score", json={
            "species": "ours_noir",
            "season": "printemps",
            "soil_type": "acide"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "ours_noir"
        assert "score_global" in data


class TestEnergyProteinEndpoint:
    """Tests for POST /api/v6/nutrition-intelligence/energy-protein"""
    
    def test_energy_protein_chevreuil(self):
        """Test energy-protein for chevreuil"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/energy-protein", json={
            "species": "chevreuil",
            "season": "printemps"
        })
        assert response.status_code == 200
        data = response.json()
        assert "phase" in data
        assert "energy_need" in data
        assert "protein_need" in data
        assert "energy_blocks" in data
        assert "protein_blocks" in data
        assert "seasonal_mix" in data
        
    def test_energy_protein_orignal(self):
        """Test energy-protein accepts orignal"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/energy-protein", json={
            "species": "orignal",
            "season": "hiver"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "orignal"
        assert data["season"] == "hiver"
        
    def test_energy_protein_ours_noir(self):
        """Test energy-protein accepts ours_noir"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/energy-protein", json={
            "species": "ours_noir",
            "season": "printemps"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "ours_noir"
        # ours_noir printemps should have post-hibernation phase
        assert "hibernation" in data["phase"].lower() or "deficit" in data["phase"].lower()
        
    def test_energy_protein_ours_noir_hiver(self):
        """Test ours_noir in winter (hibernation - no feeding)"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/energy-protein", json={
            "species": "ours_noir",
            "season": "hiver"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["energy_need"] == "N/A"
        assert data["protein_need"] == "N/A"


class TestFullAnalysisEndpoint:
    """Tests for POST /api/v6/nutrition-intelligence/full-analysis"""
    
    def test_full_analysis(self):
        """Test full analysis endpoint returns all data"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/full-analysis", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte",
            "substrate": "bois_mou"
        })
        assert response.status_code == 200
        data = response.json()
        assert "recipe" in data
        assert "evidence" in data
        assert "substrate_comparison" in data
        assert "products" in data
        assert "ecozone" in data


class TestOtherEndpoints:
    """Tests for other nutrition intelligence endpoints"""
    
    def test_recommendations(self):
        """POST /api/v6/nutrition-intelligence/recommendations"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/recommendations", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        
    def test_order(self):
        """POST /api/v6/nutrition-intelligence/order"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/order", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "summary" in data
        
    def test_site_guide(self):
        """POST /api/v6/nutrition-intelligence/site-guide"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/site-guide", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "acide"
        })
        assert response.status_code == 200
        data = response.json()
        assert "implantation" in data
        assert "substrats" in data
        assert "construction" in data
        
    def test_costs(self):
        """POST /api/v6/nutrition-intelligence/costs"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/costs", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte",
            "substrate": "bois_mou"
        })
        assert response.status_code == 200
        data = response.json()
        assert "initial_cost_cad" in data
        assert "annual_cost_cad" in data
        
    def test_costs_compare(self):
        """POST /api/v6/nutrition-intelligence/costs/compare"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/costs/compare", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte"
        })
        assert response.status_code == 200
        data = response.json()
        assert "bois_mou" in data
        assert "bois_dur" in data
        assert "recommended" in data
        
    def test_recipe(self):
        """POST /api/v6/nutrition-intelligence/recipe"""
        response = requests.post(f"{BASE_URL}/api/v6/nutrition-intelligence/recipe", json={
            "species": "chevreuil",
            "season": "printemps",
            "soil_type": "mixte",
            "substrate": "bois_mou"
        })
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "ingredients_cles" in data
        assert "evidence" in data
        
    def test_evidence(self):
        """GET /api/v6/nutrition-intelligence/evidence"""
        response = requests.get(f"{BASE_URL}/api/v6/nutrition-intelligence/evidence", params={
            "mineral": "Ca"
        })
        assert response.status_code == 200
        data = response.json()
        assert "references" in data
        assert "count" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
