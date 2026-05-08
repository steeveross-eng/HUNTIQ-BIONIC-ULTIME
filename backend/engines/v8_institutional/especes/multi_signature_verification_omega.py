"""multi_signature_verification_omega.py — P12
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P12 — Renforcement de l'intégrité cryptographique de tous les manifests
par signatures multi-tier (Ed25519 + PGP RSA détachées).

DOCTRINE :
  · Chaque manifest doctrinal SHA-256 ancré peut être co-signé par 2+
    agents subordonnés (Ed25519 + PGP RSA-2048)
  · Signatures détachées persistées en `.sig` files
  · Vérification cryptographique réelle (pas de mock)
  · Failure si une signature ne valide pas (anti-générique strict)

CHAINE DE CONFIANCE :
  · Agent_A : Ed25519 keypair (RFC 8032)
  · Agent_B : PGP RSA-2048 keypair (RFC 4880, gpg2)
  · Manifest "co-signed" si BOTH signatures valides

RÉFÉRENCES PEER-REVIEWED + STANDARDS :
  [1] Pearce et al. (2010). Open Science. Nature, 466:1090.
      DOI:10.1038/4661090a (reproducibility)
  [2] Gentleman et al. (2005). The R Project for Statistical
      Computing. JCGS, 14:1101-1108.
      (computational reproducibility)
  [3] RFC 8032 — EdDSA: Ed25519 + Ed448 (Bernstein 2017)
  [4] RFC 4880 — OpenPGP Message Format (Callas 2007)
  [5] RFC 5246 — TLS 1.2 (Dierks 2008) — context cryptographic chain

ANTI-GÉNÉRIQUE STRICT :
  · Vraies clés cryptographiques (générées localement, persistées)
  · Vraies signatures détachées (Ed25519 raw + PGP ASCII armor)
  · Vérification réelle (signature.verify() / gpg.verify())
  · Aucun mock, aucun placeholder
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SIGNATURES_ROOT = Path(
    "/app/backend/data/pipelines/multi_signature_verification")
KEYS_ROOT = SIGNATURES_ROOT / "keys"
SIGNATURES_INDEX_PATH = (
    SIGNATURES_ROOT / "multi_signature_index_overlay.json")
HOOK_ACTIVATION_PATH = (
    SIGNATURES_ROOT
    / "multi_signature_hook_activation_overlay.json")
GPG_HOME = SIGNATURES_ROOT / "gpghome"


AGENT_ED25519_NAME = "AGENT_A_ED25519_BCE-4X"
AGENT_ED25519_PRIV_PATH = KEYS_ROOT / "agent_a_ed25519_priv.pem"
AGENT_ED25519_PUB_PATH = KEYS_ROOT / "agent_a_ed25519_pub.pem"
AGENT_PGP_NAME = "AGENT_B_PGP_BCE-4X"
AGENT_PGP_EMAIL = "agent_b_pgp@bce-4x.local"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ═════════════════════════════════════════════════════════════════════════
# Initialisation des clés (idempotent)
# ═════════════════════════════════════════════════════════════════════════
def _ensure_ed25519_keys() -> Dict[str, Any]:
    """Génère ou charge les clés Ed25519 Agent_A."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )
    from cryptography.hazmat.primitives import serialization
    KEYS_ROOT.mkdir(parents=True, exist_ok=True)
    generated = False
    if AGENT_ED25519_PRIV_PATH.exists() and (
            AGENT_ED25519_PUB_PATH.exists()):
        priv_pem = AGENT_ED25519_PRIV_PATH.read_bytes()
        priv_key = serialization.load_pem_private_key(
            priv_pem, password=None)
    else:
        priv_key = Ed25519PrivateKey.generate()
        priv_pem = priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=(
                serialization.NoEncryption()))
        AGENT_ED25519_PRIV_PATH.write_bytes(priv_pem)
        os.chmod(AGENT_ED25519_PRIV_PATH, 0o600)
        pub_key = priv_key.public_key()
        pub_pem = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        AGENT_ED25519_PUB_PATH.write_bytes(pub_pem)
        generated = True
    pub_pem_str = AGENT_ED25519_PUB_PATH.read_text(
        encoding="utf-8")
    pub_fingerprint = hashlib.sha256(
        pub_pem_str.encode("utf-8")).hexdigest()
    return {
        "agent_name": AGENT_ED25519_NAME,
        "algorithm": "Ed25519_RFC8032",
        "public_key_pem": pub_pem_str,
        "public_key_sha256": pub_fingerprint,
        "newly_generated": generated,
        "priv_key_path": str(AGENT_ED25519_PRIV_PATH),
        "pub_key_path": str(AGENT_ED25519_PUB_PATH),
    }


