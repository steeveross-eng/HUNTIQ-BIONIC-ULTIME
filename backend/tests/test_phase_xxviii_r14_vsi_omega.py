"""
Phase XXVIII · ORDRE N°52-R14 OPTION ζ — Tests anti-régressifs VSI S3
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide le module `mffp_vsi_url_omega.py` qui contourne la limite K8s
ephemeral-storage en lisant pee_maj.gpkg directement depuis B2 via VSI.

Tests :
  · API publique exposée + constantes
  · _strip_endpoint_protocol() : retire https://
  · configure_gdal_for_b2() : pose les env vars AWS_*, retourne configured=True
  · configure_gdal_for_b2() : missing keys → configured=False, remediation
  · get_pee_maj_b2_key_from_manifest() : lit slot manifest réel
  · get_pee_maj_vsi_url() : construit /vsis3/{bucket}/{key}
  · get_pee_maj_vsi_url() : raise si bucket absent
  · get_pee_maj_vsi_url() : raise si key introuvable
  · execute_subset_extraction(vsi_url=...) : signature accepte vsi_url
"""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest


@pytest.fixture()
def mod():
    import engines.v8_institutional.especes.mffp_vsi_url_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def restore_env():
    """Sauvegarde + restaure les env vars potentiellement écrasées."""
    keys = ["B2_KEY_ID", "B2_APPLICATION_KEY", "B2_BUCKET_NAME",
            "B2_ENDPOINT_URL", "B2_REGION",
            "AWS_S3_ENDPOINT", "AWS_HTTPS", "AWS_VIRTUAL_HOSTING",
            "AWS_REGION", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
            "CPL_VSIL_CURL_CACHE_SIZE", "VSI_CACHE", "VSI_CACHE_SIZE",
            "GDAL_HTTP_TIMEOUT", "GDAL_HTTP_RETRY_ATTEMPTS",
            "GDAL_HTTP_RETRY_DELAY", "CPL_VSIL_USE_HEAD",
            "CPL_VSIL_CURL_NON_CACHED"]
    saved = {k: os.environ.get(k) for k in keys}
    yield
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


# ═════════════════════════════════════════════════════════════════════════
# 1. API publique
# ═════════════════════════════════════════════════════════════════════════
def test_vsi_exports_public_api(mod):
    assert hasattr(mod, "configure_gdal_for_b2")
    assert hasattr(mod, "get_pee_maj_b2_key_from_manifest")
    assert hasattr(mod, "get_pee_maj_vsi_url")
    assert hasattr(mod, "probe_vsi_pee_maj")
    assert "configure_gdal_for_b2" in mod.__all__
    assert "get_pee_maj_vsi_url" in mod.__all__
    assert mod.SLOT_ID == "FORET_MFFP_PEE_MAJ_Ω"
    assert mod.PEE_MAJ_FILENAME == "pee_maj.gpkg"


# ═════════════════════════════════════════════════════════════════════════
# 2. _strip_endpoint_protocol
# ═════════════════════════════════════════════════════════════════════════
def test_strip_endpoint_protocol_https(mod):
    assert mod._strip_endpoint_protocol(
        "https://s3.ca-east-006.backblazeb2.com"
    ) == "s3.ca-east-006.backblazeb2.com"


def test_strip_endpoint_protocol_http(mod):
    assert mod._strip_endpoint_protocol(
        "http://example.com/"
    ) == "example.com"


def test_strip_endpoint_protocol_no_proto(mod):
    assert mod._strip_endpoint_protocol(
        "s3.ca-east-006.backblazeb2.com"
    ) == "s3.ca-east-006.backblazeb2.com"


# ═════════════════════════════════════════════════════════════════════════
# 3. configure_gdal_for_b2
# ═════════════════════════════════════════════════════════════════════════
def test_configure_gdal_missing_keys(mod, restore_env):
    """Si B2_KEY_ID absent → configured=False + missing = ['B2_KEY_ID']."""
    os.environ.pop("B2_KEY_ID", None)
    os.environ.pop("B2_APPLICATION_KEY", None)
    os.environ["B2_BUCKET_NAME"] = "test"
    os.environ["B2_ENDPOINT_URL"] = "https://s3.test.com"
    result = mod.configure_gdal_for_b2()
    assert result["configured"] is False
    assert "B2_KEY_ID" in result["missing"]
    assert "B2_APPLICATION_KEY" in result["missing"]
    assert "remediation" in result


