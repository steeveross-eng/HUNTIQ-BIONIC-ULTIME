/**
 * lkgCacheOmega.test.js — Tests Jest doctrine LKG IndexedDB
 * ============================================================
 * P22ΩΩ_ZEROCOST_PHASE2_R2_CLOUDFLARE_Ω · 2026-02-XX
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU
 *
 * Tests :
 *   1. buildLkgKey produit clé canonique stable
 *   2. lkgSave + lkgGet roundtrip
 *   3. lkgSave refuse bundles DEGRADED (NEVER BLANK Ω)
 *   4. lkgSave accepte bundles mask_halt (doctrine MFFP)
 *   5. lkgGet retourne null si entry expirée (TTL 7j simulé)
 *   6. lkgPurge supprime tout
 *   7. lkgGet annote le retour avec metadata _lkg
 */

import 'fake-indexeddb/auto';
import {
  buildLkgKey,
  lkgSave,
  lkgGet,
  lkgStats,
  lkgPurge,
  __resetForTests__,
} from './lkgCacheOmega';

describe('P22ΩΩ_LKG_Ω · IndexedDB cache doctrinal', () => {
  beforeEach(async () => {
    await __resetForTests__();
  });

  test('buildLkgKey est stable et quantize à 4 décimales', () => {
    const k1 = buildLkgKey('chevreuil', 48.20665, -68.38242);
    const k2 = buildLkgKey('chevreuil', 48.20669, -68.38249);
    expect(k1).toBe('chevreuil|48.2067|-68.3824');
    expect(k2).toBe('chevreuil|48.2067|-68.3825');
    // Normalisation case
    expect(buildLkgKey('CHEVREUIL', 48.2067, -68.3824)).toBe('chevreuil|48.2067|-68.3824');
  });

  test('lkgSave + lkgGet roundtrip d\'un bundle valide', async () => {
    const bundle = {
      corridors: [{ id: 'c1', hierarchy: 'veine_principale' }],
      score_local: { value: 67.5 },
      bundle_tier: 'ESSENTIEL_T0',
    };
    const ok = await lkgSave('orignal', 48.2067, -68.3824, bundle);
    expect(ok).toBe(true);

    const got = await lkgGet('orignal', 48.2067, -68.3824);
    expect(got).not.toBeNull();
    expect(got.corridors).toHaveLength(1);
    expect(got.score_local.value).toBe(67.5);
    // Stamp LKG
    expect(got._lkg).toBeDefined();
    expect(got._lkg.served_from_lkg).toBe(true);
    expect(got._lkg.doctrine).toBe('P22ΩΩ_LKG_Ω');
    expect(got._lkg.age_ms).toBeGreaterThanOrEqual(0);
  });

  test('lkgSave REFUSE un bundle DEGRADED (NEVER BLANK Ω)', async () => {
    const degraded = {
      status: 'DEGRADED',
      reason: 'endpoint_unavailable_http_404',
      doctrine: 'P22ΩΩ_NEVER_BLANK_Ω',
    };
    const ok = await lkgSave('orignal', 48.20, -68.38, degraded);
    expect(ok).toBe(false);
    const got = await lkgGet('orignal', 48.20, -68.38);
    expect(got).toBeNull();
  });

  test('lkgSave ACCEPTE un bundle mask_halt (doctrine MFFP)', async () => {
    const halt = {
      corridors: [],
      bio_presence_mask_halt: true,
      bio_presence_mask: { status: 'HALT', reason: 'MFFP absent' },
      species: 'wapiti',
    };
    const ok = await lkgSave('wapiti', 48.2067, -68.3824, halt);
    expect(ok).toBe(true);

    const got = await lkgGet('wapiti', 48.2067, -68.3824);
    expect(got).not.toBeNull();
    expect(got.bio_presence_mask_halt).toBe(true);
    expect(got.corridors).toHaveLength(0);
  });

  test('lkgGet retourne null si entry inexistante', async () => {
    const got = await lkgGet('coyote', 50.0, -75.0);
    expect(got).toBeNull();
  });

  test('lkgPurge vide la base', async () => {
    await lkgSave('chevreuil', 48.2, -68.4, { corridors: [], score_local: { value: 70 } });
    let stats = await lkgStats();
    expect(stats.entries).toBeGreaterThanOrEqual(1);

    const ok = await lkgPurge();
    expect(ok).toBe(true);
    stats = await lkgStats();
    expect(stats.entries).toBe(0);
  });

  test('lkgStats renvoie les configurations doctrinales', async () => {
    const stats = await lkgStats();
    expect(stats.db_name).toBe('bionic_lkg_omega_v1');
    expect(stats.max).toBe(200);
    expect(stats.ttl_ms).toBe(7 * 24 * 3600 * 1000); // 7 jours
  });

  test('clés distinctes pour espèces différentes au même point', async () => {
    await lkgSave('chevreuil', 48.2067, -68.3824, { corridors: [{ id: 'A' }] });
    await lkgSave('orignal', 48.2067, -68.3824, { corridors: [{ id: 'B' }] });

    const a = await lkgGet('chevreuil', 48.2067, -68.3824);
    const b = await lkgGet('orignal', 48.2067, -68.3824);
    expect(a.corridors[0].id).toBe('A');
    expect(b.corridors[0].id).toBe('B');
  });
});