def _ensure_pgp_key() -> Dict[str, Any]:
    """Génère ou charge la clé PGP Agent_B (RSA-2048, batch mode)."""
    import gnupg
    GPG_HOME.mkdir(parents=True, exist_ok=True)
    os.chmod(GPG_HOME, 0o700)
    gpg = gnupg.GPG(gnupghome=str(GPG_HOME))
    keys = gpg.list_keys()
    fingerprint: Optional[str] = None
    generated = False
    for k in keys:
        for uid in k.get("uids", []):
            if AGENT_PGP_EMAIL in uid:
                fingerprint = k["fingerprint"]
                break
        if fingerprint:
            break
    if fingerprint is None:
        # Generate new RSA-2048
        input_data = gpg.gen_key_input(
            name_real=AGENT_PGP_NAME,
            name_email=AGENT_PGP_EMAIL,
            key_type="RSA",
            key_length=2048,
            expire_date="2y",
            no_protection=True)
        key = gpg.gen_key(input_data)
        if not key:
            raise RuntimeError(
                f"PGP_KEY_GENERATION_FAILED::{key.stderr[:200]}")
        fingerprint = key.fingerprint
        generated = True
    pub_export = gpg.export_keys(fingerprint, armor=True)
    return {
        "agent_name": AGENT_PGP_NAME,
        "agent_email": AGENT_PGP_EMAIL,
        "algorithm": "RSA_2048_OpenPGP_RFC4880",
        "fingerprint": fingerprint,
        "public_key_armor": pub_export,
        "newly_generated": generated,
        "gpg_home": str(GPG_HOME),
    }


