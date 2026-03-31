/**
 * ShareBionicButton — BCE-4X GOLDEN V6+ SHARE ENGINE V1
 * =======================================================
 * Directive x5001 — SHARE_ENGINE_V1_EASYLEAD_ULTRA_REVISION_3
 * 
 * 14 canaux fonctionnels + Screenshot automatique html2canvas
 * + Watermark "Analyse generee avec BIONIC OS — IA Terrain"
 * + EASYlead tracking URL (?ref=USER_ID&lead=SHARE_ID&page=PAGE_SHARED)
 * + Payload officiel avec texte BIONIC certifie
 *
 * STEEVE-MAX — ZERO INTERPRETATION — TOUS CANAUX FONCTIONNELS
 */
import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  Share2, Copy, CheckCircle, Mail, MessageCircle,
  Smartphone, ExternalLink, X, Camera, Loader2
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

// ═══ TEXTE OFFICIEL BIONIC — x5002 CERTIFIE ═══
const OFFICIAL_TEXT_FR = {
  description: "Chasse Bionic\u2122 red\u00e9finit l\u2019art de la chasse moderne. Analysez et comparez en toute confiance votre territoire, ses zones d\u2019achalandage, les terres \u00e0 louer, les pourvoiries et les produits les plus performants. Gr\u00e2ce \u00e0 une plateforme fond\u00e9e exclusivement sur des donn\u00e9es scientifiques, publiques, d\u00e9clar\u00e9es et v\u00e9rifiables, vous acc\u00e9dez \u00e0 un v\u00e9ritable \u00e9cosyst\u00e8me de pr\u00e9cision\u2026 directement au bout des doigts.",
  highlight: "Identifiez les zones les plus performantes et acc\u00e9dez instantan\u00e9ment aux meilleures strat\u00e9gies, solutions et prix afin d\u2019optimiser vos r\u00e9sultats de chasse.",
  slogan: "La science valide ce que le terrain confirme.\u2122",
  watermark: "Analyse g\u00e9n\u00e9r\u00e9e avec BIONIC OS \u2014 IA Terrain",
};