def test_configure_gdal_complete(mod, restore_env):
    os.environ["B2_KEY_ID"] = "test_key_id"
    os.environ["B2_APPLICATION_KEY"] = "test_secret"
    os.environ["B2_BUCKET_NAME"] = "pee-maj-gpkg"
    os.environ["B2_ENDPOINT_URL"] = "https://s3.ca-east-006.backblazeb2.com"
    os.environ["B2_REGION"] = "ca-east-006"
    result = mod.configure_gdal_for_b2()
    assert result["configured"] is True
    assert result["bucket_used"] == "pee-maj-gpkg"
    assert result["region_used"] == "ca-east-006"
    assert result["endpoint_used"] == "s3.ca-east-006.backblazeb2.com"
    # Vérifier les env vars AWS posées (path-style + HTTPS)
    assert os.environ["AWS_S3_ENDPOINT"] == "s3.ca-east-006.backblazeb2.com"
    assert os.environ["AWS_HTTPS"] == "YES"
    assert os.environ["AWS_VIRTUAL_HOSTING"] == "FALSE"
    assert os.environ["AWS_REGION"] == "ca-east-006"
    assert os.environ["AWS_ACCESS_KEY_ID"] == "test_key_id"
    assert os.environ["AWS_SECRET_ACCESS_KEY"] == "test_secret"
    # Performance VSI
    assert "CPL_VSIL_CURL_CACHE_SIZE" in result["gdal_options_set"]
    assert "VSI_CACHE" in result["gdal_options_set"]


def test_configure_gdal_does_not_leak_secret_in_response(mod, restore_env):
    """Le retour ne doit JAMAIS contenir B2_APPLICATION_KEY en clair."""
    os.environ["B2_KEY_ID"] = "test_key_id"
    os.environ["B2_APPLICATION_KEY"] = "ULTRA_SECRET_DO_NOT_LEAK"
    os.environ["B2_BUCKET_NAME"] = "test"
    os.environ["B2_ENDPOINT_URL"] = "https://test.com"
    result = mod.configure_gdal_for_b2()
    response_str = json.dumps(result)
    assert "ULTRA_SECRET_DO_NOT_LEAK" not in response_str


# ═════════════════════════════════════════════════════════════════════════
# 4. get_pee_maj_b2_key_from_manifest
# ═════════════════════════════════════════════════════════════════════════
def test_get_b2_key_returns_none_if_manifest_absent(mod, tmp_path,
                                                     monkeypatch):
    fake_manifest = tmp_path / "missing.json"
    monkeypatch.setattr(mod, "SLOT_MANIFEST_PATH", fake_manifest)
    assert mod.get_pee_maj_b2_key_from_manifest() is None


def test_get_b2_key_extracts_from_manifest(mod, tmp_path, monkeypatch):
    fake_manifest = tmp_path / "manifest.json"
    fake_manifest.write_text(json.dumps({
        "slots": {
            "FORET_MFFP_PEE_MAJ_Ω": {
                "uploads": [
                    {
                        "filename": "pee_maj.gpkg",
                        "source": "BACKBLAZE_B2_MULTIPART",
                        "b2_key": "FORET_MFFP_PEE_MAJ/pee_maj.gpkg",
                    },
                    {
                        "filename": "old.gpkg",
                        "source": "BACKBLAZE_B2_MULTIPART",
                        "b2_key": "old/old.gpkg",
                    },
                ],
            }
        }
    }), encoding="utf-8")
    monkeypatch.setattr(mod, "SLOT_MANIFEST_PATH", fake_manifest)
    key = mod.get_pee_maj_b2_key_from_manifest()
    assert key == "FORET_MFFP_PEE_MAJ/pee_maj.gpkg"


def test_get_b2_key_ignores_non_pee_maj_filename(mod, tmp_path,
                                                  monkeypatch):
    fake_manifest = tmp_path / "manifest.json"
    fake_manifest.write_text(json.dumps({
        "slots": {
            "FORET_MFFP_PEE_MAJ_Ω": {
                "uploads": [
                    {"filename": "other.gpkg",
                     "source": "BACKBLAZE_B2_MULTIPART",
                     "b2_key": "ignore.gpkg"},
                ]
            }
        }
    }), encoding="utf-8")
    monkeypatch.setattr(mod, "SLOT_MANIFEST_PATH", fake_manifest)
    assert mod.get_pee_maj_b2_key_from_manifest() is None


# ═════════════════════════════════════════════════════════════════════════
# 5. get_pee_maj_vsi_url
# ═════════════════════════════════════════════════════════════════════════
def test_get_vsi_url_raises_if_bucket_absent(mod, restore_env):
    os.environ.pop("B2_BUCKET_NAME", None)
    with pytest.raises(ValueError, match="B2_BUCKET_NAME"):
        mod.get_pee_maj_vsi_url(b2_key="some/key.gpkg")


