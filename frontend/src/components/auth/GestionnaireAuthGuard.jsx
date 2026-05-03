/**
 * GestionnaireAuthGuard — Wrapper d'authentification ORDRE N°47
 * ════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · Ordre N°47
 *
 * Sécurise la route /gestionnaire avec le mot de passe Saturn5858*.
 * Pattern identique à AdminPremiumPage : POST /api/auth/login →
 * localStorage.gestionnaire_authenticated=true.
 *
 * data-testid principaux :
 *   · gestionnaire-auth-guard, gestionnaire-password-input
 *   · gestionnaire-login-btn, gestionnaire-logout-btn
 * ════════════════════════════════════════════════════════════════════
 */
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Lock, Shield } from "lucide-react";
import { toast } from "sonner";
import { Button } from "../ui/button";
import { Card } from "../ui/card";

const STORAGE_KEY = "gestionnaire_authenticated";

export default function GestionnaireAuthGuard({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [authError, setAuthError] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    // ─── ORDRE N°48 · MODE RESET URL — débloque caches/SW corrompus ───
    const params = new URLSearchParams(window.location.search);
    if (params.get("reset") === "1" || params.get("clear") === "1") {
      try {
        localStorage.clear();
        sessionStorage.clear();
        if ("serviceWorker" in navigator) {
          navigator.serviceWorker.getRegistrations().then((regs) => {
            regs.forEach((r) => r.unregister());
          });
        }
        if (window.caches) {
          caches.keys().then((keys) => keys.forEach((k) => caches.delete(k)));
        }
      } catch (err) {
        console.warn("[GESTIONNAIRE_RESET] partial:", err);
      }
      const url = new URL(window.location.href);
      url.searchParams.delete("reset");
      url.searchParams.delete("clear");
      window.location.replace(url.pathname + url.search);
      return;
    }
    if (localStorage.getItem(STORAGE_KEY) === "true") {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAuthError(null);
    try {
      const r = await axios.post(
        `${BACKEND_URL}/api/auth/login`,
        { email: "admin@huntiq.com", password },
        { timeout: 15000 }
      );
      if (r.data?.success) {
        localStorage.setItem(STORAGE_KEY, "true");
        setIsAuthenticated(true);
        toast.success("Accès Gestionnaire autorisé — Commandant identifié");
      } else {
        setAuthError(`Réponse inattendue: ${JSON.stringify(r.data).slice(0, 80)}`);
      }
    } catch (err) {
      let msg = "Mot de passe incorrect ou réseau indisponible";
      if (err.response) {
        msg = `HTTP ${err.response.status} · ${err.response.data?.detail || err.response.statusText}`;
      } else if (err.request) {
        msg = `Réseau injoignable · ${BACKEND_URL}`;
      }
      setAuthError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleHardReset = () => {
    window.location.href = `${window.location.pathname}?reset=1`;
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setIsAuthenticated(false);
    setPassword("");
  };

  if (!isAuthenticated) {
    return (
      <main
        className="min-h-screen bg-[#050510] flex items-center justify-center"
        data-testid="gestionnaire-auth-guard"
      >
        <Card className="w-full max-w-md bg-[#0a0a15] border-[#F5A623]/30 p-8">
          <div className="text-center mb-6">
            <Shield className="h-12 w-12 text-[#F5A623] mx-auto mb-3" />
            <h2 className="text-xl font-bold text-white">
              GESTIONNAIRE — Accès sécurisé
            </h2>
            <p className="text-gray-500 text-sm mt-1">
              BCE-4X ULTIME ABSOLU · Mot de passe Commandant requis
            </p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mot de passe Commandant"
              className="w-full bg-black border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-[#F5A623] focus:outline-none"
              data-testid="gestionnaire-password-input"
              autoComplete="current-password"
            />
            {authError && (
              <div
                className="text-xs text-red-400 bg-red-950/40 border border-red-900/60 rounded p-2 font-mono break-all"
                data-testid="gestionnaire-auth-error"
              >
                ⚠ {authError}
              </div>
            )}
            <Button
              type="submit"
              className="w-full bg-[#F5A623] text-black font-bold hover:bg-[#F5A623]/90"
              disabled={loading || !password}
              data-testid="gestionnaire-login-btn"
            >
              <Lock className="h-4 w-4 mr-2" />
              {loading ? "Connexion..." : "Se connecter"}
            </Button>
          </form>
          <div className="mt-6 pt-4 border-t border-gray-800">
            <button
              type="button"
              onClick={handleHardReset}
              className="w-full text-xs text-cyan-400/80 hover:text-cyan-300 font-mono py-2 px-3 border border-cyan-900/40 rounded hover:bg-cyan-950/20 transition-colors"
              data-testid="gestionnaire-hard-reset-btn"
              title="Vide le cache local + service workers + storage si la connexion échoue"
            >
              ⟳ Connexion bloquée ? Vider la session locale & recharger
            </button>
            <p className="text-[10px] text-gray-600 mt-3 text-center font-mono">
              ORDRE N°47 · ANTI-GÉNÉRIQUE STRICT · V30 INVIOLÉ
            </p>
            <p className="text-[10px] text-gray-700 mt-1 text-center font-mono break-all">
              {BACKEND_URL}/api/auth/login
            </p>
          </div>
        </Card>
      </main>
    );
  }

  return (
    <div data-testid="gestionnaire-authenticated-root">
      {/* Logout button toujours accessible (top-right discreet) */}
      <button
        onClick={handleLogout}
        data-testid="gestionnaire-logout-btn"
        className="fixed top-4 right-4 z-50 px-3 py-1.5 bg-black/50 hover:bg-black/80 border border-[#F5A623]/30 rounded text-xs text-[#F5A623] font-mono transition-colors"
        title="Se déconnecter du Gestionnaire"
      >
        ⏻ Déconnexion
      </button>
      {children}
    </div>
  );
}
