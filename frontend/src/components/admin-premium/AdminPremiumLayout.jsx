/**
 * AdminPremiumLayout.jsx — P21 doctrinal admin shell + auth guard
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Layout commun pour /admin/bce-4x-premium/* :
 *  - Sidebar navigation (6 sections)
 *  - Auth guard via X-Commandant-Token (anti-générique : POST GET status réel)
 *  - Header doctrinal
 * V30_LOCK : INVIOLÉ.
 * ═══════════════════════════════════════════════════════════════
 */
import React, { useEffect, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  Anchor, FileText, BookOpen, MapPin, BarChart3, ShieldCheck,
  LogOut, Lock, AlertTriangle,
} from 'lucide-react';
import {
  getCommandantToken, setCommandantToken, clearCommandantToken,
  validationStatus,
} from '@/lib/bce4xApi';

const NAV_ITEMS = [
  { to: '/admin/bce-4x-premium/visualizer', label: 'Visualizer 18',  icon: BarChart3, code: 'P18' },
  { to: '/admin/bce-4x-premium/territoire', label: 'Rapports Ω',     icon: FileText,  code: 'P15' },
  { to: '/admin/bce-4x-premium/waypoint',   label: 'Field Guides',   icon: MapPin,    code: 'P17' },
  { to: '/admin/bce-4x-premium/manual',     label: 'Manuel Couches', icon: BookOpen,  code: 'P18' },
  { to: '/admin/bce-4x-premium/merkle',     label: 'Merkle Audit',   icon: Anchor,    code: 'P14' },
  { to: '/admin/bce-4x-premium/validation', label: 'Validations',    icon: ShieldCheck, code: 'P22' },
];

