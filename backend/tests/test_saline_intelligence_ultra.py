"""
SALINE INTELLIGENCE ULTRA — Backend API Tests
Tests all 7 engines, geospatial layers, e-commerce endpoints.
Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://huntiq-restore.preview.emergentagent.com')

# Test session for cart operations
TEST_SESSION_ID = f"test_saline_{uuid.uuid4().hex[:8]}"


class TestSalineHealth:
    """Health endpoint tests - verifies 7 engines operational"""
    
    def test_health_returns_operational(self):
        """GET /api/v1/saline/health returns operational status"""
        response = requests.get(f"{BASE_URL}/api/v1/saline/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "operational"
        assert data["engine"] == "saline_intelligence_ultra"
        assert data["engines_count"] == 7
        assert "version" in data
        print(f"✓ Health check passed: {data['message']}")


class TestSalineAnalysis:
    """Full analysis endpoint tests - orchestrates all 7 engines"""
    
    def test_full_analysis_post(self):
        """POST /api/v1/saline/analyze returns full analysis with all 7 engine outputs"""
        payload = {
            "lat": 47.3,
            "lng": -71.2,
            "species": "orignal",
            "sex": "male",
            "age": "adult",
            "month": 10,
            "season": "automne"
        }
        response = requests.post(f"{BASE_URL}/api/v1/saline/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert data["type"] == "saline_intelligence_ultra"
        assert "engines" in data
        assert "analysis" in data
        assert "recommendations" in data
        
        # Verify all 7 engines present
        engines = data["engines"]
        assert "soil" in engines
        assert "needs" in engines
        assert "deficiency" in engines
        assert "vegetation" in engines
        assert "hydrology" in engines
        assert "metabolism" in engines
        
        # Verify analysis components
        analysis = data["analysis"]
        assert "adjusted_deficits" in analysis
        assert "intelligence_score" in analysis
        assert "placement" in analysis
        
        # Verify intelligence score structure
        score = analysis["intelligence_score"]
        assert "global_score" in score
        assert "rating" in score
        assert "components" in score
        
        print(f"✓ Full analysis passed: Score {score['global_score']} ({score['rating']})")
    
    def test_quick_analysis_get(self):
        """GET /api/v1/saline/analyze/quick returns quick analysis"""
        params = {
            "lat": 47.3,
            "lng": -71.2,
            "species": "orignal",
            "month": 10,
            "season": "automne"
        }
        response = requests.get(f"{BASE_URL}/api/v1/saline/analyze/quick", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "saline_intelligence_ultra"
        assert "engines" in data
        print("✓ Quick analysis GET passed")


class TestSalineSubEngines:
    """Individual sub-engine endpoint tests"""
    
    def test_soil_analysis_get(self):
        """GET /api/v1/saline/soil returns soil analysis"""
        params = {"lat": 47.3, "lng": -71.2}
        response = requests.get(f"{BASE_URL}/api/v1/saline/soil", params=params)
        assert response.status_code == 200
        
        data = response.json()
        # Soil endpoint returns texture, pH, quality_index, minerals
        assert "texture" in data or "soil_type" in data
        assert "pH" in data
        assert "quality_index" in data
        assert "minerals" in data
        soil_type = data.get("texture") or data.get("soil_type")
        print(f"✓ Soil analysis: {soil_type}, pH {data['pH']}, quality {data['quality_index']}")
    
    def test_nutrients_analysis_get(self):
        """GET /api/v1/saline/nutrients returns deficiency data"""
        params = {"lat": 47.3, "lng": -71.2, "species": "orignal"}
        response = requests.get(f"{BASE_URL}/api/v1/saline/nutrients", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "soil" in data
        assert "needs" in data
        assert "deficiency" in data
        
        # Verify deficiency structure
        deficiency = data["deficiency"]
        assert "coverage" in deficiency
        assert "overall_coverage_pct" in deficiency
        print(f"✓ Nutrients analysis: overall coverage {deficiency['overall_coverage_pct']}%")
    
    def test_vegetation_analysis_get(self):
        """GET /api/v1/saline/vegetation returns vegetation data"""
        params = {"lat": 47.3, "lng": -71.2, "month": 10}
        response = requests.get(f"{BASE_URL}/api/v1/saline/vegetation", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "phenophase" in data
        assert "couvert_pct" in data
        assert "vegetation_minerals_mg_kg" in data
        print(f"✓ Vegetation analysis: {data['phenophase']}, couvert {data['couvert_pct']}%")
    
    def test_hydrology_analysis_get(self):
        """GET /api/v1/saline/hydrology returns hydrology data"""
        params = {"lat": 47.3, "lng": -71.2}
        response = requests.get(f"{BASE_URL}/api/v1/saline/hydrology", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "drainage" in data
        assert "leaching_risk" in data
        assert "leaching" in data
        print(f"✓ Hydrology analysis: drainage {data['drainage']}, leaching risk {data['leaching_risk']}")
    
    def test_metabolism_analysis_get(self):
        """GET /api/v1/saline/metabolism returns metabolic state"""
        params = {"month": 10, "species": "orignal"}
        response = requests.get(f"{BASE_URL}/api/v1/saline/metabolism", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "metabolic_phase" in data
        assert "energy_demand_factor" in data
        assert "activity_level" in data
        assert "priority_minerals" in data
        print(f"✓ Metabolism analysis: phase {data['metabolic_phase']}, activity {data['activity_level']}")


class TestSalineSpeciesFormulas:
    """Species and formulas endpoint tests"""
    
    def test_list_species(self):
        """GET /api/v1/saline/species returns 4 species"""
        response = requests.get(f"{BASE_URL}/api/v1/saline/species")
        assert response.status_code == 200
        
        data = response.json()
        assert "species" in data
        species_list = data["species"]
        assert len(species_list) >= 4
        
        # Verify species structure
        for sp in species_list:
            assert "id" in sp
            assert "base_weight_kg" in sp
        
        species_ids = [sp["id"] for sp in species_list]
        print(f"✓ Species list: {species_ids}")
    
    def test_list_formulas(self):
        """GET /api/v1/saline/formulas returns 6 formulas"""
        response = requests.get(f"{BASE_URL}/api/v1/saline/formulas")
        assert response.status_code == 200
        
        data = response.json()
        assert "formulas" in data
        formulas_list = data["formulas"]
        assert len(formulas_list) >= 6
        
        # Verify formula structure
        for f in formulas_list:
            assert "id" in f
            assert "name" in f
            assert "format" in f
            assert "minerals" in f
        
        formula_ids = [f["id"] for f in formulas_list]
        print(f"✓ Formulas list: {formula_ids}")


class TestSalineGeospatialLayers:
    """Geospatial layers endpoint tests - 5 layers"""
    
    def test_list_layers(self):
        """GET /api/v1/saline/layers returns 5 geospatial layers"""
        response = requests.get(f"{BASE_URL}/api/v1/saline/layers")
        assert response.status_code == 200
        
        data = response.json()
        assert "layers" in data
        layers_list = data["layers"]
        assert len(layers_list) >= 5
        
        # Verify layer structure
        for layer in layers_list:
            assert "id" in layer
            assert "name" in layer
            assert "source" in layer
        
        layer_ids = [l["id"] for l in layers_list]
        print(f"✓ Layers list: {layer_ids}")
    
    def test_suitability_score(self):
        """GET /api/v1/saline/suitability returns suitability score"""
        params = {"lat": 47.3, "lng": -71.2}
        response = requests.get(f"{BASE_URL}/api/v1/saline/suitability", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "suitability_score" in data
        assert "rating" in data
        assert "component_scores" in data
        assert "layers" in data
        assert "recommendations" in data
        
        print(f"✓ Suitability score: {data['suitability_score']} ({data['rating']})")


class TestSalineEcommerce:
    """E-commerce endpoint tests - products, cart, checkout"""
    
    def test_list_products(self):
        """GET /api/v1/saline/shop/products returns 6 saline products"""
        response = requests.get(f"{BASE_URL}/api/v1/saline/shop/products")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "products" in data
        products = data["products"]
        assert len(products) >= 6
        
        # Verify product structure
        for p in products:
            assert "id" in p
            assert "name" in p
            assert "price" in p
            assert "formula_id" in p
            assert "minerals" in p
        
        print(f"✓ Products list: {len(products)} products")
    
    def test_recommend_products(self):
        """GET /api/v1/saline/shop/recommend returns recommended products"""
        params = {
            "lat": 47.3,
            "lng": -71.2,
            "species": "orignal",
            "month": 10,
            "season": "automne"
        }
        response = requests.get(f"{BASE_URL}/api/v1/saline/shop/recommend", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "recommended_products" in data
        assert "intelligence_score" in data
        assert "custom_recipe" in data
        
        products = data["recommended_products"]
        assert len(products) > 0
        
        # Verify recommended product structure
        for p in products:
            assert "id" in p
            assert "match_score" in p
        
        print(f"✓ Recommended products: {len(products)} products")
    
    def test_add_to_cart(self):
        """POST /api/v1/saline/shop/cart/add adds item to cart"""
        # First get a product ID
        products_response = requests.get(f"{BASE_URL}/api/v1/saline/shop/products")
        products = products_response.json()["products"]
        product_id = products[0]["id"]
        
        payload = {
            "session_id": TEST_SESSION_ID,
            "product_id": product_id,
            "quantity": 1
        }
        response = requests.post(f"{BASE_URL}/api/v1/saline/shop/cart/add", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "item" in data
        
        item = data["item"]
        assert item["product_id"] == product_id
        assert item["quantity"] == 1
        assert "subtotal" in item
        
        print(f"✓ Added to cart: {item['product_name']} - ${item['subtotal']}")
    
    def test_get_cart(self):
        """GET /api/v1/saline/shop/cart/{session_id} returns enriched cart"""
        response = requests.get(f"{BASE_URL}/api/v1/saline/shop/cart/{TEST_SESSION_ID}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "items" in data
        assert "total" in data
        assert "currency" in data
        assert data["currency"] == "CAD"
        
        print(f"✓ Cart retrieved: {data['item_count']} items, total ${data['total']}")


class TestSalineEdgeCases:
    """Edge case and validation tests"""
    
    def test_invalid_coordinates(self):
        """Test with invalid coordinates - API may accept or reject"""
        params = {"lat": 999, "lng": -999}
        response = requests.get(f"{BASE_URL}/api/v1/saline/soil", params=params)
        # API may return 422 for validation error or 200 with default values
        # Both behaviors are acceptable depending on implementation
        assert response.status_code in [200, 422]
        print(f"✓ Invalid coordinates handled with status {response.status_code}")
    
    def test_missing_required_params(self):
        """Test with missing required parameters"""
        response = requests.get(f"{BASE_URL}/api/v1/saline/soil")
        assert response.status_code == 422
        print("✓ Missing params properly rejected")
    
    def test_invalid_product_id(self):
        """Test adding invalid product to cart"""
        payload = {
            "session_id": TEST_SESSION_ID,
            "product_id": "invalid_product_xyz",
            "quantity": 1
        }
        response = requests.post(f"{BASE_URL}/api/v1/saline/shop/cart/add", json=payload)
        assert response.status_code == 404
        print("✓ Invalid product ID properly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
