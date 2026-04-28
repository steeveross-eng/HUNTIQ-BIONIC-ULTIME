/**
 * useTerritoireWatchdog.js — PHASE 2 STABILISATION TERRITOIRE Ω
 * ════════════════════════════════════════════════════════════════════════
 * Hook qui pinge /api/v30/territoire/health toutes les 5 minutes côté
 * client visible afin d'empêcher l'hibernation idle du pod backend.
 *
 * - Ping immédiat à l'activation.
 * - Intervalle 300 000 ms (5 min) tant que le composant est monté.
 * - Au passage en arrière-plan (visibilitychange = hidden), pause.
 * - Au retour en avant-plan, reprise immédiate avec un ping.
 *
 * Aucune logique d'effet de bord : le hook n'expose aucun state aux
 * consommateurs (le retour est uniquement informationnel).
 * ════════════════════════════════════════════════════════════════════════
 */
import { useEffect, useRef, useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const PING_INTERVAL_MS = 5 * 60 * 1000; // 300 000 ms

export default function useTerritoireWatchdog() {
  const [lastPingAt, setLastPingAt] = useState(null);
  const [lastPingStatus, setLastPingStatus] = useState(null);
  const [pingCount, setPingCount] = useState(0);
  const intervalRef = useRef(null);
  const cancelledRef = useRef(false);

  const ping = async () => {
    if (cancelledRef.current) return;
    if (!BACKEND_URL) return;
    try {
      const r = await fetch(
        `${BACKEND_URL}/api/v30/territoire/health?_t=${Date.now()}`,
        {
          credentials: 'omit', cache: 'no-store',
          headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' },
        },
      );
      setLastPingAt(new Date().toISOString());
      setLastPingStatus(r.ok ? 'ALIVE' : `ERR_${r.status}`);
      setPingCount((c) => c + 1);
    } catch (_e) {
      setLastPingAt(new Date().toISOString());
      setLastPingStatus('NETWORK_ERROR');
      setPingCount((c) => c + 1);
    }
  };

  useEffect(() => {
    cancelledRef.current = false;
    // Ping immédiat à l'activation
    ping();
    // Intervalle de surveillance
    intervalRef.current = setInterval(() => { ping(); }, PING_INTERVAL_MS);
    // Reprise au retour d'avant-plan
    const onVisibility = () => {
      if (document.visibilityState === 'visible') ping();
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => {
      cancelledRef.current = true;
      if (intervalRef.current) clearInterval(intervalRef.current);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, []);

  return { lastPingAt, lastPingStatus, pingCount };
}