def test_get_vsi_url_raises_if_key_unknown(mod, restore_env, tmp_path,
                                            monkeypatch):
    os.environ["B2_BUCKET_NAME"] = "my-bucket"
    fake_manifest = tmp_path / "missing.json"
    monkeypatch.setattr(mod, "SLOT_MANIFEST_PATH", fake_manifest)
    with pytest.raises(ValueError, match="b2_key introuvable"):
        mod.get_pee_maj_vsi_url()


def test_get_vsi_url_builds_canonical_path(mod, restore_env):
    os.environ["B2_BUCKET_NAME"] = "pee-maj-gpkg"
    url = mod.get_pee_maj_vsi_url(b2_key="FORET_MFFP/pee_maj.gpkg")
    assert url == "/vsis3/pee-maj-gpkg/FORET_MFFP/pee_maj.gpkg"


def test_get_vsi_url_with_explicit_key_overrides_manifest(
        mod, restore_env, tmp_path, monkeypatch):
    os.environ["B2_BUCKET_NAME"] = "test-bucket"
    fake_manifest = tmp_path / "manifest.json"
    fake_manifest.write_text(json.dumps({
        "slots": {"FORET_MFFP_PEE_MAJ_Ω": {"uploads": [
            {"filename": "pee_maj.gpkg",
             "source": "BACKBLAZE_B2_MULTIPART",
             "b2_key": "FROM_MANIFEST/pee_maj.gpkg"},
        ]}}
    }), encoding="utf-8")
    monkeypatch.setattr(mod, "SLOT_MANIFEST_PATH", fake_manifest)
    url = mod.get_pee_maj_vsi_url(b2_key="EXPLICIT_OVERRIDE/pee_maj.gpkg")
    assert "EXPLICIT_OVERRIDE" in url
    assert "FROM_MANIFEST" not in url


# ═════════════════════════════════════════════════════════════════════════
# 6. execute_subset_extraction signature accepte vsi_url
# ═════════════════════════════════════════════════════════════════════════
def test_subset_extraction_signature_accepts_vsi_url():
    from engines.v8_institutional.especes import (
        mffp_subset_extractor_omega as ext)
    import inspect
    sig = inspect.signature(ext.execute_subset_extraction)
    assert "vsi_url" in sig.parameters
    assert sig.parameters["vsi_url"].default is None
    assert "pee_maj_local_path" in sig.parameters


def test_subset_extraction_vsi_path_skips_local_existence_check(
        mod, restore_env, tmp_path, monkeypatch):
    """Si vsi_url fourni, ne vérifie pas src.exists() local."""
    from engines.v8_institutional.especes import (
        mffp_subset_extractor_omega as ext)
    # Configure GDAL stub
    os.environ["B2_KEY_ID"] = "k"
    os.environ["B2_APPLICATION_KEY"] = "s"
    os.environ["B2_BUCKET_NAME"] = "b"
    os.environ["B2_ENDPOINT_URL"] = "https://test.com"

    # Mock pyogrio pour ne pas faire d'appel HTTP réel
    fake_calls = {"list": None, "read": None}

    class FakePyogrio:
        @staticmethod
        def list_layers(src):
            fake_calls["list"] = src
            import numpy as np
            return np.array([["peuplement_ecoforestier", "Polygon"]])

        @staticmethod
        def read_dataframe(src, layer, bbox, use_arrow):
            fake_calls["read"] = {"src": src, "layer": layer,
                                   "bbox": bbox}
            import geopandas as gpd
            from shapely.geometry import Polygon
            return gpd.GeoDataFrame({
                "TY_COUV": ["FE"], "CL_DENS": ["A"],
                "CL_AGE": ["50"], "ESS_DOMI": ["ERS"],
                "geometry": [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
            }, crs="EPSG:32198")

        @staticmethod
        def write_dataframe(df, dst, layer, driver):
            Path(dst).write_bytes(b"fake_gpkg_content_for_test_only")

    import sys
    monkeypatch.setitem(sys.modules, "pyogrio", FakePyogrio)
    # Rediriger output dir vers tmp
    monkeypatch.setattr(ext, "SUBSETS_OUTPUT_ROOT", tmp_path)

    result = ext.execute_subset_extraction(
        vsi_url="/vsis3/test-bucket/path/to/pee_maj.gpkg")
    assert result["status"] == "EXECUTED"
    assert result["source_kind"] == "vsi_s3_b2"
    assert result["src_path"] == "/vsis3/test-bucket/path/to/pee_maj.gpkg"
    assert fake_calls["list"] == "/vsis3/test-bucket/path/to/pee_maj.gpkg"
    assert result["n_polygons_extracted"] == 1