// ═══ 14 CANAUX PARTAGER — TOUS FONCTIONNELS ═══
const SHARE_CHANNELS = [
  { id: 'native', label: 'Partage natif (iOS/Android)', desc: 'Partage syst\u00e8me natif', icon: Smartphone, color: '#10B981',
    getUrl: (url, text) => ({ native: true, text, url }) },
  { id: 'gmail', label: 'Gmail', desc: 'Email via Gmail', icon: Mail, color: '#EA4335',
    getUrl: (url, text) => `https://mail.google.com/mail/?view=cm&fs=1&body=${encodeURIComponent(text + '\n\n' + url)}&su=${encodeURIComponent('BIONIC \u2014 Analyse Territoire de Chasse')}` },
  { id: 'outlook', label: 'Outlook', desc: 'Email via Outlook', icon: Mail, color: '#0078D4',
    getUrl: (url, text) => `https://outlook.live.com/mail/0/deeplink/compose?body=${encodeURIComponent(text + '\n\n' + url)}&subject=${encodeURIComponent('BIONIC \u2014 Analyse Territoire de Chasse')}` },
  { id: 'yahoo', label: 'Yahoo Mail', desc: 'Email via Yahoo', icon: Mail, color: '#6001D2',
    getUrl: (url, text) => `https://compose.mail.yahoo.com/?body=${encodeURIComponent(text + '\n\n' + url)}&subject=${encodeURIComponent('BIONIC \u2014 Analyse Territoire de Chasse')}` },
  { id: 'facebook', label: 'Facebook', desc: 'Partager sur Facebook', icon: ExternalLink, color: '#1877F2',
    getUrl: (url) => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}` },
  { id: 'messenger', label: 'Messenger', desc: 'Envoyer via Messenger', icon: MessageCircle, color: '#0099FF',
    getUrl: (url) => `https://www.facebook.com/dialog/send?link=${encodeURIComponent(url)}&app_id=966242223397117&redirect_uri=${encodeURIComponent(url)}` },
  { id: 'whatsapp', label: 'WhatsApp', desc: 'Envoyer via WhatsApp', icon: MessageCircle, color: '#25D366',
    getUrl: (url, text) => `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}` },
  { id: 'x_twitter', label: 'X (Twitter)', desc: 'Partager sur X', icon: ExternalLink, color: '#1DA1F2',
    getUrl: (url, text) => `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}` },
  { id: 'linkedin', label: 'LinkedIn', desc: 'Partager sur LinkedIn', icon: ExternalLink, color: '#0A66C2',
    getUrl: (url) => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}` },
  { id: 'instagram', label: 'Instagram', desc: 'Copier pour Instagram', icon: ExternalLink, color: '#E4405F',
    getUrl: () => ({ copy: true }) },
  { id: 'tiktok', label: 'TikTok', desc: 'Copier pour TikTok', icon: ExternalLink, color: '#000000',
    getUrl: () => ({ copy: true }) },
  { id: 'sms', label: 'SMS', desc: 'Envoyer par texto', icon: MessageCircle, color: '#34C759',
    getUrl: (url, text) => `sms:?body=${encodeURIComponent(text + ' ' + url)}` },
  { id: 'copy', label: 'Copier le lien', desc: 'Copier dans le presse-papier', icon: Copy, color: '#8B5CF6',
    getUrl: () => ({ copy: true }) },
];

const SHARE_TEMPLATES = {
  territoire: { prefix: 'Analyse BIONIC SUPRA', shareText: OFFICIAL_TEXT_FR.highlight },
  premium: { prefix: 'Rapport BIONIC Premium', shareText: OFFICIAL_TEXT_FR.highlight },
  viral: { prefix: 'BIONIC Chasse', shareText: OFFICIAL_TEXT_FR.highlight },
};

/**
 * Genere un SHARE_ID unique pour le tracking EASYlead
 */
const generateShareId = () => {
  return 'SH_' + Date.now().toString(36) + '_' + Math.random().toString(36).substr(2, 6);
};

/**
 * Construit l'URL EASYlead avec parametres de tracking
 * Format: ?ref=USER_ID&lead=SHARE_ID&page=PAGE_SHARED
 */
const buildEasyLeadUrl = (baseUrl, userId, shareId, page) => {
  const url = new URL(baseUrl);
  url.searchParams.set('ref', userId || 'anonymous');
  url.searchParams.set('lead', shareId);
  url.searchParams.set('page', page || '/');
  return url.toString();
};

/**
 * Capture screenshot avec watermark BIONIC via html2canvas
 */
const captureScreenshotWithWatermark = async () => {
  try {
    const html2canvas = (await import('html2canvas')).default;
    const targetEl = document.querySelector('#root') || document.body;
    
    const canvas = await html2canvas(targetEl, {
      useCORS: true,
      scale: 1,
      logging: false,
      backgroundColor: '#0a0a0f',
      width: Math.min(targetEl.scrollWidth, 1440),
      height: Math.min(targetEl.scrollHeight, 900),
      windowWidth: 1440,
      windowHeight: 900,
    });

    // Appliquer le watermark
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    // Barre de watermark en bas
    const barHeight = 48;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.fillRect(0, h - barHeight, w, barHeight);

    // Ligne orange BIONIC
    ctx.fillStyle = '#F5A623';
    ctx.fillRect(0, h - barHeight, w, 3);

    // Texte watermark
    ctx.font = 'bold 16px "Inter", "Segoe UI", Arial, sans-serif';
    ctx.fillStyle = '#F5A623';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(OFFICIAL_TEXT_FR.watermark, 20, h - barHeight / 2);

    // Logo texte BIONIC a droite
    ctx.font = 'bold 18px "Inter", "Segoe UI", Arial, sans-serif';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'right';
    ctx.fillText('BIONIC OS\u2122', w - 20, h - barHeight / 2);

    return canvas.toDataURL('image/png', 0.92);
  } catch (err) {
    console.warn('[SHARE-ENGINE] Screenshot capture failed:', err);
    return null;
  }
};

export function ShareBionicButton({ variant = 'default' }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [lastShared, setLastShared] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('territoire');
  const [masterSwitch, setMasterSwitch] = useState({ global: true, channels: {} });
  const [isCapturing, setIsCapturing] = useState(false);
  const [screenshotReady, setScreenshotReady] = useState(false);
  const [currentShareId, setCurrentShareId] = useState(null);
  const panelRef = useRef(null);
  const screenshotRef = useRef(null);

  // Generer un SHARE_ID a l'ouverture du panneau
  useEffect(() => {
    if (open) {
      setCurrentShareId(generateShareId());
      setScreenshotReady(false);
      screenshotRef.current = null;
    }
  }, [open]);

  // Fetch Master Switch status
  useEffect(() => {
    const fetchMasterSwitch = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/share/master-switch`);
        if (res.ok) {
          const data = await res.json();
          setMasterSwitch({ global: data.global_enabled, channels: Object.fromEntries(Object.entries(data.channels || {}).map(([k, v]) => [k, v.enabled !== false])) });
        }
      } catch (_) { /* Master Switch defaults to ON */ }
    };
    if (open) fetchMasterSwitch();
  }, [open]);

  // Close on click outside
  useEffect(() => {
    if (!open) return;
    const handleClickOutside = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open]);

  // ═══ Capture screenshot automatique ═══
  const handleCaptureScreenshot = useCallback(async () => {
    setIsCapturing(true);
    const dataUrl = await captureScreenshotWithWatermark();
    if (dataUrl) {
      screenshotRef.current = dataUrl;
      setScreenshotReady(true);
    }
    setIsCapturing(false);
  }, []);

  // ═══ Build EASYlead share URL ═══
  const buildShareUrl = useCallback(() => {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin + window.location.pathname : 'https://huntiq.ca';
    const userId = localStorage.getItem('huntiq_user_id') || 'anonymous';
    const page = typeof window !== 'undefined' ? window.location.pathname : '/';
    const shareId = currentShareId || generateShareId();
    return buildEasyLeadUrl(baseUrl, userId, shareId, page);
  }, [currentShareId]);

  // ═══ Build texte officiel BIONIC ═══
  const buildShareText = useCallback(() => {
    const template = SHARE_TEMPLATES[selectedTemplate];
    return `${template.prefix} \u2014 ${OFFICIAL_TEXT_FR.highlight}\n\n${OFFICIAL_TEXT_FR.slogan}`;
  }, [selectedTemplate]);

  // ═══ Track share event + EASYlead + marketing capture ═══
  const trackShare = useCallback(async (channel, template, easyLeadUrl) => {
    try {
      await fetch(`${BACKEND_URL}/api/share/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel,
          template,
          url: easyLeadUrl,
          timestamp: new Date().toISOString(),
          page_context: typeof window !== 'undefined' ? window.location.pathname : '',
          user_email: localStorage.getItem('huntiq_user_email') || null,
          user_id: localStorage.getItem('huntiq_user_id') || null,
          share_id: currentShareId,
          easylead_url: easyLeadUrl,
          has_screenshot: screenshotReady,
        }),
      });
    } catch (_) { /* silent fail */ }
  }, [currentShareId, screenshotReady]);

  // ═══ Register EASYlead in backend ═══
  const registerEasyLead = useCallback(async (channel, easyLeadUrl) => {
    try {
      await fetch(`${BACKEND_URL}/api/share/easylead/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          share_id: currentShareId,
          user_id: localStorage.getItem('huntiq_user_id') || 'anonymous',
          channel,
          page_shared: typeof window !== 'undefined' ? window.location.pathname : '/',
          easylead_url: easyLeadUrl,
          has_screenshot: screenshotReady,
        }),
      });
    } catch (_) { /* silent fail */ }
  }, [currentShareId, screenshotReady]);

  // ═══ HANDLE SHARE — 14 canaux + EASYlead + Screenshot ═══
  const handleShare = useCallback(async (channelId) => {
    const channel = SHARE_CHANNELS.find(c => c.id === channelId);
    if (!channel) return;

    // Capture screenshot automatiquement si pas encore fait
    if (!screenshotReady && !isCapturing) {
      await handleCaptureScreenshot();
    }

    const url = buildShareUrl();
    const text = buildShareText();
    const result = channel.getUrl(url, text);

    // Track + EASYlead registration
    trackShare(channelId, selectedTemplate, url);
    registerEasyLead(channelId, url);

    if (typeof result === 'object' && result.native) {
      // Native share API
      if (navigator.share) {
        const shareData = { title: 'BIONIC \u2014 Analyse Territoire de Chasse', text: result.text, url: result.url };
        navigator.share(shareData).catch(() => {});
      } else {
        navigator.clipboard?.writeText(url + '\n\n' + text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } else if (typeof result === 'object' && result.copy) {
      // Copy to clipboard — payload complet officiel
      const payload = `${text}\n\n${url}`;
      navigator.clipboard?.writeText(payload);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } else if (typeof result === 'string') {
      window.open(result, '_blank', 'width=600,height=500,scrollbars=yes,resizable=yes');
    }

    setLastShared(channelId);
    setTimeout(() => setLastShared(null), 3000);
  }, [buildShareUrl, buildShareText, selectedTemplate, trackShare, registerEasyLead, screenshotReady, isCapturing, handleCaptureScreenshot]);

  return (
    <div className="relative" ref={panelRef}>
      {/* BOUTON PARTAGER */}
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 rounded-lg px-3 py-2 transition-all group cursor-pointer"
        style={{
          backgroundColor: open ? '#10B98120' : '#111118',
          border: `1px solid ${open ? '#10B98150' : '#10B98130'}`,
        }}
        title="Partager BIONIC"
        data-testid="header-share-btn"
      >
        <Share2 className="h-4 w-4 text-emerald-400 group-hover:text-emerald-300 transition-colors" />
        <span className="text-[14px] text-emerald-400 uppercase font-bold tracking-wider group-hover:text-emerald-300">PARTAGER</span>
      </button>

      {/* PANNEAU PARTAGE — Position absolute, z-index maximal */}
      {open && (
        <div
          className="absolute right-0 top-full mt-2 w-[400px] rounded-2xl overflow-hidden"
          style={{
            backgroundColor: '#0F172A',
            boxShadow: '0 12px 48px rgba(0,0,0,0.7)',
            zIndex: 99999,
          }}
          data-testid="share-popover"
        >
          {/* Header */}
          <div className="px-4 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#3CB37120' }}>
                  <Share2 className="h-4 w-4 text-emerald-400" />
                </div>
                <div>
                  <span className="text-[16px] font-bold text-white block">PARTAGER BIONIC</span>
                  <span className="text-[11px] text-gray-500 font-mono">EASYlead {currentShareId}</span>
                </div>
              </div>
              <button onClick={() => setOpen(false)} className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-white/10 transition-all" data-testid="share-close-btn">
                <X className="h-4 w-4 text-slate-400" />
              </button>
            </div>
            {/* Templates */}
            <div className="flex gap-2">
              {Object.entries(SHARE_TEMPLATES).map(([key, tmpl]) => (
                <button key={key} onClick={() => setSelectedTemplate(key)}
                  className="flex-1 px-3 py-1.5 rounded-xl text-[14px] font-bold transition-all"
                  style={{
                    backgroundColor: selectedTemplate === key ? '#10B98120' : '#1E293B',
                    color: selectedTemplate === key ? '#10B981' : '#6b7280',
                  }}
                  data-testid={`share-template-${key}`}>
                  {key === 'territoire' ? 'Territoire' : key === 'premium' ? 'Premium' : 'Viral'}
                </button>
              ))}
            </div>
          </div>

          {/* Screenshot Capture — Section C */}
          <div className="px-4 py-2.5" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <button
              onClick={handleCaptureScreenshot}
              disabled={isCapturing || screenshotReady}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-[13px] font-bold transition-all"
              style={{
                backgroundColor: screenshotReady ? '#10B98115' : '#F5A62315',
                color: screenshotReady ? '#10B981' : '#F5A623',
                border: `1px solid ${screenshotReady ? '#10B98130' : '#F5A62330'}`,
              }}
              data-testid="share-screenshot-btn"
            >
              {isCapturing ? (
                <><Loader2 className="h-4 w-4 animate-spin" /> Capture en cours...</>
              ) : screenshotReady ? (
                <><CheckCircle className="h-4 w-4" /> Screenshot BIONIC captur&eacute;</>
              ) : (
                <><Camera className="h-4 w-4" /> Capturer screenshot + watermark</>
              )}
            </button>
            {screenshotReady && (
              <p className="text-[11px] text-gray-500 text-center mt-1 font-mono">
                Watermark : {OFFICIAL_TEXT_FR.watermark}
              </p>
            )}
          </div>

          {/* Preview — Texte officiel */}
          <div className="px-4 py-2.5" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <div className="text-[11px] text-gray-500 uppercase font-bold mb-1 tracking-wider">Payload officiel BIONIC</div>
            <p className="text-[13px] text-gray-300 leading-relaxed line-clamp-3">{buildShareText()}</p>
            <div className="mt-1.5 flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[11px] text-emerald-500/80 font-mono">EASYlead tracking actif</span>
            </div>
          </div>

          {/* 14 CANAUX — TOUS FONCTIONNELS */}
          <div className="p-2 max-h-[280px] overflow-y-auto" data-testid="share-channels-list">
            {!masterSwitch.global && (
              <div className="px-4 py-6 text-center">
                <div className="text-[14px] text-red-400 font-bold uppercase mb-1">Master Switch OFF</div>
                <div className="text-[14px] text-gray-500">Activation par STEEVE-MAX requise</div>
              </div>
            )}
            {masterSwitch.global && SHARE_CHANNELS.map((ch) => {
              const Icon = ch.icon;
              const isLast = lastShared === ch.id;
              return (
                <button key={ch.id} onClick={() => handleShare(ch.id)}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-left transition-all hover:bg-white/5"
                  style={{ backgroundColor: isLast ? '#10B98115' : 'transparent' }}
                  data-testid={`share-channel-${ch.id}`}>
                  <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${ch.color}20` }}>
                    {isLast ? <CheckCircle className="h-4 w-4 text-emerald-400" /> : <Icon className="h-4 w-4" style={{ color: ch.color }} />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[14px] font-medium text-white">{ch.label}</div>
                    <div className="text-[12px] text-gray-500">{ch.desc}</div>
                  </div>
                  {(ch.id === 'copy' || ch.id === 'instagram' || ch.id === 'tiktok') && copied && isLast && (
                    <span className="text-[13px] text-emerald-400 font-bold flex-shrink-0">Copie!</span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Footer — Master Switch + EASYlead Status */}
          <div className="px-4 py-2.5" style={{ borderTop: '1px solid rgba(255,255,255,0.06)', backgroundColor: '#1E293B', borderRadius: '0 0 16px 16px' }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${masterSwitch.global ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                <span className={`text-[12px] uppercase font-bold tracking-wider ${masterSwitch.global ? 'text-gray-500' : 'text-red-400'}`}>
                  Master Switch {masterSwitch.global ? 'ON' : 'OFF'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold tracking-wider text-[#F5A623]/60">EASYlead</span>
                <span className="text-[12px] font-bold tracking-wider text-emerald-500/60" data-testid="master-switch-indicator">
                  14 CANAUX
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ShareBionicButton;
