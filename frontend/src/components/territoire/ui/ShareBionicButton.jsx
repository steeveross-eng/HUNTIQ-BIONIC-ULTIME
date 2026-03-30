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
  { id: 'native', label: 'Partage OS', icon: Smartphone, color: '#3CB371', desc: 'Contacts natifs' },
  { id: 'facebook', label: 'Facebook', icon: Facebook, color: '#1877F2', desc: 'Groupes & Feed' },
  { id: 'messenger', label: 'Messenger', icon: MessageCircle, color: '#0099FF', desc: 'Message direct' },
  { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircle, color: '#25D366', desc: 'Contacts & Groupes' },
  { id: 'instagram', label: 'Instagram', icon: ExternalLink, color: '#E4405F', desc: 'Story & DM' },
  { id: 'tiktok', label: 'TikTok', icon: ExternalLink, color: '#000000', desc: 'Profil & Message' },
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
        className="w-80 bg-gray-950/98 backdrop-blur-xl border-emerald-500/20 p-0 shadow-2xl shadow-black/60"
        data-testid="share-popover"
      >
        <div className="p-3 border-b border-gray-700/40">
          <div className="flex items-center gap-2 mb-2">
            <Share2 className="h-4 w-4 text-emerald-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">Partager BIONIC</span>
          </div>
          {/* Template selector */}
          <div className="flex gap-1">
            {Object.entries(SHARE_TEMPLATES).map(([key, tmpl]) => (
              <button
                key={key}
                onClick={() => setSelectedTemplate(key)}
                className={`flex-1 px-2 py-1 rounded text-[9px] font-bold uppercase tracking-wider transition-all ${
                  selectedTemplate === key
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'bg-gray-800/50 text-gray-500 border border-gray-700/30 hover:text-gray-300'
                }`}
                data-testid={`share-template-${key}`}
              >
                {key === 'territoire' ? 'Territoire' : key === 'premium' ? 'Premium' : 'Viral'}
              </button>
            ))}
          </div>
        </div>

        {/* Preview */}
        <div className="px-3 py-2 border-b border-gray-700/30">
          <div className="text-[9px] text-gray-500 uppercase font-bold mb-1">Apercu du contenu</div>
          <p className="text-[10px] text-gray-300 leading-relaxed line-clamp-3">{shareText.slice(0, 160)}...</p>
        </div>

        {/* Share channels — filtered by Master Switch */}
        <div className="p-2 space-y-0.5" data-testid="share-channels-list">
          {SHARE_CHANNELS.filter(ch => masterSwitch.global && masterSwitch.channels[ch.id] !== false).map((ch) => {
            const Icon = ch.icon;
            const isLastShared = lastShared === ch.id;
            return (
              <button
                key={ch.id}
                onClick={() => handleShare(ch.id)}
                className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-left transition-all ${
                  isLastShared ? 'bg-emerald-500/15' : 'hover:bg-white/5'
                }`}
                data-testid={`share-channel-${ch.id}`}
              >
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${ch.color}20` }}>
                  {isLastShared ? (
                    <CheckCircle className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <Icon className="h-4 w-4" style={{ color: ch.color }} />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-medium text-white">{ch.label}</div>
                  <div className="text-[9px] text-gray-500">{ch.desc}</div>
                </div>
                {ch.id === 'copy' && copied && (
                  <span className="text-[9px] text-emerald-400 font-bold">Copie!</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Footer — Master Switch + Tracking */}
        <div className="px-3 py-2 border-t border-gray-700/30 bg-gray-900/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[8px] text-gray-500 uppercase font-bold tracking-wider">Master Switch ON</span>
            </div>
            <span className="text-[8px] text-emerald-500/60 font-bold tracking-wider" data-testid="master-switch-indicator">8/8 CANAUX</span>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