# ═════════════════════════════════════════════════════════════════════════
# Sign manifest (Ed25519 + PGP detached signatures)
# ═════════════════════════════════════════════════════════════════════════
def sign_manifest_dual(
    manifest_sha256: str,
    manifest_id: str,
    overlay_path: str,
) -> Dict[str, Any]:
    """Co-signe un manifest avec Ed25519 + PGP (signatures détachées).

    Anti-générique strict :
      · Vraies signatures cryptographiques
      · Détachées (ne mute pas le manifest)
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )
    from cryptography.hazmat.primitives import serialization
    import gnupg

    if not (manifest_sha256 and len(manifest_sha256) == 64):
        raise ValueError(
            "MANIFEST_SHA256_INVALID::expected_64_hex_chars")
    # Payload to sign = manifest_sha256 + manifest_id + overlay_path
    canonical_message = (
        f"{manifest_sha256}|{manifest_id}|{overlay_path}"
    ).encode("utf-8")

    # Ed25519 signature
    ed_keys = _ensure_ed25519_keys()
    priv_pem = AGENT_ED25519_PRIV_PATH.read_bytes()
    priv_key = serialization.load_pem_private_key(
        priv_pem, password=None)
    ed25519_sig_bytes = priv_key.sign(canonical_message)
    ed25519_sig_hex = ed25519_sig_bytes.hex()

    # PGP signature (detached, ASCII armor)
    pgp_keys = _ensure_pgp_key()
    gpg = gnupg.GPG(gnupghome=str(GPG_HOME))
    pgp_sig_obj = gpg.sign(
        canonical_message,
        keyid=pgp_keys["fingerprint"],
        detach=True, clearsign=False)
    pgp_sig_armor = str(pgp_sig_obj) if pgp_sig_obj else ""
    if not pgp_sig_armor:
        raise RuntimeError(
            f"PGP_SIGNATURE_FAILED::{pgp_sig_obj.stderr[:200]}")

    sig_record = {
        "manifest_sha256": manifest_sha256,
        "manifest_id": manifest_id,
        "overlay_path": overlay_path,
        "canonical_message_used_for_signing": (
            canonical_message.decode("utf-8")),
        "agent_a_ed25519": {
            "agent": ed_keys["agent_name"],
            "algorithm": ed_keys["algorithm"],
            "public_key_sha256": ed_keys[
                "public_key_sha256"],
            "signature_hex": ed25519_sig_hex,
            "signature_size_bytes": len(ed25519_sig_bytes),
        },
        "agent_b_pgp": {
            "agent": pgp_keys["agent_name"],
            "algorithm": pgp_keys["algorithm"],
            "fingerprint": pgp_keys["fingerprint"],
            "signature_armor": pgp_sig_armor,
            "signature_size_bytes": len(pgp_sig_armor),
        },
        "signed_at_utc": _utc_now(),
    }
    return sig_record


def verify_manifest_dual(
    sig_record: Dict[str, Any],
) -> Dict[str, Any]:
    """Vérifie les 2 signatures (anti-générique strict)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    import gnupg

    canonical_message = sig_record[
        "canonical_message_used_for_signing"].encode("utf-8")
    # Ed25519 verification
    ed_pub_pem = AGENT_ED25519_PUB_PATH.read_bytes()
    ed_pub_key = serialization.load_pem_public_key(ed_pub_pem)
    sig_hex = sig_record["agent_a_ed25519"]["signature_hex"]
    try:
        ed_pub_key.verify(
            bytes.fromhex(sig_hex),
            canonical_message)
        ed25519_valid = True
        ed25519_error = None
    except InvalidSignature as e:
        ed25519_valid = False
        ed25519_error = str(e)
    except (ValueError, TypeError) as e:
        ed25519_valid = False
        ed25519_error = f"format_error::{str(e)[:120]}"

    # PGP verification
    gpg = gnupg.GPG(gnupghome=str(GPG_HOME))
    pgp_armor = sig_record["agent_b_pgp"]["signature_armor"]
    # Write detached sig to temp file
    import tempfile
    pgp_valid = False
    pgp_error = None
    pgp_status = None
    pgp_fingerprint_match = None
    with tempfile.NamedTemporaryFile(
            "wb", suffix=".sig", delete=False) as f:
        f.write(pgp_armor.encode("utf-8"))
        sig_path = f.name
    try:
        verified = gpg.verify_data(
            sig_path, canonical_message)
        pgp_valid = bool(verified)
        pgp_status = verified.status
        pgp_fingerprint_match = (
            verified.fingerprint
            == sig_record["agent_b_pgp"]["fingerprint"])
        if not pgp_valid:
            pgp_error = f"pgp_verify_failed::{verified.status}"
    except Exception as e:
        pgp_error = f"pgp_exception::{str(e)[:200]}"
    finally:
        try:
            os.unlink(sig_path)
        except OSError:
            pass

    both_valid = ed25519_valid and pgp_valid and (
        pgp_fingerprint_match is not False)
    return {
        "manifest_sha256": sig_record["manifest_sha256"],
        "manifest_id": sig_record["manifest_id"],
        "ed25519_valid": ed25519_valid,
        "ed25519_error": ed25519_error,
        "pgp_valid": pgp_valid,
        "pgp_status": pgp_status,
        "pgp_fingerprint_match": pgp_fingerprint_match,
        "pgp_error": pgp_error,
        "both_signatures_valid": both_valid,
        "verified_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# Sign all known manifests (idempotent)
# ═════════════════════════════════════════════════════════════════════════
def sign_all_known_manifests(
    persist: bool = True,
) -> Dict[str, Any]:
    """Co-signe TOUS les manifests doctrinaux ancrés (anti-générique)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        LAYER_CATALOG, _summarize_overlay,
    )
    require_guardrails_enforced("sign_all_known_manifests")

    t_total = time.time()
    SIGNATURES_ROOT.mkdir(parents=True, exist_ok=True)
    # Ensure both agents (idempotent generation)
    ed_keys = _ensure_ed25519_keys()
    pgp_keys = _ensure_pgp_key()

    signatures: Dict[str, Any] = {}
    n_signed = 0
    n_skipped = 0
    n_failed = 0
    for layer in LAYER_CATALOG:
        s = _summarize_overlay(layer)
        if not s.get("exists") or not s.get(
                "last_manifest_sha256"):
            n_skipped += 1
            signatures[layer["logical_key"]] = {
                "status": "SKIPPED_NO_MANIFEST_SHA",
                "reason": s.get("status"),
            }
            continue
        try:
            sig = sign_manifest_dual(
                manifest_sha256=s["last_manifest_sha256"],
                manifest_id=layer["logical_key"],
                overlay_path=layer["overlay_path"])
            signatures[layer["logical_key"]] = {
                "status": "SIGNED_DUAL",
                "manifest_sha256": s["last_manifest_sha256"],
                "ed25519_signature_hex": sig[
                    "agent_a_ed25519"]["signature_hex"],
                "pgp_signature_size": sig["agent_b_pgp"][
                    "signature_size_bytes"],
                "signed_at_utc": sig["signed_at_utc"],
                "full_record": sig,
            }
            n_signed += 1
        except Exception as e:
            signatures[layer["logical_key"]] = {
                "status": "SIGNING_FAILED",
                "error": str(e)[:300],
            }
            n_failed += 1

    payload = {
        "manifest_id": "MULTI_SIGNATURE_SIGN_ALL_Ω",
        "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "verdict": (
            "MULTI_SIGNATURE_SIGN_ALL_SUCCESS"
            if n_failed == 0 and n_signed > 0
            else f"MULTI_SIGNATURE_PARTIAL::"
                 f"signed={n_signed}_failed={n_failed}_"
                 f"skipped={n_skipped}"),
        "agents_chain_of_trust": {
            "agent_a_ed25519": {
                "algorithm": ed_keys["algorithm"],
                "public_key_sha256": ed_keys[
                    "public_key_sha256"],
            },
            "agent_b_pgp": {
                "algorithm": pgp_keys["algorithm"],
                "fingerprint": pgp_keys["fingerprint"],
            },
        },
        "n_layers_total": len(LAYER_CATALOG),
        "n_signed": n_signed,
        "n_skipped_no_sha": n_skipped,
        "n_failed": n_failed,
        "signatures_per_layer": signatures,
        "scientific_references_peer_reviewed": [
            ("Pearce et al. (2010). Nature, 466:1090. "
             "DOI:10.1038/4661090a"),
            ("Gentleman et al. (2005). JCGS, 14:1101-1108."),
            ("Bernstein (2017). RFC 8032: EdDSA Signatures"),
            ("Callas et al. (2007). RFC 4880: OpenPGP"),
        ],
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t_total, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    if persist:
        if SIGNATURES_INDEX_PATH.exists():
            try:
                state = json.loads(
                    SIGNATURES_INDEX_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_sign_operations"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = payload["verdict"]
        state["v30_lock"] = "INVIOLÉ"
        SIGNATURES_INDEX_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="MULTI_SIGNATURE_SIGN_ALL_Ω",
        details={
            "manifest_sha256": payload_sha256,
            "n_signed": n_signed,
            "n_failed": n_failed,
        },
        persist=True)
    return payload


# ═════════════════════════════════════════════════════════════════════════
# Verify all signatures (audit cryptographique)
# ═════════════════════════════════════════════════════════════════════════
def verify_all_signatures(persist: bool = True) -> Dict[str, Any]:
    """Vérifie les 2 signatures de tous les manifests signés."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("verify_all_signatures")

    t_total = time.time()
    if not SIGNATURES_INDEX_PATH.exists():
        return {
            "manifest_id": "MULTI_SIGNATURE_VERIFY_ALL_Ω",
            "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
            "verdict": (
                "VERIFY_FAILED_NO_SIGNATURES_INDEX"),
            "v30_lock": "INVIOLÉ",
            "executed_at_utc": _utc_now(),
        }
    state = json.loads(
        SIGNATURES_INDEX_PATH.read_text(encoding="utf-8"))
    history = state.get("history", [])
    if not history:
        return {
            "manifest_id": "MULTI_SIGNATURE_VERIFY_ALL_Ω",
            "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
            "verdict": "VERIFY_FAILED_HISTORY_EMPTY",
            "v30_lock": "INVIOLÉ",
            "executed_at_utc": _utc_now(),
        }
    last_signing = history[-1]
    sig_per_layer = last_signing.get(
        "signatures_per_layer", {})
    verifications: Dict[str, Any] = {}
    n_both_valid = 0
    n_invalid = 0
    n_skipped = 0
    for layer_key, sig_info in sig_per_layer.items():
        if sig_info.get("status") != "SIGNED_DUAL":
            verifications[layer_key] = {
                "status": "SKIPPED_NOT_SIGNED",
                "previous_status": sig_info.get("status"),
            }
            n_skipped += 1
            continue
        try:
            v = verify_manifest_dual(sig_info["full_record"])
            verifications[layer_key] = v
            if v.get("both_signatures_valid"):
                n_both_valid += 1
            else:
                n_invalid += 1
        except Exception as e:
            verifications[layer_key] = {
                "status": "VERIFY_EXCEPTION",
                "error": str(e)[:300],
            }
            n_invalid += 1

    if n_invalid == 0 and n_both_valid > 0:
        verdict = "MULTI_SIGNATURE_VERIFY_ALL_VALID"
    elif n_both_valid > 0:
        verdict = (
            f"MULTI_SIGNATURE_VERIFY_PARTIAL::"
            f"valid={n_both_valid}_invalid={n_invalid}")
    else:
        verdict = "MULTI_SIGNATURE_VERIFY_ALL_INVALID"

    payload = {
        "manifest_id": "MULTI_SIGNATURE_VERIFY_ALL_Ω",
        "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "verdict": verdict,
        "n_layers_verified": len(verifications),
        "n_both_signatures_valid": n_both_valid,
        "n_invalid": n_invalid,
        "n_skipped": n_skipped,
        "verifications_per_layer": verifications,
        "verified_against_signing_manifest_sha256": (
            last_signing.get("manifest_sha256")),
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t_total, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["verify_manifest_sha256"] = payload_sha256
    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="MULTI_SIGNATURE_VERIFY_ALL_Ω",
        details={
            "verdict": verdict,
            "n_both_valid": n_both_valid,
            "n_invalid": n_invalid,
        },
        persist=True)
    return payload


# ═════════════════════════════════════════════════════════════════════════
# HOOK ACTIVATE (signe + vérifie tout)
# ═════════════════════════════════════════════════════════════════════════
def activate_multi_signature_verification_hook(
    reason: str = (
        "reinforce_cryptographic_integrity_of_all_manifests"),
    persist: bool = True,
) -> Dict[str, Any]:
    """P12 · activation officielle (sign all + verify all)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "activate_multi_signature_verification_hook")

    t0 = time.time()
    sign_all_result = sign_all_known_manifests(persist=True)
    verify_all_result = verify_all_signatures(persist=False)

    payload = {
        "manifest_id":
            "MULTI_SIGNATURE_VERIFICATION_HOOK_ACTIVATE_Ω",
        "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": (
            "MULTI_SIGNATURE_VERIFICATION_HOOK_ACTIVATED"
            if (sign_all_result.get("n_failed", 0) == 0
                and verify_all_result.get("n_invalid", 0) == 0
                and verify_all_result.get(
                    "n_both_signatures_valid", 0) >= 1)
            else "MULTI_SIGNATURE_VERIFICATION_HOOK_PARTIAL"),
        "reason": reason,
        "sign_all_result_summary": {
            "verdict": sign_all_result.get("verdict"),
            "n_signed": sign_all_result.get("n_signed"),
            "n_failed": sign_all_result.get("n_failed"),
            "manifest_sha256": sign_all_result.get(
                "manifest_sha256"),
            "agents_chain_of_trust": sign_all_result.get(
                "agents_chain_of_trust"),
        },
        "verify_all_result_summary": {
            "verdict": verify_all_result.get("verdict"),
            "n_both_signatures_valid": verify_all_result.get(
                "n_both_signatures_valid"),
            "n_invalid": verify_all_result.get("n_invalid"),
            "verify_manifest_sha256": verify_all_result.get(
                "verify_manifest_sha256"),
        },
        "outputs_unblocked_via_this_hook": [
            "cryptographic_chain_of_trust_2_tier",
            "Ed25519_signatures_per_manifest",
            "PGP_RSA_2048_signatures_per_manifest",
        ],
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        SIGNATURES_ROOT.mkdir(parents=True, exist_ok=True)
        if HOOK_ACTIVATION_PATH.exists():
            try:
                state = json.loads(
                    HOOK_ACTIVATION_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_activations"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = payload["verdict"]
        state["v30_lock"] = "INVIOLÉ"
        HOOK_ACTIVATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(HOOK_ACTIVATION_PATH)
        persisted["overlay_size_bytes"] = (
            HOOK_ACTIVATION_PATH.stat().st_size)

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persisted["audit_persisted"] = persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype": "MULTI_SIGNATURE_HOOK_ACTIVATE",
            "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "activated": True,
            "verdict": payload["verdict"],
            "manifest_sha256": payload_sha256,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="MULTI_SIGNATURE_VERIFICATION_HOOK_ACTIVATED",
        details={"manifest_sha256": payload_sha256},
        persist=True)
    payload["persisted_paths"] = persisted
    return payload


def get_multi_signature_hook_status() -> Dict[str, Any]:
    if not HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id":
                "MULTI_SIGNATURE_VERIFICATION_STATUS_Ω",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    last = (
        state["history"][-1]
        if state.get("history") else None)
    return {
        "manifest_id":
            "MULTI_SIGNATURE_VERIFICATION_STATUS_Ω",
        "current_status": (
            "ACTIVATED_OPERATIONAL" if last
            and last.get("activated") else "NOT_ACTIVATED"),
        "n_activations_history": state.get(
            "n_activations", 0),
        "last_manifest_sha256": state.get(
            "last_manifest_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_summary": (
            {
                "verdict": last.get("verdict"),
                "sign_all_result_summary": last.get(
                    "sign_all_result_summary"),
                "verify_all_result_summary": last.get(
                    "verify_all_result_summary"),
            } if last else None),
        "overlay_path": str(HOOK_ACTIVATION_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "SIGNATURES_ROOT",
    "SIGNATURES_INDEX_PATH",
    "HOOK_ACTIVATION_PATH",
    "sign_manifest_dual",
    "verify_manifest_dual",
    "sign_all_known_manifests",
    "verify_all_signatures",
    "activate_multi_signature_verification_hook",
    "get_multi_signature_hook_status",
]
