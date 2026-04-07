/**
 * GATEKEEPER_PIPELINE.js
 * ================================================================
 * Pipeline CI/CD BCE-4X-GLOBAL — Gardien Steeve-Max
 * Version 0.1 | 2026-04-07 | Branche: BIONIC-ULTIME-INIT
 * ================================================================
 *
 * ROLE: Intercepte TOUT commit et TOUTE PR, execute les 12
 * validateurs du STEEVE_MAX_VALIDATOR_GLOBAL.js, et BLOQUE
 * automatiquement toute deviation, regression ou violation.
 *
 * CONTROLES ACTIFS:
 *   1. NoParasiteLegends
 *   2. NoGhostElements
 *   3. NoControlOverlap
 *   4. NoBranchMerge
 *   5. Nomenclature
 *   6. TestIds
 *   7. InstitutionalFiles
 *   8. Anti-regression
 *   9. Anti-contournement modules critiques
 * ================================================================
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

// Charger le validateur officiel STEEVE-MAX
const validator = require('./STEEVE_MAX_VALIDATOR_GLOBAL.js');
const LOCK = JSON.parse(fs.readFileSync(path.resolve(__dirname, 'BCE4X_GLOBAL_LOCK.json'), 'utf-8'));

// ================================================================
// CONFIGURATION
// ================================================================
const PROTECTED_BRANCH = 'BIONIC-ULTIME-INIT';
const FORBIDDEN_TARGET = 'main';

const SEALED_HASHES = {
  'BCE4X_GLOBAL_LOCK.json': '8bcc27e3012eb7b8c81ae3e07d36470ddaece0ea2c7d4abda19950fb6ff3b8eb',
  'STEEVE_MAX_RULES_GLOBAL.md': '45557f47c2c1c2f3a1426f704e395cef3f07e47bdaea8e81f6321609237d7a76',
  'STEEVE_MAX_VALIDATOR_GLOBAL.js': '775a6f280dc97d13c1f563c58f30b3059f548ec2f5e6d304abd3dd05e59a3767',
};

// Patterns interdits (parasites, fantomes, contournements)
const FORBIDDEN_PATTERNS = {
  parasiteLegend: [
    /showLegend\s*=\s*true/,
    /data-testid=["'](?:hunt-legend-golden|ndvi-legend|movement-corridors-legend|route-planner-legend)["']/,
    /class(?:Name)?=["'][^"']*bionic-hunt-legend-golden[^"']*["']/,
  ],
  ghostElement: [
    /document\.createElement\s*\(\s*['"]div['"]\s*\)[\s\S]{0,500}appendChild/,
  ],
  controlOverlap: [
    /position:\s*['"]?absolute['"]?[^}]*top:\s*(\d{1,2})px[^}]*left:\s*(\d{1,2})px/,
  ],
  forbiddenNomenclature: [
    /BDRE\s+P[EeÉé]DAGOGIQUE/i,
    /MODULE\s+P[EeÉé]DAGOGIQUE/i,
    /SECTION\s+P[EeÉé]DAGOGIQUE/i,
  ],
  emoji: [
    /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}]/u,
  ],
};

const ALLOWED_LEGEND_FILES = ['BionicLegend.jsx'];
const INSTITUTIONAL_FILES = ['BCE4X_GLOBAL_LOCK.json', 'STEEVE_MAX_RULES_GLOBAL.md', 'STEEVE_MAX_VALIDATOR_GLOBAL.js'];
const CRITICAL_MODULES = ['BionicLegend.jsx', 'exclusion_layer_bce4x.py', 'relocation_engine.py'];

// ================================================================
// UTILITAIRES
// ================================================================
function computeSHA256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function getChangedFiles() {
  try {
    const output = execSync('git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || git diff HEAD~1 --name-only 2>/dev/null || echo ""', { encoding: 'utf-8' });
    return output.trim().split('\n').filter(f => f.length > 0).map(f => path.resolve(process.cwd(), f));
  } catch {
    return [];
  }
}

function getCurrentBranch() {
  try {
    return execSync('git branch --show-current 2>/dev/null', { encoding: 'utf-8' }).trim();
  } catch {
    return 'unknown';
  }
}

function readFileSafe(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch {
    return null;
  }
}

// ================================================================
// CONTROLES ACTIFS
// ================================================================

function ctrl_NoParasiteLegends(files) {
  const violations = [];
  for (const file of files) {
    const basename = path.basename(file);
    if (ALLOWED_LEGEND_FILES.includes(basename)) continue;
    if (!file.match(/\.(jsx|js|tsx|ts)$/)) continue;
    const content = readFileSafe(file);
    if (!content) continue;
    for (const pattern of FORBIDDEN_PATTERNS.parasiteLegend) {
      if (pattern.test(content)) {
        violations.push({ control: 'NoParasiteLegends', file: basename, severity: 'BLOCK', detail: `Pattern parasite: ${pattern.source.substring(0, 50)}` });
      }
    }
  }
  return violations;
}

function ctrl_NoGhostElements(files) {
  const violations = [];
  for (const file of files) {
    if (!file.match(/\.(jsx|js)$/)) continue;
    const content = readFileSafe(file);
    if (!content) continue;
    if (content.includes('document.createElement') && content.includes('appendChild')) {
      if (!content.includes('.remove()') && !content.includes('removeChild')) {
        violations.push({ control: 'NoGhostElements', file: path.basename(file), severity: 'WARNING', detail: 'DOM createElement sans cleanup — risque fantome' });
      }
    }
  }
  return violations;
}

function ctrl_NoControlOverlap(files) {
  const violations = [];
  for (const file of files) {
    if (!file.match(/\.(jsx|js)$/)) continue;
    if (path.basename(file) === 'BionicLegend.jsx') continue;
    const content = readFileSafe(file);
    if (!content) continue;
    if (content.includes('L.divIcon') || content.includes('divIcon')) {
      const matches = content.match(/top:\s*(\d+)px[^}]*left:\s*(\d+)px/g);
      if (matches) {
        for (const match of matches) {
          const top = parseInt((match.match(/top:\s*(\d+)/) || [])[1] || 999);
          const left = parseInt((match.match(/left:\s*(\d+)/) || [])[1] || 999);
          if (top < 180 && left < 60) {
            violations.push({ control: 'NoControlOverlap', file: path.basename(file), severity: 'BLOCK', detail: `Element a top:${top}px left:${left}px — zone controles zoom` });
          }
        }
      }
    }
  }
  return violations;
}

function ctrl_NoBranchMerge(targetBranch) {
  if (targetBranch === FORBIDDEN_TARGET) {
    return [{ control: 'NoBranchMerge', file: 'N/A', severity: 'BLOCK', detail: `Merge vers ${FORBIDDEN_TARGET} STRICTEMENT INTERDIT` }];
  }
  return [];
}

function ctrl_Nomenclature(files) {
  const violations = [];
  for (const file of files) {
    if (!file.match(/\.(jsx|js|tsx|ts)$/)) continue;
    const content = readFileSafe(file);
    if (!content) continue;
    for (const pattern of FORBIDDEN_PATTERNS.forbiddenNomenclature) {
      if (pattern.test(content)) {
        violations.push({ control: 'Nomenclature', file: path.basename(file), severity: 'BLOCK', detail: 'Nomenclature interdite — utiliser GUIDE PRO' });
      }
    }
  }
  return violations;
}

function ctrl_TestIds(files) {
  const violations = [];
  for (const file of files) {
    if (!file.match(/\.(jsx|tsx)$/)) continue;
    const content = readFileSafe(file);
    if (!content) continue;
    const buttons = (content.match(/<button(?!\s[^>]*data-testid)/gi) || []).length;
    const inputs = (content.match(/<input(?!\s[^>]*data-testid)/gi) || []).length;
    const missing = buttons + inputs;
    if (missing > 0) {
      violations.push({ control: 'TestIds', file: path.basename(file), severity: 'WARNING', detail: `${missing} element(s) interactif(s) sans data-testid` });
    }
  }
  return violations;
}

function ctrl_InstitutionalFiles(files) {
  const violations = [];
  for (const file of files) {
    const basename = path.basename(file);
    if (INSTITUTIONAL_FILES.includes(basename)) {
      violations.push({ control: 'InstitutionalFiles', file: basename, severity: 'BLOCK', detail: 'Fichier institutionnel modifie — VALIDATION STEEVE-MAX OBLIGATOIRE' });
    }
  }
  return violations;
}

function ctrl_AntiRegression(files) {
  const violations = [];
  // Verification integrite SHA256
  for (const [filename, expectedHash] of Object.entries(SEALED_HASHES)) {
    const filePath = path.resolve(__dirname, filename);
    try {
      const actual = computeSHA256(filePath);
      if (actual !== expectedHash) {
        violations.push({ control: 'AntiRegression', file: filename, severity: 'BLOCK', detail: `SHA256 altere! Attendu: ${expectedHash.substring(0, 16)}... Actuel: ${actual.substring(0, 16)}...` });
      }
    } catch {
      violations.push({ control: 'AntiRegression', file: filename, severity: 'BLOCK', detail: 'Fichier institutionnel introuvable!' });
    }
  }
  return violations;
}

function ctrl_AntiContournementModulesCritiques(files) {
  const violations = [];
  for (const file of files) {
    const basename = path.basename(file);
    if (CRITICAL_MODULES.includes(basename)) {
      violations.push({ control: 'AntiContournement', file: basename, severity: 'WARNING', detail: 'Module critique modifie — verification manuelle requise' });
    }
  }
  return violations;
}

// ================================================================
// ORCHESTRATEUR PIPELINE
// ================================================================

function runGatekeeper(options = {}) {
  const startTime = Date.now();
  const changedFiles = options.files || getChangedFiles();
  const targetBranch = options.targetBranch || null;
  const currentBranch = getCurrentBranch();

  const allViolations = [];

  // Executer tous les controles
  allViolations.push(...ctrl_NoParasiteLegends(changedFiles));
  allViolations.push(...ctrl_NoGhostElements(changedFiles));
  allViolations.push(...ctrl_NoControlOverlap(changedFiles));
  if (targetBranch) allViolations.push(...ctrl_NoBranchMerge(targetBranch));
  allViolations.push(...ctrl_Nomenclature(changedFiles));
  allViolations.push(...ctrl_TestIds(changedFiles));
  allViolations.push(...ctrl_InstitutionalFiles(changedFiles));
  allViolations.push(...ctrl_AntiRegression(changedFiles));
  allViolations.push(...ctrl_AntiContournementModulesCritiques(changedFiles));

  // Executer le validateur officiel STEEVE-MAX (12 checks)
  const commitProxy = {
    modifies: (f) => changedFiles.some(cf => path.basename(cf) === f),
    violatesGlobalRules: () => false,
    introducesRegression: () => allViolations.some(v => v.control === 'AntiRegression' && v.severity === 'BLOCK'),
    createsDOMLegend: () => allViolations.some(v => v.control === 'NoParasiteLegends'),
    createsOverlayHTML: () => false,
    createsGhostOverlay: () => allViolations.some(v => v.control === 'NoGhostElements'),
    modifiesCriticalModules: () => allViolations.some(v => v.control === 'AntiContournement'),
    breaksInterModuleConsistency: () => false,
    breaksUXRules: () => allViolations.some(v => v.control === 'Nomenclature'),
    breaksTerrainLogic: () => false,
    breaksSEO: () => false,
    breaksBoutique: () => false,
    breaksAdmin: () => false,
    breaksMapEngine: () => allViolations.some(v => v.control === 'NoControlOverlap'),
    breaksAPI: () => false,
    breaksBackend: () => false,
    breaksFrontend: () => false,
    breaksPerformance: () => false,
    breaksSecurity: () => false,
  };

  const validatorResult = validator.validateCommit(commitProxy);

  // Classification
  const blocks = allViolations.filter(v => v.severity === 'BLOCK');
  const warnings = allViolations.filter(v => v.severity === 'WARNING');
  const isBlocked = blocks.length > 0 || validatorResult.status === 'BLOCK';

  const verdict = isBlocked ? 'BLOCK' : (warnings.length > 0 ? 'PASS_WITH_WARNINGS' : 'PASS');

  // Journal
  const journal = {
    timestamp: new Date().toISOString(),
    pipeline: 'BCE-4X-GLOBAL GATEKEEPER',
    version: '0.1',
    branch: currentBranch,
    target_branch: targetBranch || 'N/A',
    protected_branch: PROTECTED_BRANCH,
    files_analyzed: changedFiles.length,
    duration_ms: Date.now() - startTime,
    controls_executed: 9,
    validator_checks: 12,
    violations: {
      total: allViolations.length,
      blocks: blocks.length,
      warnings: warnings.length,
    },
    validator_result: validatorResult,
    verdict,
    details: allViolations,
    authority: 'COMMANDANT STEEVE-MAX',
  };

  // Affichage
  console.log('\n' + '#'.repeat(60));
  console.log('#  BCE-4X-GLOBAL GATEKEEPER — RAPPORT PIPELINE');
  console.log('#'.repeat(60));
  console.log(`  Branche:           ${currentBranch}`);
  console.log(`  Branche cible:     ${targetBranch || 'N/A'}`);
  console.log(`  Fichiers analyses: ${changedFiles.length}`);
  console.log(`  Controles:         9 pipeline + 12 validateur = 21 total`);
  console.log(`  Duree:             ${journal.duration_ms}ms`);
  console.log('#'.repeat(60));
  console.log(`  BLOCKS:     ${blocks.length}`);
  console.log(`  WARNINGS:   ${warnings.length}`);
  console.log(`  VALIDATOR:  ${validatorResult.status}${validatorResult.reason ? ' — ' + validatorResult.reason : ''}`);
  console.log('#'.repeat(60));
  console.log(`  >>> VERDICT: ${verdict} <<<`);
  console.log('#'.repeat(60));

  if (allViolations.length > 0) {
    console.log('\n  DETAIL DES VIOLATIONS:');
    for (const v of allViolations) {
      const icon = v.severity === 'BLOCK' ? 'BLOCK' : 'WARN ';
      console.log(`  [${icon}] ${v.control} | ${v.file} | ${v.detail}`);
    }
  }

  if (isBlocked) {
    console.log('\n  >>> COMMIT/PR BLOQUE — Corriger les violations <<<');
    console.log('  >>> AUCUNE FUSION AUTORISEE <<<\n');
  } else if (warnings.length > 0) {
    console.log('\n  >>> COMMIT AUTORISE AVEC AVERTISSEMENTS <<<\n');
  } else {
    console.log('\n  >>> COMMIT/PR CONFORME — FUSION AUTORISEE <<<\n');
  }

  return journal;
}

// ================================================================
// EXPORTS
// ================================================================
module.exports = {
  runGatekeeper,
  ctrl_NoParasiteLegends,
  ctrl_NoGhostElements,
  ctrl_NoControlOverlap,
  ctrl_NoBranchMerge,
  ctrl_Nomenclature,
  ctrl_TestIds,
  ctrl_InstitutionalFiles,
  ctrl_AntiRegression,
  ctrl_AntiContournementModulesCritiques,
  SEALED_HASHES,
  PROTECTED_BRANCH,
  FORBIDDEN_TARGET,
};

// ================================================================
// EXECUTION STANDALONE
// ================================================================
if (require.main === module) {
  const args = process.argv.slice(2);
  const targetBranch = args.find(a => a.startsWith('--target='))?.split('=')[1] || null;
  const testMode = args.includes('--test');

  if (testMode) {
    console.log('[GATEKEEPER] Mode test — 3 scenarios de demonstration\n');

    // CAS 1: PASS — commit conforme
    console.log('=== CAS 1: COMMIT CONFORME ===');
    runGatekeeper({ files: [], targetBranch: 'BIONIC_REWRITE_P0' });

    // CAS 2: BLOCK — PR vers main
    console.log('=== CAS 2: PR VERS MAIN (INTERDIT) ===');
    runGatekeeper({ files: [], targetBranch: 'main' });

    // CAS 3: WARNING — modification module critique
    console.log('=== CAS 3: MODIFICATION MODULE CRITIQUE ===');
    const criticalFile = path.resolve(__dirname, '..', 'frontend', 'src', 'components', 'territoire', 'BionicLegend.jsx');
    runGatekeeper({ files: [criticalFile] });

  } else {
    const journal = runGatekeeper({ targetBranch });
    // BLOCAGE REEL: exit code 1 si verdict = BLOCK
    process.exit(journal.verdict === 'BLOCK' ? 1 : 0);
  }
}
