/**
 * STEEVE_MAX_VALIDATOR_GLOBAL.js
 * Version 0.1 — Gardien Institutionnel BCE-4X-GLOBAL
 * Statut : NON NEGOCIABLE — SCELLE
 */

module.exports = {
  
  validateCommit(commit) {
    const results = [];

    // 1 — Verification du LOCK
    results.push(this.checkLockIntegrity(commit));

    // 2 — Verification des regles globales
    results.push(this.checkGlobalRules(commit));

    // 3 — Verification anti-regression
    results.push(this.checkRegression(commit));

    // 4 — Verification anti-parasites
    results.push(this.checkParasites(commit));

    // 5 — Verification anti-fantomes
    results.push(this.checkGhosts(commit));

    // 6 — Verification des modules critiques
    results.push(this.checkCriticalModules(commit));

    // 7 — Verification inter-modules
    results.push(this.checkInterModuleConsistency(commit));

    // 8 — Verification UX globale
    results.push(this.checkUXCompliance(commit));

    // 9 — Verification BDRE/SUPRA/AFFUTS
    results.push(this.checkTerrainModules(commit));

    // 10 — Verification SEO / Boutique / Admin / Carte
    results.push(this.checkCommercialAndMarketing(commit));

    // 11 — Verification API / Backend / Frontend
    results.push(this.checkTechnicalLayers(commit));

    // 12 — Verification Performance / Securite
    results.push(this.checkPerfAndSecurity(commit));

    // Decision finale
    return this.finalDecision(results);
  },

  // ---------------------------------------------------------
  // 1 — LOCK
  // ---------------------------------------------------------
  checkLockIntegrity(commit) {
    return commit.modifies("BCE4X_GLOBAL_LOCK.json")
      ? this.block("Modification du LOCK interdite.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 2 — REGLES GLOBALES
  // ---------------------------------------------------------
  checkGlobalRules(commit) {
    return commit.violatesGlobalRules()
      ? this.block("Violation des regles globales.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 3 — ANTI-REGRESSION
  // ---------------------------------------------------------
  checkRegression(commit) {
    return commit.introducesRegression()
      ? this.block("Regression detectee.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 4 — ANTI-PARASITES
  // ---------------------------------------------------------
  checkParasites(commit) {
    return commit.createsDOMLegend() ||
           commit.createsOverlayHTML()
      ? this.block("Parasite detecte.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 5 — ANTI-FANTOMES
  // ---------------------------------------------------------
  checkGhosts(commit) {
    return commit.createsGhostOverlay()
      ? this.block("Fantome detecte.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 6 — MODULES CRITIQUES
  // ---------------------------------------------------------
  checkCriticalModules(commit) {
    return commit.modifiesCriticalModules()
      ? this.block("Modification non autorisee d'un module critique.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 7 — INTER-MODULES
  // ---------------------------------------------------------
  checkInterModuleConsistency(commit) {
    return commit.breaksInterModuleConsistency()
      ? this.block("Incoherence inter-modules.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 8 — UX
  // ---------------------------------------------------------
  checkUXCompliance(commit) {
    return commit.breaksUXRules()
      ? this.block("Violation des normes UX globales.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 9 — BDRE / SUPRA / AFFUTS
  // ---------------------------------------------------------
  checkTerrainModules(commit) {
    return commit.breaksTerrainLogic()
      ? this.block("Violation BDRE/SUPRA/AFFUTS.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 10 — SEO / Boutique / Admin / Carte
  // ---------------------------------------------------------
  checkCommercialAndMarketing(commit) {
    return commit.breaksSEO() ||
           commit.breaksBoutique() ||
           commit.breaksAdmin() ||
           commit.breaksMapEngine()
      ? this.block("Violation SEO/Boutique/Admin/Carte.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 11 — API / Backend / Frontend
  // ---------------------------------------------------------
  checkTechnicalLayers(commit) {
    return commit.breaksAPI() ||
           commit.breaksBackend() ||
           commit.breaksFrontend()
      ? this.block("Violation API/Backend/Frontend.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // 12 — PERFORMANCE / SECURITE
  // ---------------------------------------------------------
  checkPerfAndSecurity(commit) {
    return commit.breaksPerformance() ||
           commit.breaksSecurity()
      ? this.block("Violation Performance/Securite.")
      : this.pass();
  },

  // ---------------------------------------------------------
  // UTILITAIRES
  // ---------------------------------------------------------
  block(reason) {
    return { status: "BLOCK", reason };
  },

  pass() {
    return { status: "PASS" };
  },

  finalDecision(results) {
    const failure = results.find(r => r.status === "BLOCK");
    return failure || { status: "PASS" };
  }
};