const AdminPremiumLayout = () => {
  const [token, setTokenLocal] = useState(getCommandantToken());
  const [authChecked, setAuthChecked] = useState(false);
  const [authOk, setAuthOk] = useState(false);
  const [authError, setAuthError] = useState('');
  const navigate = useNavigate();

  const verify = async (candidate) => {
    if (!candidate) {
      setAuthOk(false);
      setAuthChecked(true);
      return;
    }
    setCommandantToken(candidate);
    // Anti-générique : POST réel sur endpoint protégé via tester un autre POST
    // mais pour ne pas muter, on fait un petit GET status (public) puis on
    // tente une activation idempotente du messaging hook (POST protégé) pour
    // valider le token. Si 401 → token rejeté.
    try {
      const res = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/v30/super-masters/messaging-engine-channel-hook-activate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Commandant-Token': candidate,
          },
          body: JSON.stringify({ persist: false }),
        },
      );
      if (res.status === 200) {
        setAuthOk(true);
        setAuthError('');
      } else if (res.status === 401) {
        setAuthOk(false);
        setAuthError('TOKEN_REJETÉ_PAR_SERVEUR');
      } else {
        // 412/500 etc considérés comme "token accepté mais autre erreur"
        setAuthOk(true);
        setAuthError(`SERVEUR_ALERTE_HTTP_${res.status}`);
      }
    } catch (e) {
      setAuthOk(false);
      setAuthError(`NETWORK_ERROR::${e.message}`);
    } finally {
      setAuthChecked(true);
    }
  };

  useEffect(() => {
    verify(token);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSubmitToken = async (e) => {
    e.preventDefault();
    const v = e.target.elements.token.value.trim();
    setTokenLocal(v);
    setAuthChecked(false);
    await verify(v);
  };

  const onLogout = () => {
    clearCommandantToken();
    setTokenLocal('');
    setAuthOk(false);
    setAuthChecked(true);
    navigate('/admin/bce-4x-premium');
  };

  if (!authChecked) {
    return (
      <div
        data-testid="admin-premium-loading"
        style={{
          minHeight: '100vh',
          background: '#0F1419',
          color: '#D4A017',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'Georgia, serif',
        }}
      >
        Vérification token Commandant…
      </div>
    );
  }

  if (!authOk) {
    return (
      <div
        data-testid="admin-premium-auth-screen"
        style={{
          minHeight: '100vh',
          background:
            'radial-gradient(circle at 30% 20%, #1d2330 0%, #0F1419 60%)',
          color: '#E8E4D9',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'Georgia, serif',
          padding: 24,
        }}
      >
        <form
          onSubmit={onSubmitToken}
          data-testid="admin-premium-auth-form"
          style={{
            background: 'rgba(15,23,42,0.95)',
            border: '1px solid rgba(212,160,23,0.4)',
            borderRadius: 12,
            padding: 32,
            width: 420,
            maxWidth: '100%',
            boxShadow: '0 24px 64px rgba(0,0,0,0.6)',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              marginBottom: 16,
            }}
          >
            <Lock size={22} color="#D4A017" />
            <h1
              style={{
                color: '#D4A017',
                margin: 0,
                fontSize: 18,
                fontWeight: 800,
                letterSpacing: 2,
              }}
            >
              ADMIN PREMIUM · BCE-4X
            </h1>
          </div>
          <p style={{ fontSize: 13, opacity: 0.8, lineHeight: 1.6 }}>
            Saisir le <code>X-Commandant-Token</code> doctrinal pour accéder
            aux 6 panneaux institutionnels.
          </p>
          <input
            name="token"
            type="password"
            placeholder="X-Commandant-Token"
            data-testid="admin-premium-auth-input"
            defaultValue={token}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: 6,
              background: '#0F1419',
              border: '1px solid rgba(212,160,23,0.4)',
              color: '#E8E4D9',
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 13,
              marginTop: 12,
            }}
          />
          {authError && (
            <div
              data-testid="admin-premium-auth-error"
              style={{
                marginTop: 10,
                padding: '8px 10px',
                background: 'rgba(220,38,38,0.15)',
                border: '1px solid rgba(220,38,38,0.4)',
                borderRadius: 6,
                fontSize: 12,
                color: '#FCA5A5',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <AlertTriangle size={14} /> {authError}
            </div>
          )}
          <button
            type="submit"
            data-testid="admin-premium-auth-submit"
            style={{
              marginTop: 16,
              width: '100%',
              padding: '10px',
              background: '#D4A017',
              border: 'none',
              borderRadius: 6,
              color: '#0F1419',
              fontWeight: 800,
              letterSpacing: 1,
              cursor: 'pointer',
            }}
          >
            DÉVERROUILLER
          </button>
          <p
            style={{
              fontSize: 10,
              opacity: 0.5,
              marginTop: 14,
              fontFamily: 'JetBrains Mono, monospace',
            }}
          >
            V30_LOCK · ANTI-GÉNÉRIQUE STRICT · COMMANDANT STEEVE-MAX
          </p>
        </form>
      </div>
    );
  }

  // Authenticated layout
  return (
    <div
      data-testid="admin-premium-layout"
      style={{
        minHeight: '100vh',
        background: '#0F1419',
        color: '#E8E4D9',
        display: 'flex',
        fontFamily: 'Georgia, serif',
      }}
    >
      <aside
        style={{
          width: 240,
          background: 'rgba(13,20,30,0.95)',
          borderRight: '1px solid rgba(212,160,23,0.2)',
          padding: '20px 14px',
          flexShrink: 0,
        }}
      >
        <div style={{ marginBottom: 28 }}>
          <h2
            style={{
              color: '#D4A017',
              fontSize: 14,
              fontWeight: 800,
              letterSpacing: 2,
              margin: 0,
            }}
          >
            BCE-4X
          </h2>
          <p
            style={{
              fontSize: 9,
              opacity: 0.6,
              fontFamily: 'JetBrains Mono, monospace',
              margin: '2px 0 0',
            }}
          >
            ADMIN PREMIUM Ω
          </p>
        </div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {NAV_ITEMS.map((it) => {
            const Icon = it.icon;
            return (
              <NavLink
                key={it.to}
                to={it.to}
                data-testid={`admin-premium-nav-${it.code.toLowerCase()}`}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 10px',
                  borderRadius: 6,
                  fontSize: 12,
                  fontWeight: isActive ? 700 : 500,
                  textDecoration: 'none',
                  background: isActive
                    ? 'rgba(212,160,23,0.18)'
                    : 'transparent',
                  color: isActive ? '#D4A017' : '#E8E4D9',
                  borderLeft: isActive
                    ? '3px solid #D4A017'
                    : '3px solid transparent',
                  transition: 'background 0.18s',
                })}
              >
                <Icon size={14} />
                <span>{it.label}</span>
                <span
                  style={{
                    marginLeft: 'auto',
                    fontSize: 8,
                    opacity: 0.6,
                    fontFamily: 'JetBrains Mono, monospace',
                  }}
                >
                  {it.code}
                </span>
              </NavLink>
            );
          })}
        </nav>
        <button
          onClick={onLogout}
          data-testid="admin-premium-logout"
          style={{
            marginTop: 28,
            width: '100%',
            padding: '8px 10px',
            background: 'transparent',
            border: '1px solid rgba(220,38,38,0.4)',
            borderRadius: 6,
            color: '#FCA5A5',
            fontSize: 11,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 6,
          }}
        >
          <LogOut size={12} /> Déconnexion
        </button>
      </aside>
      <main
        style={{
          flex: 1,
          padding: 24,
          overflowX: 'hidden',
          maxWidth: '100%',
        }}
        data-testid="admin-premium-main"
      >
        <Outlet />
      </main>
    </div>
  );
};

export default AdminPremiumLayout;
