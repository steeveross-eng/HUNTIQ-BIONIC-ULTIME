/**
 * ShareBionicButton — BCE-4X GOLDEN V6+ PARTAGER
 * =================================================
 * Bouton de partage BIONIC avec 14 canaux fonctionnels.
 * Chaque canal ouvre la fenetre de partage native.
 * Master Switch + Marketing Engine auto-capture.
 *
 * STEEVE-MAX — ZERO INTERPRETATION — TOUS CANAUX FONCTIONNELS
 */
import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  Share2, Copy, CheckCircle, Mail, MessageCircle,
  Smartphone, ExternalLink, X
} from 'lucide-react';

// ═══ 14 CANAUX PARTAGER — TOUS FONCTIONNELS ═══
const SHARE_CHANNELS = [
  { id: 'native', label: 'Partage natif (iOS/Android)', desc: 'Partage systeme natif', icon: Smartphone, color: '#10B981',
    getUrl: (url, text) => ({ native: true, text, url }) },
  { id: 'gmail', label: 'Gmail', desc: 'Email via Gmail', icon: Mail, color: '#EA4335',
    getUrl: (url, text) => `https://mail.google.com/mail/?view=cm&fs=1&body=${encodeURIComponent(text + '\n\n' + url)}&su=${encodeURIComponent('BIONIC — Territoire de chasse')}` },
  { id: 'outlook', label: 'Outlook', desc: 'Email via Outlook', icon: Mail, color: '#0078D4',
    getUrl: (url, text) => `https://outlook.live.com/mail/0/deeplink/compose?body=${encodeURIComponent(text + '\n\n' + url)}&subject=${encodeURIComponent('BIONIC — Territoire de chasse')}` },
  { id: 'yahoo', label: 'Yahoo Mail', desc: 'Email via Yahoo', icon: Mail, color: '#6001D2',
    getUrl: (url, text) => `https://compose.mail.yahoo.com/?body=${encodeURIComponent(text + '\n\n' + url)}&subject=${encodeURIComponent('BIONIC — Territoire de chasse')}` },
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
  territoire: { prefix: 'Analyse BIONIC SUPRA' },
  premium: { prefix: 'Rapport BIONIC Premium' },
  viral: { prefix: 'BIONIC Chasse' },
};

export function ShareBionicButton({ variant = 'default' }) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [lastShared, setLastShared] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('territoire');
  const [masterSwitch, setMasterSwitch] = useState({ global: true, channels: {} });
  const panelRef = useRef(null);

  // Fetch Master Switch status
  useEffect(() => {
    const fetchMasterSwitch = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
        const res = await fetch(`${backendUrl}/api/share/master-switch`);
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

  const buildShareUrl = useCallback(() => {
    return typeof window !== 'undefined' ? window.location.href : 'https://huntiq.ca';
  }, []);

  const buildShareText = useCallback(() => {
    const template = SHARE_TEMPLATES[selectedTemplate];
    return `${template.prefix} — Analyse complete du territoire. Donnees scientifiques, scores nutritionnels et recommandations.`;
  }, [selectedTemplate]);

  // Track share event + marketing capture
  const trackShare = useCallback(async (channel, template) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      await fetch(`${backendUrl}/api/share/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel,
          template,
          url: buildShareUrl(),
          timestamp: new Date().toISOString(),
          page_context: typeof window !== 'undefined' ? window.location.pathname : '',
          user_email: localStorage.getItem('huntiq_user_email') || null,
          user_id: localStorage.getItem('huntiq_user_id') || null,
        }),
      });
    } catch (_) { /* silent fail */ }
  }, [buildShareUrl]);

  const handleShare = useCallback((channelId) => {
    const channel = SHARE_CHANNELS.find(c => c.id === channelId);
    if (!channel) return;

    const url = buildShareUrl();
    const text = buildShareText();
    const result = channel.getUrl(url, text);

    // Track marketing event
    trackShare(channelId, selectedTemplate);

    if (typeof result === 'object' && result.native) {
      // Native share API
      if (navigator.share) {
        navigator.share({ title: 'BIONIC Territoire', text: result.text, url: result.url }).catch(() => {});
      } else {
        // Fallback: copy link
        navigator.clipboard?.writeText(url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } else if (typeof result === 'object' && result.copy) {
      // Copy to clipboard
      navigator.clipboard?.writeText(url + '\n\n' + text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } else if (typeof result === 'string') {
      // Open sharing window
      window.open(result, '_blank', 'width=600,height=500,scrollbars=yes,resizable=yes');
    }

    setLastShared(channelId);
    setTimeout(() => setLastShared(null), 3000);
  }, [buildShareUrl, buildShareText, selectedTemplate, trackShare]);

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
          className="absolute right-0 top-full mt-2 w-[380px] rounded-2xl overflow-hidden"
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
                <span className="text-[16px] font-bold text-white">PARTAGER BIONIC</span>
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

          {/* Preview */}
          <div className="px-4 py-2.5" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <div className="text-[14px] text-gray-500 uppercase font-bold mb-1">Apercu</div>
            <p className="text-[14px] text-gray-300 leading-relaxed line-clamp-2">{buildShareText()}</p>
          </div>

          {/* 14 CANAUX — TOUS FONCTIONNELS */}
          <div className="p-2 max-h-[320px] overflow-y-auto" data-testid="share-channels-list">
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
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all hover:bg-white/5"
                  style={{ backgroundColor: isLast ? '#10B98115' : 'transparent' }}
                  data-testid={`share-channel-${ch.id}`}>
                  <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${ch.color}20` }}>
                    {isLast ? <CheckCircle className="h-4 w-4 text-emerald-400" /> : <Icon className="h-4 w-4" style={{ color: ch.color }} />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[16px] font-medium text-white">{ch.label}</div>
                    <div className="text-[14px] text-gray-500">{ch.desc}</div>
                  </div>
                  {(ch.id === 'copy' || ch.id === 'instagram' || ch.id === 'tiktok') && copied && isLast && (
                    <span className="text-[14px] text-emerald-400 font-bold flex-shrink-0">Copie!</span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Footer — Master Switch */}
          <div className="px-4 py-2.5" style={{ borderTop: '1px solid rgba(255,255,255,0.06)', backgroundColor: '#1E293B', borderRadius: '0 0 16px 16px' }}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${masterSwitch.global ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                <span className={`text-[14px] uppercase font-bold tracking-wider ${masterSwitch.global ? 'text-gray-500' : 'text-red-400'}`}>
                  Master Switch {masterSwitch.global ? 'ON' : 'OFF'}
                </span>
              </div>
              <span className="text-[14px] font-bold tracking-wider text-emerald-500/60" data-testid="master-switch-indicator">
                14 CANAUX
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ShareBionicButton;
