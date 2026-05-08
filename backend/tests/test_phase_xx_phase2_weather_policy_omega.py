"""test_phase_xx_phase2_weather_policy_omega — P20_PHASE2 weather doctrine.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral filename — no excluded keyword.
"""
from __future__ import annotations

import pytest


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        weather_provider_policy_omega as mod,
    )
    assert hasattr(mod, "assert_provider_allowed")
    assert hasattr(mod, "execute_weather_provider_policy_attest")
    assert hasattr(mod, "WeatherProviderDeprecatedError")
    assert "openweathermap" in mod.ACTIVE_PROVIDERS
    assert "noaa_cfsv2" in mod.DEPRECATED_PROVIDERS
    assert "copernicus" in mod.DEPRECATED_PROVIDERS


def test_assert_provider_allowed_owm_passes_omega():
    from engines.v8_institutional.especes.weather_provider_policy_omega import (
        assert_provider_allowed,
    )
    # Should not raise
    assert_provider_allowed("openweathermap")
    assert_provider_allowed("OpenWeatherMap")


def test_assert_provider_allowed_noaa_raises_omega():
    from engines.v8_institutional.especes.weather_provider_policy_omega import (
        assert_provider_allowed, WeatherProviderDeprecatedError,
    )
    with pytest.raises(
            WeatherProviderDeprecatedError,
            match="WEATHER_PROVIDER_DEPRECATED::noaa_cfsv2"):
        assert_provider_allowed("noaa_cfsv2")
    with pytest.raises(
            WeatherProviderDeprecatedError,
            match="WEATHER_PROVIDER_DEPRECATED"):
        assert_provider_allowed("NOAA")


def test_assert_provider_allowed_copernicus_raises_omega():
    from engines.v8_institutional.especes.weather_provider_policy_omega import (
        assert_provider_allowed, WeatherProviderDeprecatedError,
    )
    with pytest.raises(
            WeatherProviderDeprecatedError,
            match="WEATHER_PROVIDER_DEPRECATED::copernicus"):
        assert_provider_allowed("copernicus")
    with pytest.raises(WeatherProviderDeprecatedError):
        assert_provider_allowed("Copernicus_Marine")


def test_attest_persistence_omega(tmp_path, monkeypatch):
    """Anti-générique : vraie persistance overlay JSON."""
    import engines.v8_institutional.especes.weather_provider_policy_omega as mod
    monkeypatch.setattr(
        mod, "WEATHER_POLICY_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "WEATHER_POLICY_OVERLAY_PATH",
        tmp_path / "overlay.json")
    payload = mod.execute_weather_provider_policy_attest(
        persist=True)
    assert payload["activated"] is True
    assert payload["verdict"] == "WEATHER_PROVIDER_POLICY_ATTESTED"
    assert payload["v30_lock"] == "INVIOLÉ"
    assert len(payload["policy_sha256"]) == 64
    assert payload["active_providers"] == ["openweathermap"]
    assert "noaa_cfsv2" in payload["deprecated_providers"]
    assert (tmp_path / "overlay.json").exists()


def test_status_active_provider_omega(tmp_path, monkeypatch):
    import engines.v8_institutional.especes.weather_provider_policy_omega as mod
    payload = mod.get_weather_provider_policy_status()
    assert payload["openweathermap_status"] in (
        "ACTIVE_PRIMARY", "ACTIVE_NO_API_KEY")
    assert payload["noaa_status"] == (
        "DEPRECATED_ENFORCED_P20_PHASE2")
    assert payload["copernicus_status"] == (
        "DEPRECATED_ENFORCED_P20_PHASE2")
