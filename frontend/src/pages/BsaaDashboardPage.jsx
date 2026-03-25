/**
 * BSAA Dashboard — BIONIC Social Ads Automation
 * x4500-ULTRA — Multi-platform campaign management
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Megaphone, Plus, BarChart3, Eye, MousePointer, TrendingUp,
  Facebook, Instagram, Video, Youtube, MessageCircle,
  ChevronRight, Sparkles, Globe, Target, Calendar,
  Trash2, Edit, Play, Pause, Copy
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const PLATFORM_ICONS = {
  facebook: Facebook,
  instagram: Instagram,
  tiktok: Video,
  youtube: Youtube,
  reddit: MessageCircle,
};

const STATUS_COLORS = {
  draft: 'bg-gray-600 text-gray-200',
  scheduled: 'bg-blue-900 text-blue-300',
  active: 'bg-green-900 text-green-300',
  paused: 'bg-yellow-900 text-yellow-300',
  completed: 'bg-purple-900 text-purple-300',
};

const TYPE_LABELS = {
  awareness: 'Notoriete',
  traffic: 'Trafic',
  conversion: 'Conversion',
  engagement: 'Engagement',
};

export default function BsaaDashboardPage() {
  const [campaigns, setCampaigns] = useState([]);
  const [summary, setSummary] = useState(null);
  const [platforms, setPlatforms] = useState({});
  const [generatedContent, setGeneratedContent] = useState(null);
  const [activeTab, setActiveTab] = useState('campaigns');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [campRes, sumRes, platRes] = await Promise.all([
        fetch(`${API}/api/bsaa/campaigns`),
        fetch(`${API}/api/bsaa/analytics/summary`),
        fetch(`${API}/api/bsaa/platforms`),
      ]);
      const campData = await campRes.json();
      const sumData = await sumRes.json();
      const platData = await platRes.json();
      setCampaigns(campData.campaigns || []);
      setSummary(sumData);
      setPlatforms(platData.platforms || {});
    } catch (err) {
      console.error('BSAA fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const createCampaign = async (data) => {
    try {
      const res = await fetch(`${API}/api/bsaa/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (res.ok) {
        setShowCreateModal(false);
        fetchData();
      }
    } catch (err) {
      console.error('Create campaign error:', err);
    }
  };

  const deleteCampaign = async (id) => {
    if (!window.confirm('Supprimer cette campagne ?')) return;
    try {
      await fetch(`${API}/api/bsaa/campaigns/${id}`, { method: 'DELETE' });
      fetchData();
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const generateContent = async (type = 'awareness', platform = 'facebook', language = 'fr') => {
    try {
      const res = await fetch(`${API}/api/bsaa/content/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, platform, language, species: 'CERF', region: 'Quebec' }),
      });
      const data = await res.json();
      setGeneratedContent(data.content);
    } catch (err) {
      console.error('Generate error:', err);
    }
  };

  return (
    <div data-testid="bsaa-dashboard" className="min-h-screen bg-[#0c1117] text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-[#0f1620]">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-amber-500/20 to-orange-500/20">
                <Megaphone className="h-6 w-6 text-amber-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold">BSAA</h1>
                <p className="text-xs text-gray-500">BIONIC Social Ads Automation</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                data-testid="bsaa-generate-btn"
                onClick={() => generateContent()}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600/20 border border-purple-500/30 rounded-lg text-purple-300 hover:bg-purple-600/30 transition-colors text-sm"
              >
                <Sparkles className="h-4 w-4" /> Generer du contenu
              </button>
              <button
                data-testid="bsaa-create-campaign-btn"
                onClick={() => setShowCreateModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-amber-500 rounded-lg text-black font-semibold hover:bg-amber-400 transition-colors text-sm"
              >
                <Plus className="h-4 w-4" /> Nouvelle campagne
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {[
              { key: 'campaigns', label: 'Campagnes', icon: Megaphone },
              { key: 'content', label: 'Contenu', icon: Sparkles },
              { key: 'analytics', label: 'Analytics', icon: BarChart3 },
              { key: 'platforms', label: 'Plateformes', icon: Globe },
            ].map(tab => (
              <button
                key={tab.key}
                data-testid={`bsaa-tab-${tab.key}`}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-amber-400 text-amber-400'
                    : 'border-transparent text-gray-500 hover:text-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Analytics summary cards */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            {[
              { label: 'Campagnes', value: summary.total_campaigns, icon: Megaphone, color: 'amber' },
              { label: 'Impressions', value: summary.total_impressions.toLocaleString(), icon: Eye, color: 'blue' },
              { label: 'Clics', value: summary.total_clicks.toLocaleString(), icon: MousePointer, color: 'green' },
              { label: 'Conversions', value: summary.total_conversions, icon: TrendingUp, color: 'purple' },
              { label: 'CTR moyen', value: `${summary.avg_ctr}%`, icon: Target, color: 'orange' },
            ].map((card, i) => (
              <div
                key={i}
                data-testid={`bsaa-stat-${card.label.toLowerCase()}`}
                className="bg-[#151d28] border border-gray-800 rounded-xl p-4"
              >
                <div className="flex items-center gap-2 mb-2">
                  <card.icon className={`h-4 w-4 text-${card.color}-400`} />
                  <span className="text-xs text-gray-500">{card.label}</span>
                </div>
                <div className="text-2xl font-bold">{card.value}</div>
              </div>
            ))}
          </div>
        )}

        {/* Tab: Campaigns */}
        {activeTab === 'campaigns' && (
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-12 text-gray-500">Chargement...</div>
            ) : campaigns.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-gray-700 rounded-xl">
                <Megaphone className="h-10 w-10 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">Aucune campagne</p>
                <p className="text-gray-600 text-xs mt-1">Cliquez sur "Nouvelle campagne" pour commencer</p>
              </div>
            ) : (
              campaigns.map(c => (
                <div
                  key={c.campaign_id}
                  data-testid={`bsaa-campaign-${c.campaign_id}`}
                  className="bg-[#151d28] border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex gap-1.5">
                        {c.platforms?.map(p => {
                          const Icon = PLATFORM_ICONS[p] || Globe;
                          return <Icon key={p} className="h-4 w-4 text-gray-400" />;
                        })}
                      </div>
                      <div>
                        <h3 className="font-semibold text-sm">{c.name}</h3>
                        <p className="text-xs text-gray-500">{c.description || TYPE_LABELS[c.type] || c.type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[c.status] || 'bg-gray-700'}`}>
                        {c.status}
                      </span>
                      <span className="text-xs text-gray-500">{c.budget?.total} {c.budget?.currency}</span>
                      <div className="flex gap-1">
                        <button onClick={() => deleteCampaign(c.campaign_id)} className="p-1.5 rounded hover:bg-red-900/30">
                          <Trash2 className="h-3.5 w-3.5 text-red-400" />
                        </button>
                      </div>
                      <ChevronRight className="h-4 w-4 text-gray-600" />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Tab: Content Generator */}
        {activeTab === 'content' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-[#151d28] border border-gray-800 rounded-xl p-6">
                <h3 className="font-semibold text-sm mb-4 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-purple-400" /> Generateur de contenu
                </h3>
                <div className="space-y-3">
                  {['awareness', 'traffic', 'conversion', 'engagement'].map(type => (
                    <button
                      key={type}
                      data-testid={`bsaa-gen-${type}`}
                      onClick={() => generateContent(type)}
                      className="w-full flex items-center justify-between p-3 bg-[#0f1620] rounded-lg hover:bg-[#1a2436] transition-colors text-sm"
                    >
                      <span>{TYPE_LABELS[type]}</span>
                      <ChevronRight className="h-4 w-4 text-gray-500" />
                    </button>
                  ))}
                </div>
              </div>
              {generatedContent && (
                <div data-testid="bsaa-generated-content" className="bg-[#151d28] border border-amber-800/30 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-sm text-amber-400">Contenu genere</h3>
                    <span className="text-xs bg-amber-900/30 text-amber-300 px-2 py-0.5 rounded">{generatedContent.platform}</span>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-gray-500">Titre</label>
                      <p className="text-sm font-semibold mt-1">{generatedContent.title}</p>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">Corps</label>
                      <p className="text-sm text-gray-300 mt-1">{generatedContent.body}</p>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500">CTA</label>
                      <p className="text-sm text-amber-400 font-medium mt-1">{generatedContent.cta}</p>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {generatedContent.hashtags?.map((h, i) => (
                        <span key={i} className="text-xs bg-blue-900/30 text-blue-400 px-2 py-0.5 rounded">{h}</span>
                      ))}
                    </div>
                    <div className="flex gap-2 pt-2">
                      <button
                        onClick={() => navigator.clipboard?.writeText(`${generatedContent.title}\n\n${generatedContent.body}\n\n${generatedContent.hashtags?.join(' ')}`)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 rounded-lg text-xs hover:bg-gray-600"
                      >
                        <Copy className="h-3 w-3" /> Copier
                      </button>
                      <button
                        onClick={() => generateContent(generatedContent.type, generatedContent.platform, generatedContent.language)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-700/30 text-purple-300 rounded-lg text-xs hover:bg-purple-700/50"
                      >
                        <Sparkles className="h-3 w-3" /> Regenerer
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab: Analytics */}
        {activeTab === 'analytics' && summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#151d28] border border-gray-800 rounded-xl p-6">
              <h3 className="font-semibold text-sm mb-4">Par statut</h3>
              {Object.entries(summary.by_status || {}).length === 0 ? (
                <p className="text-gray-500 text-xs">Aucune donnee</p>
              ) : (
                <div className="space-y-2">
                  {Object.entries(summary.by_status).map(([status, count]) => (
                    <div key={status} className="flex justify-between items-center text-sm">
                      <span className={`px-2 py-0.5 rounded-full text-xs ${STATUS_COLORS[status]}`}>{status}</span>
                      <span className="font-mono">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="bg-[#151d28] border border-gray-800 rounded-xl p-6">
              <h3 className="font-semibold text-sm mb-4">Par plateforme</h3>
              {Object.entries(summary.by_platform || {}).length === 0 ? (
                <p className="text-gray-500 text-xs">Aucune donnee</p>
              ) : (
                <div className="space-y-2">
                  {Object.entries(summary.by_platform).map(([platform, count]) => {
                    const Icon = PLATFORM_ICONS[platform] || Globe;
                    return (
                      <div key={platform} className="flex justify-between items-center text-sm">
                        <div className="flex items-center gap-2">
                          <Icon className="h-4 w-4 text-gray-400" />
                          <span>{platform}</span>
                        </div>
                        <span className="font-mono">{count}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab: Platforms */}
        {activeTab === 'platforms' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(platforms).map(([key, p]) => {
              const Icon = PLATFORM_ICONS[key] || Globe;
              return (
                <div
                  key={key}
                  data-testid={`bsaa-platform-${key}`}
                  className="bg-[#151d28] border border-gray-800 rounded-xl p-5"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <Icon className="h-5 w-5 text-gray-400" />
                    <h3 className="font-semibold text-sm">{p.name}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded ${p.status === 'available' ? 'bg-green-900/30 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                      {p.status === 'available' ? 'Disponible' : 'Bientot'}
                    </span>
                  </div>
                  <div className="space-y-2 text-xs text-gray-500">
                    <div>Formats: {p.formats?.join(', ')}</div>
                    <div>Tailles: {p.image_sizes?.join(', ')}</div>
                    {p.max_title_length > 0 && <div>Titre max: {p.max_title_length} car.</div>}
                    <div>Corps max: {p.max_body_length} car.</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Campaign Modal */}
      {showCreateModal && <CreateCampaignModal onCreate={createCampaign} onClose={() => setShowCreateModal(false)} />}
    </div>
  );
}

function CreateCampaignModal({ onCreate, onClose }) {
  const [form, setForm] = useState({
    name: '',
    description: '',
    type: 'awareness',
    platforms: ['facebook'],
    budget_total: 100,
    budget_daily: 10,
    languages: ['fr'],
  });

  const togglePlatform = (p) => {
    setForm(prev => ({
      ...prev,
      platforms: prev.platforms.includes(p)
        ? prev.platforms.filter(x => x !== p)
        : [...prev.platforms, p],
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div data-testid="bsaa-create-modal" className="bg-[#151d28] border border-gray-700 rounded-2xl p-6 w-full max-w-lg">
        <h2 className="text-lg font-bold mb-4">Nouvelle campagne</h2>
        <div className="space-y-4">
          <div>
            <label className="text-xs text-gray-500">Nom</label>
            <input
              data-testid="bsaa-input-name"
              value={form.name}
              onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
              className="w-full mt-1 px-3 py-2 bg-[#0c1117] border border-gray-700 rounded-lg text-sm focus:border-amber-500 outline-none"
              placeholder="Ma campagne BIONIC"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500">Type</label>
            <select
              data-testid="bsaa-select-type"
              value={form.type}
              onChange={e => setForm(p => ({ ...p, type: e.target.value }))}
              className="w-full mt-1 px-3 py-2 bg-[#0c1117] border border-gray-700 rounded-lg text-sm outline-none"
            >
              <option value="awareness">Notoriete</option>
              <option value="traffic">Trafic</option>
              <option value="conversion">Conversion</option>
              <option value="engagement">Engagement</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500">Plateformes</label>
            <div className="flex gap-2 mt-1">
              {['facebook', 'instagram', 'tiktok', 'youtube', 'reddit'].map(p => {
                const Icon = PLATFORM_ICONS[p] || Globe;
                return (
                  <button
                    key={p}
                    onClick={() => togglePlatform(p)}
                    className={`p-2 rounded-lg border text-sm ${
                      form.platforms.includes(p)
                        ? 'border-amber-500 bg-amber-900/20 text-amber-300'
                        : 'border-gray-700 text-gray-500 hover:border-gray-600'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </button>
                );
              })}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500">Budget total (CAD)</label>
              <input
                type="number"
                value={form.budget_total}
                onChange={e => setForm(p => ({ ...p, budget_total: Number(e.target.value) }))}
                className="w-full mt-1 px-3 py-2 bg-[#0c1117] border border-gray-700 rounded-lg text-sm outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500">Budget quotidien (CAD)</label>
              <input
                type="number"
                value={form.budget_daily}
                onChange={e => setForm(p => ({ ...p, budget_daily: Number(e.target.value) }))}
                className="w-full mt-1 px-3 py-2 bg-[#0c1117] border border-gray-700 rounded-lg text-sm outline-none"
              />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button
              data-testid="bsaa-submit-campaign"
              onClick={() => form.name && onCreate(form)}
              className="flex-1 py-2 bg-amber-500 text-black font-semibold rounded-lg hover:bg-amber-400 text-sm"
            >
              Creer la campagne
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 text-sm"
            >
              Annuler
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
