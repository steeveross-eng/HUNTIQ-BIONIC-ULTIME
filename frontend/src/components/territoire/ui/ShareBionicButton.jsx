/**
 * ShareBionicButton — BCE-4X GOLDEN V6+ Module PARTAGER
 * ======================================================
 * Remplacement total du bouton PRINT V1-V5.
 * 
 * Fonctionnalités:
 *   - Web Share API (contacts OS natif: iPhone, Android, Windows, MacOS)
 *   - Partage direct: Facebook, Instagram, TikTok, Messenger, WhatsApp, SMS
 *   - Contenus pré-conçus: publicités BIONIC, visuels Premium
 *   - Tracking Premium: clics, partages, conversions
 *   - Intégration ADMIN PREMIUM ready
 */
import React, { useState, useCallback } from 'react';
import { Share2, Facebook, MessageCircle, Send, Smartphone, Link, CheckCircle, ExternalLink } from 'lucide-react';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';

const SHARE_CHANNELS = [
  { id: 'native', label: 'Partage OS', icon: Smartphone, color: '#3CB371', desc: 'iOS / Android natif' },
  { id: 'gmail', label: 'Gmail', icon: Send, color: '#EA4335', desc: 'Courriel Gmail' },
  { id: 'outlook', label: 'Outlook', icon: Send, color: '#0078D4', desc: 'Courriel Outlook' },
  { id: 'yahoo', label: 'Yahoo Mail', icon: Send, color: '#6001D2', desc: 'Courriel Yahoo' },
  { id: 'facebook', label: 'Facebook', icon: Facebook, color: '#1877F2', desc: 'Groupes & Feed' },
  { id: 'messenger', label: 'Messenger', icon: MessageCircle, color: '#0099FF', desc: 'Message direct' },
  { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircle, color: '#25D366', desc: 'Contacts & Groupes' },
  { id: 'x', label: 'X (Twitter)', icon: ExternalLink, color: '#000000', desc: 'Tweet & DM' },
  { id: 'linkedin', label: 'LinkedIn', icon: ExternalLink, color: '#0A66C2', desc: 'Post & Message' },
  { id: 'instagram', label: 'Instagram', icon: ExternalLink, color: '#E4405F', desc: 'Story & DM' },
  { id: 'tiktok', label: 'TikTok', icon: ExternalLink, color: '#FF0050', desc: 'Profil & Message' },
  { id: 'sms', label: 'SMS', icon: Send, color: '#4CAF50', desc: 'Texto direct' },
  { id: 'copy', label: 'Copier lien', icon: Link, color: '#9CA3AF', desc: 'Presse-papiers' },
];

const SHARE_TEMPLATES = {
  territoire: {
    title: 'HUNTIQ BIONIC - Mon Territoire de Chasse',
    text: 'Analyse complete de mon territoire avec HUNTIQ BIONIC V6+ : meteo, vents, corridors fauniques, points chauds et scoring IA.',
    hashtags: '#HUNTIQ #BionicHunting #ChasseQuebec #TerritoireBionic',
  },
  premium: {
    title: 'HUNTIQ BIONIC PREMIUM - Intelligence Terrain',
    text: 'Decouvrez HUNTIQ BIONIC : la plateforme de chasse intelligente #1 au Quebec. Analyse terrain IA, cartes HF LIDAR, recommandations affuts et corridors fauniques.',
    hashtags: '#HUNTIQ #Premium #ChasseIntelligente #Quebec',
  },
  viral: {
    title: 'Resultats incroyables avec HUNTIQ BIONIC',
    text: 'Ma strategie de chasse a change completement depuis HUNTIQ BIONIC V6+. Score terrain, meteo en temps reel, corridors fauniques... Essayez gratuitement !',
    hashtags: '#HUNTIQ #Chasse #ResultatsReels #BionicHunting',
  },
};

const buildShareUrl = () => {
  return typeof window !== 'undefined' ? window.location.href : 'https://huntiq.ca';
};

const trackShare = async (channel, template, metadata = {}) => {
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
        ...metadata,
      }),
    });
  } catch (_) { /* silent fail — tracking non-bloquant */ }
};

export function ShareBionicButton({ sharedWeather }) {
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('territoire');
  const [copied, setCopied] = useState(false);
  const [lastShared, setLastShared] = useState(null);
  const [masterSwitch, setMasterSwitch] = useState({ global: true, channels: {} });

  // Master Switch — Vérification état au montage et à chaque ouverture
  const fetchMasterSwitch = useCallback(async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const res = await fetch(`${backendUrl}/api/share/master-switch`);
      if (res.ok) {
        const data = await res.json();
        setMasterSwitch({
          global: data.global_enabled,
          channels: Object.fromEntries(
            Object.entries(data.channels || {}).map(([k, v]) => [k, v.enabled])
          ),
        });
      }
    } catch (_) { /* Master Switch fallback: ON */ }
  }, []);

  React.useEffect(() => { fetchMasterSwitch(); }, [fetchMasterSwitch]);
  React.useEffect(() => { if (open) fetchMasterSwitch(); }, [open, fetchMasterSwitch]);

  const template = SHARE_TEMPLATES[selectedTemplate];
  const shareUrl = buildShareUrl();

  const weatherSummary = sharedWeather?.weather?.temperature != null
    ? ` | ${sharedWeather.weather.temperature}C ${sharedWeather.wind?.directionLabel || ''} ${sharedWeather.wind?.speed || ''}km/h`
    : '';
  const shareText = `${template.text}${weatherSummary}\n\n${template.hashtags}\n${shareUrl}`;

  const handleShare = useCallback(async (channel) => {
    const url = buildShareUrl();
    const text = `${template.text}${weatherSummary}\n\n${template.hashtags}`;
    const title = template.title;

    trackShare(channel, selectedTemplate, {
      hasWeather: !!sharedWeather?.weather?.temperature,
    });

    switch (channel) {
      case 'native':
        if (navigator.share) {
          try {
            await navigator.share({ title, text, url });
            setLastShared('native');
          } catch (_) { /* user cancelled */ }
        } else {
          await navigator.clipboard.writeText(`${title}\n${text}\n${url}`);
          setCopied(true);
          setLastShared('native');
          setTimeout(() => setCopied(false), 2000);
        }
        break;

      case 'gmail':
        window.open(`https://mail.google.com/mail/?view=cm&su=${encodeURIComponent(title)}&body=${encodeURIComponent(`${text}\n${url}`)}`, '_blank');
        setLastShared('gmail');
        break;

      case 'outlook':
        window.open(`https://outlook.live.com/mail/0/deeplink/compose?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`${text}\n${url}`)}`, '_blank');
        setLastShared('outlook');
        break;

      case 'yahoo':
        window.open(`https://compose.mail.yahoo.com/?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`${text}\n${url}`)}`, '_blank');
        setLastShared('yahoo');
        break;

      case 'facebook':
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}&quote=${encodeURIComponent(text)}`, '_blank', 'width=600,height=400');
        setLastShared('facebook');
        break;

      case 'messenger':
        window.open(`fb-messenger://share?link=${encodeURIComponent(url)}`, '_blank');
        setTimeout(() => {
          window.open(`https://www.facebook.com/dialog/send?link=${encodeURIComponent(url)}&app_id=0&redirect_uri=${encodeURIComponent(url)}`, '_blank', 'width=600,height=400');
        }, 500);
        setLastShared('messenger');
        break;

      case 'whatsapp':
        window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(`${title}\n${text}\n${url}`)}`, '_blank');
        setLastShared('whatsapp');
        break;

      case 'x':
        window.open(`https://x.com/intent/tweet?text=${encodeURIComponent(`${text}`)}&url=${encodeURIComponent(url)}`, '_blank', 'width=600,height=400');
        setLastShared('x');
        break;

      case 'linkedin':
        window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`, '_blank', 'width=600,height=400');
        setLastShared('linkedin');
        break;

      case 'instagram':
        await navigator.clipboard.writeText(`${title}\n${text}\n${url}`);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        window.open('https://www.instagram.com/', '_blank');
        setLastShared('instagram');
        break;

      case 'tiktok':
        await navigator.clipboard.writeText(`${title}\n${text}\n${url}`);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        window.open('https://www.tiktok.com/', '_blank');
        setLastShared('tiktok');
        break;

      case 'sms':
        window.open(`sms:?body=${encodeURIComponent(`${title}\n${text}\n${url}`)}`, '_self');
        setLastShared('sms');
        break;

      case 'copy':
        await navigator.clipboard.writeText(`${title}\n${text}\n${url}`);
        setCopied(true);
        setLastShared('copy');
        setTimeout(() => setCopied(false), 2000);
        break;

      default:
        break;
    }
  }, [template, weatherSummary, selectedTemplate, sharedWeather]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          className="flex items-center gap-1.5 bg-[#111118] rounded-lg px-2.5 py-1.5 border border-emerald-500/30 hover:bg-emerald-500/10 hover:border-emerald-500/50 transition-all group"
          title="Partager BIONIC"
          data-testid="header-share-btn"
        >
          <Share2 className="h-4 w-4 text-emerald-400 group-hover:text-emerald-300 transition-colors" />
          <span className="text-[10px] text-emerald-400 uppercase font-bold tracking-wider group-hover:text-emerald-300">Partager</span>
        </button>
      </PopoverTrigger>
      <PopoverContent
        align="end"
        sideOffset={8}
        className="w-96 bg-[#0F172A] border-none p-0 shadow-2xl shadow-black/60"
        style={{ borderRadius: '16px' }}
        data-testid="share-popover"
      >
        <div className="p-4 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#3CB37120' }}>
              <Share2 className="h-4 w-4 text-emerald-400" />
            </div>
            <span className="text-[16px] font-bold text-white">Partager BIONIC</span>
          </div>
          {/* Template selector */}
          <div className="flex gap-2">
            {Object.entries(SHARE_TEMPLATES).map(([key, tmpl]) => (
              <button
                key={key}
                onClick={() => setSelectedTemplate(key)}
                className="flex-1 px-3 py-1.5 rounded-xl text-[14px] font-bold transition-all"
                style={{
                  backgroundColor: selectedTemplate === key ? '#10B98120' : '#1E293B',
                  color: selectedTemplate === key ? '#10B981' : '#6b7280',
                  border: selectedTemplate === key ? '1px solid #10B98140' : '1px solid transparent',
                }}
                data-testid={`share-template-${key}`}
              >
                {key === 'territoire' ? 'Territoire' : key === 'premium' ? 'Premium' : 'Viral'}
              </button>
            ))}
          </div>
        </div>

        {/* Preview */}
        <div className="px-4 py-3 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
          <div className="text-[12px] text-gray-500 uppercase font-bold mb-1">Apercu</div>
          <p className="text-[14px] text-gray-300 leading-relaxed line-clamp-2">{shareText.slice(0, 140)}...</p>
        </div>

        {/* Share channels — STANDARD GOLDEN */}
        <div className="p-2 max-h-[320px] overflow-y-auto" style={{ scrollBehavior: 'smooth' }} data-testid="share-channels-list">
          {!masterSwitch.global && (
            <div className="px-4 py-6 text-center">
              <div className="text-[14px] text-red-400 font-bold uppercase mb-1">Master Switch OFF</div>
              <div className="text-[14px] text-gray-500">Activation par STEEVE-MAX requise</div>
            </div>
          )}
          {SHARE_CHANNELS.filter(ch => masterSwitch.global && masterSwitch.channels[ch.id] !== false).map((ch) => {
            const Icon = ch.icon;
            const isLastShared = lastShared === ch.id;
            return (
              <button
                key={ch.id}
                onClick={() => handleShare(ch.id)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all"
                style={{ backgroundColor: isLastShared ? '#10B98115' : 'transparent' }}
                onMouseEnter={e => { if (!isLastShared) e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.04)'; }}
                onMouseLeave={e => { if (!isLastShared) e.currentTarget.style.backgroundColor = 'transparent'; }}
                data-testid={`share-channel-${ch.id}`}
              >
                <div className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${ch.color}20` }}>
                  {isLastShared ? (
                    <CheckCircle className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <Icon className="h-4 w-4" style={{ color: ch.color }} />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-[16px] font-medium text-white">{ch.label}</div>
                  <div className="text-[12px] text-gray-500">{ch.desc}</div>
                </div>
                {ch.id === 'copy' && copied && (
                  <span className="text-[14px] text-emerald-400 font-bold">Copie!</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Footer — Master Switch */}
        <div className="px-4 py-2.5 border-t" style={{ borderColor: 'rgba(255,255,255,0.06)', backgroundColor: '#1E293B', borderRadius: '0 0 16px 16px' }}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${masterSwitch.global ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
              <span className={`text-[12px] uppercase font-bold tracking-wider ${masterSwitch.global ? 'text-gray-500' : 'text-red-400'}`}>
                Master Switch {masterSwitch.global ? 'ON' : 'OFF'}
              </span>
            </div>
            <span className={`text-[12px] font-bold tracking-wider ${masterSwitch.global ? 'text-emerald-500/60' : 'text-red-400/60'}`} data-testid="master-switch-indicator">
              {Object.values(masterSwitch.channels).filter(Boolean).length}/13 CANAUX
            </span>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
