import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import "@/theme/bionic_theme.css";
import {
  Target, Cloud, Eye, MapPin, Leaf, Bell, Award, Calendar,
  Thermometer, Navigation, ChevronRight, Activity, Moon,
  Wind, Droplets, Mountain, Camera, Clock, TrendingUp,
  AlertTriangle, Crosshair, Compass, BarChart3, Layers,
  Loader2, RefreshCw, Radio, Zap, TreePine, Waves
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

/* ============================================================
   BIONIC MODULES PAGE — 10 Modules Predictifs V5
   STEEVE-MAX x2000 / Phase D

   01. Prediction Comportement Faune
   02. Meteo Chasse Intelligente
   03. Carte Comportementale Dynamique
   04. Gestionnaire Territoire
   05. Vision Faune (Cameras)
   06. Planificateur Chasse
   07. Zones Alimentation
   08. Suivi GPS Intelligent
   09. Alertes Intelligentes
   10. Score Territoire
   ============================================================ */

const MODULES = [
  { id: "predictions", label: "Predictions", icon: Target, color: "#FF6B35" },
  { id: "meteo", label: "Meteo Chasse", icon: Cloud, color: "#4ECDC4" },
  { id: "behavioral-map", label: "Carte Comportementale", icon: Layers, color: "#9B59B6" },
  { id: "territory", label: "Mon Territoire", icon: MapPin, color: "#27AE60" },
  { id: "cameras", label: "Vision Faune", icon: Camera, color: "#E74C3C" },
  { id: "planner", label: "Planificateur", icon: Calendar, color: "#F39C12" },
  { id: "feeding", label: "Alimentation", icon: Leaf, color: "#2ECC71" },
  { id: "gps", label: "Suivi GPS", icon: Navigation, color: "#3498DB" },
  { id: "alerts", label: "Alertes", icon: Bell, color: "#E67E22" },
  { id: "score", label: "Score Territoire", icon: Award, color: "#1ABC9C" },
];

const SPECIES = [
  { value: "orignal", label: "Orignal", color: "#8B4513" },
  { value: "cerf_virginie", label: "Cerf de Virginie", color: "#D2691E" },
  { value: "ours_noir", label: "Ours noir", color: "#2C2C2C" },
  { value: "dindon_sauvage", label: "Dindon sauvage", color: "#8B0000" },
  { value: "caribou", label: "Caribou", color: "#696969" },
  { value: "wapiti", label: "Wapiti (Elk)", color: "#B8860B" },
  { value: "cerf_mulet", label: "Cerf mulet", color: "#C4A35A" },
  { value: "pronghorn", label: "Antilocapre (Pronghorn)", color: "#DEB887" },
];

// ═══════════════════════════════════════
// GAUGE COMPONENT
// ═══════════════════════════════════════
const ScoreGauge = ({ value, max = 100, label, color = "#FF6B35", size = 120 }) => {
  const radius = size * 0.44;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct * 0.75);

  return (
    <div style={{ textAlign: "center" }} data-testid={`gauge-${label}`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={radius}
          fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="8"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          transform={`rotate(135 ${size/2} ${size/2})`} strokeLinecap="round" />
        <circle cx={size/2} cy={size/2} r={radius}
          fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeDashoffset={offset}
          transform={`rotate(135 ${size/2} ${size/2})`} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s ease" }} />
      </svg>
      <div style={{ marginTop: -size * 0.55, fontSize: size * 0.22, fontWeight: 700, color }}>{Math.round(value)}</div>
      <div style={{ fontSize: 11, color: "rgba(255,255,255,0.6)", marginTop: 4 }}>{label}</div>
    </div>
  );
};

// ═══════════════════════════════════════
// DATA CARD
// ═══════════════════════════════════════
const DataCard = ({ title, value, unit, icon: Icon, color = "#4ECDC4", trend }) => (
  <div className="saline-stat-card" data-testid={`data-card-${title}`}>
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
      {Icon && <Icon size={16} style={{ color, opacity: 0.8 }} />}
      <span style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", textTransform: "uppercase", letterSpacing: 1 }}>{title}</span>
    </div>
    <div style={{ fontSize: 24, fontWeight: 700, color }}>{value}<span style={{ fontSize: 12, opacity: 0.6, marginLeft: 4 }}>{unit}</span></div>
    {trend && <div style={{ fontSize: 10, color: trend.startsWith("+") ? "#2ECC71" : "#E74C3C", marginTop: 4 }}>{trend}</div>}
  </div>
);

// ═══════════════════════════════════════
// PROGRESS BAR
// ═══════════════════════════════════════
const ProgressBar = ({ label, value, max = 100, color = "#FF6B35" }) => (
  <div style={{ marginBottom: 12 }}>
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
      <span style={{ color: "rgba(255,255,255,0.7)" }}>{label}</span>
      <span style={{ color, fontWeight: 600 }}>{Math.round(value)}%</span>
    </div>
    <div style={{ height: 6, background: "rgba(255,255,255,0.08)", borderRadius: 3 }}>
      <div style={{ height: "100%", width: `${Math.min(value / max * 100, 100)}%`, background: color, borderRadius: 3, transition: "width 0.8s ease" }} />
    </div>
  </div>
);

// ═══════════════════════════════════════
// MODULE 01: PREDICTIONS
// ═══════════════════════════════════════
const PredictionsModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const preds = data?.predictions || [];
  const weather = data?.weather;
  const solunar = data?.solunar;

  return (
    <div data-testid="module-predictions">
      <h3 className="saline-section-title" style={{ color: "#FF6B35" }}>
        <Target size={18} /> Prediction Comportement Faune
      </h3>
      <div className="saline-grid-3">
        {preds.map((p, i) => (
          <div key={i} className="saline-stat-card" style={{ borderLeft: `3px solid ${p.success_probability > 0.65 ? "#2ECC71" : p.success_probability > 0.45 ? "#F39C12" : "#E74C3C"}` }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.9)", marginBottom: 8, textTransform: "capitalize" }}>{p.species}</div>
            <ScoreGauge value={p.success_probability * 100} label="Succes" color={p.success_probability > 0.65 ? "#2ECC71" : "#F39C12"} size={100} />
            <div style={{ marginTop: 8, fontSize: 11, color: "rgba(255,255,255,0.5)" }}>
              Activite: <span style={{ color: "#4ECDC4" }}>{p.activity_level}</span>
            </div>
            {p.optimal_windows?.length > 0 && (
              <div style={{ marginTop: 6, fontSize: 10, color: "rgba(255,255,255,0.4)" }}>
                <Clock size={10} style={{ marginRight: 4 }} />
                {p.optimal_windows.map(w => `${w.start}-${w.end}`).join(", ")}
              </div>
            )}
          </div>
        ))}
      </div>
      {weather && (
        <div style={{ marginTop: 16 }}>
          <div className="saline-grid-4">
            <DataCard title="Temperature" value={weather.temperature_c} unit="C" icon={Thermometer} color="#4ECDC4" />
            <DataCard title="Vent" value={weather.wind_speed_kmh} unit="km/h" icon={Wind} color="#3498DB" />
            <DataCard title="Humidite" value={weather.humidity_pct} unit="%" icon={Droplets} color="#9B59B6" />
            <DataCard title="Impact Chasse" value={weather.hunting_impact_score} unit="/100" icon={Target} color="#FF6B35" />
          </div>
        </div>
      )}
      {solunar && (
        <div className="saline-stat-card" style={{ marginTop: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <Moon size={14} style={{ color: "#F39C12" }} />
            <span style={{ fontSize: 12, color: "rgba(255,255,255,0.6)" }}>Solunaire</span>
          </div>
          <div className="saline-grid-4">
            <div><span style={{ fontSize: 11, color: "rgba(255,255,255,0.4)" }}>Phase</span><div style={{ fontSize: 13, color: "#F39C12" }}>{solunar.moon_phase}</div></div>
            <div><span style={{ fontSize: 11, color: "rgba(255,255,255,0.4)" }}>Majeure 1</span><div style={{ fontSize: 13, color: "#4ECDC4" }}>{solunar.major_period_1}</div></div>
            <div><span style={{ fontSize: 11, color: "rgba(255,255,255,0.4)" }}>Majeure 2</span><div style={{ fontSize: 13, color: "#4ECDC4" }}>{solunar.major_period_2}</div></div>
            <div><span style={{ fontSize: 11, color: "rgba(255,255,255,0.4)" }}>Rating</span><div style={{ fontSize: 13, color: "#FF6B35" }}>{solunar.solunar_rating}/100</div></div>
          </div>
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 02: METEO CHASSE
// ═══════════════════════════════════════
const MeteoModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const w = data?.weather;
  const s = data?.solunar;
  if (!w) return <div style={{ color: "rgba(255,255,255,0.4)", padding: 20 }}>Aucune donnee meteo</div>;

  return (
    <div data-testid="module-meteo">
      <h3 className="saline-section-title" style={{ color: "#4ECDC4" }}>
        <Cloud size={18} /> Meteo Chasse Intelligente
      </h3>
      <div className="saline-grid-4">
        <DataCard title="Temperature" value={w.temperature_c} unit="C" icon={Thermometer} color="#FF6B35" />
        <DataCard title="Humidite" value={w.humidity_pct} unit="%" icon={Droplets} color="#3498DB" />
        <DataCard title="Vent" value={w.wind_speed_kmh} unit="km/h" icon={Wind} color="#9B59B6" />
        <DataCard title="Pression" value={w.pressure_hpa} unit="hPa" icon={Activity} color="#4ECDC4" />
      </div>
      <div className="saline-grid-3" style={{ marginTop: 16 }}>
        <DataCard title="Direction Vent" value={w.wind_direction} unit="" icon={Compass} color="#2ECC71" />
        <DataCard title="Precipitations" value={w.precipitation_mm} unit="mm" icon={Waves} color="#3498DB" />
        <DataCard title="Couverture Nuage" value={w.cloud_cover_pct} unit="%" icon={Cloud} color="#95A5A6" />
      </div>
      <div className="saline-stat-card" style={{ marginTop: 16, textAlign: "center" }}>
        <ScoreGauge value={w.hunting_impact_score} label="Impact Chasse" color={w.hunting_impact_score > 70 ? "#2ECC71" : w.hunting_impact_score > 40 ? "#F39C12" : "#E74C3C"} size={140} />
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 8 }}>
          Tendance pression: <span style={{ color: w.pressure_trend === "rising" ? "#2ECC71" : "#F39C12" }}>{w.pressure_trend}</span>
        </div>
      </div>
      {s && (
        <div className="saline-stat-card" style={{ marginTop: 12 }}>
          <div style={{ textAlign: "center" }}>
            <Moon size={20} style={{ color: "#F39C12", marginBottom: 8 }} />
            <div style={{ fontSize: 14, fontWeight: 600, color: "#F39C12" }}>{s.moon_phase}</div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", marginTop: 4 }}>Illumination: {s.moon_illumination_pct}%</div>
            <div style={{ fontSize: 12, color: "#4ECDC4", marginTop: 8 }}>Prediction activite: {s.activity_prediction}</div>
          </div>
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 03: CARTE COMPORTEMENTALE
// ═══════════════════════════════════════
const BehavioralMapModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const pipeline = data;
  if (!pipeline) return <div style={{ color: "rgba(255,255,255,0.4)", padding: 20 }}>Aucune donnee comportementale</div>;

  return (
    <div data-testid="module-behavioral-map">
      <h3 className="saline-section-title" style={{ color: "#9B59B6" }}>
        <Layers size={18} /> Carte Comportementale Dynamique
      </h3>
      {pipeline.key_insights?.length > 0 && (
        <div className="saline-stat-card" style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#9B59B6", marginBottom: 8 }}>Insights cles</div>
          {pipeline.key_insights.map((ins, i) => (
            <div key={i} style={{ fontSize: 12, color: "rgba(255,255,255,0.7)", padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <Zap size={10} style={{ color: "#F39C12", marginRight: 6 }} />{ins}
            </div>
          ))}
        </div>
      )}
      {pipeline.behavior_patterns?.length > 0 && (
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.6)", marginBottom: 8 }}>Patterns detectes</div>
          <div className="saline-grid-2">
            {pipeline.behavior_patterns.map((p, i) => (
              <div key={i} className="saline-stat-card" style={{ borderLeft: `3px solid ${p.behavior_type === "feeding" ? "#2ECC71" : p.behavior_type === "moving" ? "#3498DB" : p.behavior_type === "resting" ? "#9B59B6" : "#E74C3C"}` }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.8)", textTransform: "capitalize" }}>{p.behavior_type}</div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>{p.description}</div>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", marginTop: 6 }}>
                  Confiance: {Math.round(p.confidence * 100)}% | Frequence: {p.frequency}
                </div>
                {p.time_windows?.length > 0 && (
                  <div style={{ fontSize: 10, color: "#4ECDC4", marginTop: 4 }}>
                    <Clock size={9} /> {p.time_windows.map(w => `${w.start}-${w.end}`).join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      {pipeline.temporal_analysis && (
        <div className="saline-stat-card" style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#F39C12", marginBottom: 8 }}>Analyse Temporelle</div>
          <div className="saline-grid-2">
            <div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", marginBottom: 4 }}>Saisonniere</div>
              {Object.entries(pipeline.temporal_analysis.seasonal || {}).map(([s, v]) => (
                <ProgressBar key={s} label={s} value={v * 100} color="#9B59B6" />
              ))}
            </div>
            <div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", marginBottom: 4 }}>Phase lunaire</div>
              {Object.entries(pipeline.temporal_analysis.lunar_phase || {}).map(([p, v]) => (
                <ProgressBar key={p} label={p} value={v * 100} color="#F39C12" />
              ))}
            </div>
          </div>
          <div style={{ marginTop: 12, fontSize: 11 }}>
            <span style={{ color: "rgba(255,255,255,0.4)" }}>Heures de pointe: </span>
            <span style={{ color: "#2ECC71" }}>{pipeline.temporal_analysis.peak_hours?.join(", ")}</span>
          </div>
        </div>
      )}
      {pipeline.recommendations?.length > 0 && (
        <div className="saline-stat-card" style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#2ECC71", marginBottom: 8 }}>Recommandations</div>
          {pipeline.recommendations.map((r, i) => (
            <div key={i} style={{ fontSize: 12, color: "rgba(255,255,255,0.7)", padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <ChevronRight size={10} style={{ color: "#2ECC71", marginRight: 4 }} />{r}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 04: GESTIONNAIRE TERRITOIRE
// ═══════════════════════════════════════
const TerritoryModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const eco = data;
  if (!eco) return <div style={{ color: "rgba(255,255,255,0.4)", padding: 20 }}>Aucune donnee territoire</div>;

  return (
    <div data-testid="module-territory">
      <h3 className="saline-section-title" style={{ color: "#27AE60" }}>
        <MapPin size={18} /> Gestionnaire Territoire
      </h3>
      <div className="saline-grid-3">
        <DataCard title="Hotspots" value={eco.hotspots?.length || 0} unit="pts" icon={Crosshair} color="#E74C3C" />
        <DataCard title="Corridors" value={eco.corridors?.length || 0} unit="" icon={Navigation} color="#3498DB" />
        <DataCard title="Score Global" value={eco.scoring?.global_score || 0} unit="/100" icon={Award} color="#FF6B35" />
      </div>
      {eco.hotspots?.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.6)", marginBottom: 8 }}>Points d'observation</div>
          {eco.hotspots.map((h, i) => (
            <div key={i} className="saline-stat-card" style={{ marginBottom: 8, display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: h.type === "feeding" ? "#2ECC71" : h.type === "bedding" ? "#9B59B6" : h.type === "crossing" ? "#3498DB" : "#FF6B35" }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.8)" }}>{h.name}</div>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }}>{h.type} | Activite: {h.activity_score}/100</div>
              </div>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)" }}>{h.lat?.toFixed(4)}, {h.lng?.toFixed(4)}</div>
            </div>
          ))}
        </div>
      )}
      {eco.corridors?.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.6)", marginBottom: 8 }}>Corridors de deplacement</div>
          {eco.corridors.map((c, i) => (
            <div key={i} className="saline-stat-card" style={{ marginBottom: 8 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: 12, color: "rgba(255,255,255,0.8)" }}>{c.name}</span>
                <span style={{ fontSize: 11, color: "#4ECDC4" }}>{c.species}</span>
              </div>
              <ProgressBar label={`Confiance`} value={c.confidence * 100} color="#3498DB" />
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }}>
                <Clock size={9} /> {c.peak_hours?.join(", ")}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 05: VISION FAUNE (CAMERAS)
// ═══════════════════════════════════════
const CamerasModule = ({ loading }) => {
  if (loading) return <ModuleLoader />;

  const demoCameras = [
    { id: "cam-001", name: "Saline Nord", model: "Reconyx HP2X", direction: "Sud", events: 47, last: "2026-03-24 06:32", status: "active", species_detected: ["Orignal", "Cerf de Virginie", "Ours noir"] },
    { id: "cam-002", name: "Corridor Est", model: "Browning Strike Force", direction: "Ouest", events: 23, last: "2026-03-23 18:15", status: "active", species_detected: ["Cerf de Virginie", "Dindon sauvage"] },
    { id: "cam-003", name: "Point d'eau", model: "Spypoint Link-Micro", direction: "Nord", events: 12, last: "2026-03-22 05:48", status: "offline", species_detected: ["Orignal", "Wapiti"] },
    { id: "cam-004", name: "Lisiere Sud", model: "Reconyx HP2X", direction: "Est", events: 31, last: "2026-03-24 17:45", status: "active", species_detected: ["Cerf de Virginie", "Caribou", "Cerf mulet"] },
  ];

  return (
    <div data-testid="module-cameras">
      <h3 className="saline-section-title" style={{ color: "#E74C3C" }}>
        <Camera size={18} /> Vision Faune — Cameras
      </h3>
      <div className="saline-grid-3">
        <DataCard title="Cameras actives" value={3} unit="/4" icon={Camera} color="#2ECC71" />
        <DataCard title="Evenements 7j" value={113} unit="" icon={Eye} color="#FF6B35" />
        <DataCard title="Especes detectees" value={7} unit="/8" icon={Target} color="#9B59B6" />
      </div>
      <div style={{ marginTop: 16 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.6)", marginBottom: 8 }}>Cameras enregistrees</div>
        {demoCameras.map((cam) => (
          <div key={cam.id} className="saline-stat-card" style={{ marginBottom: 8, borderLeft: `3px solid ${cam.status === "active" ? "#2ECC71" : "#E74C3C"}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.9)" }}>{cam.name}</div>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }}>{cam.model} | Direction: {cam.direction}</div>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>
                  Especes: {cam.species_detected.map((sp, j) => (
                    <span key={j} style={{ display: "inline-block", background: "rgba(255,107,53,0.15)", border: "1px solid rgba(255,107,53,0.3)", borderRadius: 4, padding: "1px 6px", marginRight: 4, marginBottom: 2, fontSize: 9, color: "#FF6B35" }}>{sp}</span>
                  ))}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#FF6B35" }}>{cam.events}</div>
                <div style={{ fontSize: 9, color: "rgba(255,255,255,0.3)" }}>evenements</div>
              </div>
            </div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", marginTop: 6 }}>
              Dernier: {cam.last}
            </div>
          </div>
        ))}
      </div>
      <div className="saline-stat-card" style={{ marginTop: 16, textAlign: "center", padding: 20 }}>
        <Camera size={24} style={{ color: "rgba(255,255,255,0.2)", marginBottom: 8 }} />
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)" }}>Module cameras en mode LOCKED</div>
        <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", marginTop: 4 }}>Activation via Master Switch (directive x3000)</div>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 06: PLANIFICATEUR CHASSE
// ═══════════════════════════════════════
const PlannerModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const preds = data?.predictions || [];

  const demoTrips = [
    { id: 1, date: "2026-03-22", zone: "Zone Nord", duration: "4h30", observations: 3, species: "orignal", score: 78 },
    { id: 2, date: "2026-03-20", zone: "Corridor Est", duration: "3h15", observations: 1, species: "chevreuil", score: 62 },
    { id: 3, date: "2026-03-18", zone: "Saline Sud", duration: "5h00", observations: 5, species: "orignal", score: 91 },
  ];

  return (
    <div data-testid="module-planner">
      <h3 className="saline-section-title" style={{ color: "#F39C12" }}>
        <Calendar size={18} /> Planificateur Chasse
      </h3>
      <div className="saline-stat-card" style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "#F39C12", marginBottom: 8 }}>Creneaux optimaux (aujourd'hui)</div>
        {preds.length > 0 ? preds.slice(0, 2).map((p, i) => (
          <div key={i} style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.7)", textTransform: "capitalize" }}>{p.species}</div>
            {p.optimal_windows?.map((w, j) => (
              <div key={j} style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                <Clock size={10} style={{ color: "#4ECDC4" }} />
                <span style={{ fontSize: 12, color: "#4ECDC4" }}>{w.start} - {w.end}</span>
                <span style={{ fontSize: 10, color: "rgba(255,255,255,0.3)" }}>Score: {w.score}</span>
              </div>
            ))}
          </div>
        )) : <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)" }}>Aucune prediction disponible</div>}
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.6)", marginBottom: 8 }}>Historique sorties</div>
      {demoTrips.map((trip) => (
        <div key={trip.id} className="saline-stat-card" style={{ marginBottom: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.8)" }}>{trip.zone}</div>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }}>{trip.date} | {trip.duration} | {trip.observations} obs.</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: trip.score > 80 ? "#2ECC71" : "#F39C12" }}>{trip.score}</div>
              <div style={{ fontSize: 9, color: "rgba(255,255,255,0.3)" }}>score</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 07: ZONES ALIMENTATION
// ═══════════════════════════════════════
const FeedingModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const eco = data;

  return (
    <div data-testid="module-feeding">
      <h3 className="saline-section-title" style={{ color: "#2ECC71" }}>
        <Leaf size={18} /> Zones Alimentation
      </h3>
      {eco?.vegetation && (
        <div className="saline-stat-card" style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#2ECC71", marginBottom: 12 }}>Profil Vegetation</div>
          <ProgressBar label="Qualite fourragere" value={eco.vegetation.forage_quality} color="#2ECC71" />
          <ProgressBar label="Disponibilite brout" value={eco.vegetation.browse_availability} color="#27AE60" />
          <ProgressBar label="Couvert forestier" value={eco.vegetation.canopy_cover_pct} color="#1ABC9C" />
          <div style={{ marginTop: 8, fontSize: 11, color: "rgba(255,255,255,0.5)" }}>
            Type dominant: <span style={{ color: "#2ECC71" }}>{eco.vegetation.dominant_type}</span>
            <span style={{ margin: "0 8px" }}>|</span>
            Production mast: <span style={{ color: "#F39C12" }}>{eco.vegetation.mast_production}</span>
          </div>
        </div>
      )}
      {eco?.soil && (
        <div className="saline-stat-card" style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#FF6B35", marginBottom: 12 }}>Profil Sol</div>
          <div className="saline-grid-3">
            <DataCard title="pH" value={eco.soil.ph} unit="" icon={Mountain} color="#FF6B35" />
            <DataCard title="Matiere organique" value={eco.soil.organic_matter_pct} unit="%" icon={TreePine} color="#2ECC71" />
            <DataCard title="Humidite" value={eco.soil.moisture_pct} unit="%" icon={Droplets} color="#3498DB" />
          </div>
        </div>
      )}
      {eco?.minerals && (
        <div className="saline-stat-card">
          <div style={{ fontSize: 12, fontWeight: 600, color: "#E67E22", marginBottom: 8 }}>Mineraux & Carences</div>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginBottom: 8 }}>
            Priorite supplementation: <span style={{ color: eco.minerals.supplementation_priority === "high" ? "#E74C3C" : "#F39C12", fontWeight: 600 }}>{eco.minerals.supplementation_priority}</span>
          </div>
          {Object.entries(eco.minerals.deficiency_risk || {}).map(([min, level]) => (
            <div key={min} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", fontSize: 12 }}>
              <span style={{ color: "rgba(255,255,255,0.6)", textTransform: "capitalize" }}>{min}</span>
              <span style={{ color: level === "high" ? "#E74C3C" : level === "moderate" ? "#F39C12" : "#2ECC71" }}>{level}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 08: SUIVI GPS INTELLIGENT
// ═══════════════════════════════════════
const GpsModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const spatial = data?.spatial_analysis;

  const demoSessions = [
    { id: 1, date: "2026-03-24", distance: "4.2 km", duration: "3h15", points: 342, zones: 4 },
    { id: 2, date: "2026-03-22", distance: "6.8 km", duration: "5h00", points: 567, zones: 6 },
    { id: 3, date: "2026-03-20", distance: "3.1 km", duration: "2h45", points: 256, zones: 3 },
  ];

  return (
    <div data-testid="module-gps">
      <h3 className="saline-section-title" style={{ color: "#3498DB" }}>
        <Navigation size={18} /> Suivi GPS Intelligent
      </h3>
      <div className="saline-grid-3">
        <DataCard title="Sessions 7j" value={demoSessions.length} unit="" icon={Radio} color="#3498DB" />
        <DataCard title="Distance totale" value="14.1" unit="km" icon={Navigation} color="#2ECC71" />
        <DataCard title="Couverture" value={spatial?.territory_coverage_pct || 65} unit="%" icon={Layers} color="#9B59B6" />
      </div>
      {spatial?.zone_preferences && (
        <div className="saline-stat-card" style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#3498DB", marginBottom: 12 }}>Preferences de zones</div>
          {Object.entries(spatial.zone_preferences).map(([zone, pct]) => (
            <ProgressBar key={zone} label={zone.replace(/_/g, " ")} value={pct * 100} color="#3498DB" />
          ))}
        </div>
      )}
      <div style={{ marginTop: 16, fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.6)", marginBottom: 8 }}>Sessions recentes</div>
      {demoSessions.map((s) => (
        <div key={s.id} className="saline-stat-card" style={{ marginBottom: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.8)" }}>{s.date}</div>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }}>{s.duration} | {s.points} points | {s.zones} zones</div>
            </div>
            <div style={{ fontSize: 14, fontWeight: 700, color: "#3498DB" }}>{s.distance}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 09: ALERTES INTELLIGENTES
// ═══════════════════════════════════════
const AlertsModule = ({ loading }) => {
  if (loading) return <ModuleLoader />;

  const demoAlerts = [
    { id: 1, type: "camera", title: "Detection Camera Saline Nord", message: "Orignal detecte a 06:32", time: "Il y a 2h", priority: "high", read: false },
    { id: 2, type: "weather", title: "Conditions optimales demain", message: "Pression en hausse + temp. 8C — creneau ideal 06:00-08:00", time: "Il y a 5h", priority: "medium", read: false },
    { id: 3, type: "prediction", title: "Pic d'activite prevu", message: "Periode solunaire majeure 17:30-19:30", time: "Il y a 8h", priority: "medium", read: true },
    { id: 4, type: "territory", title: "Score territoire en hausse", message: "Zone Nord: score passe de 62 a 78", time: "Hier", priority: "low", read: true },
  ];

  return (
    <div data-testid="module-alerts">
      <h3 className="saline-section-title" style={{ color: "#E67E22" }}>
        <Bell size={18} /> Alertes Intelligentes
      </h3>
      <div className="saline-grid-3">
        <DataCard title="Non lues" value={2} unit="" icon={Bell} color="#E74C3C" />
        <DataCard title="Aujourd'hui" value={2} unit="" icon={Clock} color="#F39C12" />
        <DataCard title="Total 7j" value={demoAlerts.length} unit="" icon={BarChart3} color="#4ECDC4" />
      </div>
      <div style={{ marginTop: 16 }}>
        {demoAlerts.map((a) => (
          <div key={a.id} className="saline-stat-card" style={{
            marginBottom: 8,
            borderLeft: `3px solid ${a.priority === "high" ? "#E74C3C" : a.priority === "medium" ? "#F39C12" : "#4ECDC4"}`,
            opacity: a.read ? 0.6 : 1,
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                {!a.read && <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: "#E74C3C", marginRight: 6 }} />}
                <span style={{ fontSize: 12, fontWeight: a.read ? 400 : 600, color: "rgba(255,255,255,0.9)" }}>{a.title}</span>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>{a.message}</div>
              </div>
              <span style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", whiteSpace: "nowrap" }}>{a.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE 10: SCORE TERRITOIRE
// ═══════════════════════════════════════
const ScoreModule = ({ data, loading }) => {
  if (loading) return <ModuleLoader />;
  const scoring = data?.scoring;
  const recs = data?.recommendations || [];

  return (
    <div data-testid="module-score">
      <h3 className="saline-section-title" style={{ color: "#1ABC9C" }}>
        <Award size={18} /> Score Territoire
      </h3>
      {scoring && (
        <>
          <div style={{ textAlign: "center", marginBottom: 20 }}>
            <ScoreGauge value={scoring.global_score} label="Score Global" color={scoring.global_score > 70 ? "#2ECC71" : scoring.global_score > 50 ? "#F39C12" : "#E74C3C"} size={160} />
            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 8 }}>
              Tendance: <span style={{ color: scoring.trend === "improving" ? "#2ECC71" : "#F39C12" }}>{scoring.trend}</span>
              <span style={{ margin: "0 8px" }}>|</span>
              Percentile: <span style={{ color: "#4ECDC4" }}>{scoring.rank_percentile}%</span>
            </div>
          </div>
          <div className="saline-stat-card" style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#1ABC9C", marginBottom: 12 }}>Decomposition du score</div>
            <ProgressBar label="Habitat" value={scoring.habitat_score} color="#27AE60" />
            <ProgressBar label="Alimentation" value={scoring.food_score} color="#2ECC71" />
            <ProgressBar label="Eau" value={scoring.water_score} color="#3498DB" />
            <ProgressBar label="Couvert" value={scoring.cover_score} color="#9B59B6" />
            <ProgressBar label="Tranquillite" value={scoring.disturbance_score} color="#E67E22" />
          </div>
        </>
      )}
      {recs.length > 0 && (
        <div className="saline-stat-card">
          <div style={{ fontSize: 12, fontWeight: 600, color: "#FF6B35", marginBottom: 8 }}>Recommandations</div>
          {recs.map((r, i) => (
            <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: r.priority === "high" ? "#E74C3C" : r.priority === "medium" ? "#F39C12" : "#2ECC71" }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: "rgba(255,255,255,0.8)" }}>{r.title}</span>
              </div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 2, marginLeft: 12 }}>{r.description}</div>
              <div style={{ fontSize: 10, color: "#4ECDC4", marginTop: 2, marginLeft: 12 }}>{r.action}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════
// MODULE LOADER
// ═══════════════════════════════════════
const ModuleLoader = () => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 60 }}>
    <Loader2 size={24} style={{ color: "#FF6B35", animation: "spin 1s linear infinite" }} />
    <span style={{ marginLeft: 12, fontSize: 13, color: "rgba(255,255,255,0.4)" }}>Chargement des donnees...</span>
  </div>
);

// ═══════════════════════════════════════
// MAIN PAGE
// ═══════════════════════════════════════
export default function BionicModulesPage() {
  const [activeModule, setActiveModule] = useState("predictions");
  const [species, setSpecies] = useState("orignal");
  const [lat, setLat] = useState(47.3);
  const [lng, setLng] = useState(-71.2);
  const [loading, setLoading] = useState(false);
  const [ecoData, setEcoData] = useState(null);
  const [predData, setPredData] = useState(null);
  const [behaviorData, setBehaviorData] = useState(null);
  const [localSpecies, setLocalSpecies] = useState([]);
  const [jurisdiction, setJurisdiction] = useState(null);

  // Fetch biogeographic filter for current coordinates
  const fetchBioFilter = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/v1/ecological-intelligence/biogeography/jurisdiction?lat=${lat}&lng=${lng}`).catch(() => null);
      if (res?.data?.species_present) {
        setLocalSpecies(res.data.species_present);
        setJurisdiction({ country: res.data.country, province: res.data.province, total: res.data.total_species_present, huntable: res.data.total_huntable });
      }
    } catch (err) { console.error("Bio filter error:", err); }
  }, [lat, lng]);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    try {
      const [ecoRes, predRes, behavRes] = await Promise.all([
        axios.get(`${API}/v1/ecological-intelligence/analyze?lat=${lat}&lng=${lng}&species=${species}&radius_m=1000`).catch(() => null),
        axios.get(`${API}/v1/ecological-intelligence/predictions?lat=${lat}&lng=${lng}&species=${species}`).catch(() => null),
        axios.get(`${API}/v1/ecological-intelligence/behavior-pipeline?lat=${lat}&lng=${lng}&species=${species}`).catch(() => null),
      ]);
      if (ecoRes?.data) setEcoData(ecoRes.data);
      if (predRes?.data) setPredData(predRes.data);
      if (behavRes?.data) setBehaviorData(behavRes.data);
    } catch (err) {
      console.error("Erreur chargement:", err);
    }
    setLoading(false);
  }, [lat, lng, species]);

  useEffect(() => { fetchBioFilter(); }, [fetchBioFilter]);
  useEffect(() => { fetchAllData(); }, [fetchAllData]);

  // Filter displayed species by biogeography
  const filteredSpecies = localSpecies.length > 0
    ? SPECIES.filter(s => localSpecies.includes(s.value))
    : SPECIES;

  const renderModule = () => {
    switch (activeModule) {
      case "predictions": return <PredictionsModule data={predData} loading={loading} />;
      case "meteo": return <MeteoModule data={ecoData} loading={loading} />;
      case "behavioral-map": return <BehavioralMapModule data={behaviorData} loading={loading} />;
      case "territory": return <TerritoryModule data={ecoData} loading={loading} />;
      case "cameras": return <CamerasModule loading={loading} />;
      case "planner": return <PlannerModule data={predData} loading={loading} />;
      case "feeding": return <FeedingModule data={ecoData} loading={loading} />;
      case "gps": return <GpsModule data={behaviorData} loading={loading} />;
      case "alerts": return <AlertsModule loading={loading} />;
      case "score": return <ScoreModule data={ecoData} loading={loading} />;
      default: return null;
    }
  };

  const activeModuleData = MODULES.find(m => m.id === activeModule);

  return (
    <div className="saline-page" data-testid="bionic-modules-page">
      {/* HEADER */}
      <div className="saline-hero" style={{ paddingBottom: 20, minHeight: "auto" }}>
        <h1 className="saline-hero-title" style={{ fontSize: "1.5rem" }}>BIONIC Intelligence</h1>
        <p className="saline-hero-subtitle" style={{ fontSize: "0.8rem" }}>Ecosysteme unifie — 10 modules predictifs</p>
        {jurisdiction && (
          <div data-testid="jurisdiction-badge" style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "rgba(78,205,196,0.12)", border: "1px solid rgba(78,205,196,0.3)", borderRadius: 6, padding: "4px 12px", marginTop: 8, fontSize: 11, color: "#4ECDC4" }}>
            <MapPin size={11} /> {jurisdiction.country}/{jurisdiction.province} — {jurisdiction.total} especes presentes ({jurisdiction.huntable} chassables)
          </div>
        )}

        {/* CONTROLS */}
        <div style={{ display: "flex", gap: 12, justifyContent: "center", marginTop: 12, flexWrap: "wrap" }}>
          <select value={species} onChange={e => setSpecies(e.target.value)}
            data-testid="species-selector"
            style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 6, color: "#fff", padding: "6px 12px", fontSize: 12 }}>
            {filteredSpecies.map(s => <option key={s.value} value={s.value} style={{ background: "#1a1a2e" }}>{s.label}</option>)}
          </select>
          <input type="number" value={lat} onChange={e => setLat(parseFloat(e.target.value) || 0)} step="0.1"
            data-testid="lat-input"
            style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 6, color: "#fff", padding: "6px 10px", fontSize: 12, width: 90 }}
            placeholder="Lat" />
          <input type="number" value={lng} onChange={e => setLng(parseFloat(e.target.value) || 0)} step="0.1"
            data-testid="lng-input"
            style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 6, color: "#fff", padding: "6px 10px", fontSize: 12, width: 90 }}
            placeholder="Lng" />
          <button onClick={fetchAllData} data-testid="refresh-data-btn"
            style={{ background: "rgba(255,107,53,0.2)", border: "1px solid rgba(255,107,53,0.4)", borderRadius: 6, color: "#FF6B35", padding: "6px 14px", fontSize: 12, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
            <RefreshCw size={12} /> Actualiser
          </button>
        </div>
      </div>

      {/* MODULE TABS */}
      <div style={{ display: "flex", gap: 4, overflowX: "auto", padding: "0 16px", marginBottom: 16, scrollbarWidth: "none" }}>
        {MODULES.map(m => {
          const Icon = m.icon;
          const isActive = activeModule === m.id;
          return (
            <button key={m.id} onClick={() => setActiveModule(m.id)}
              data-testid={`tab-${m.id}`}
              style={{
                display: "flex", alignItems: "center", gap: 6, padding: "8px 14px",
                background: isActive ? `${m.color}22` : "rgba(255,255,255,0.03)",
                border: `1px solid ${isActive ? `${m.color}66` : "rgba(255,255,255,0.08)"}`,
                borderRadius: 8, color: isActive ? m.color : "rgba(255,255,255,0.5)",
                fontSize: 11, fontWeight: isActive ? 600 : 400, cursor: "pointer",
                whiteSpace: "nowrap", transition: "all 0.2s ease", flexShrink: 0,
              }}>
              <Icon size={13} />{m.label}
            </button>
          );
        })}
      </div>

      {/* MODULE CONTENT */}
      <div style={{ padding: "0 16px 40px" }}>
        {renderModule()}
      </div>

      {/* MASTER SWITCH STATUS */}
      <div style={{ textAlign: "center", padding: "20px 0 40px", borderTop: "1px solid rgba(255,255,255,0.05)" }}>
        <div style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", letterSpacing: 2, textTransform: "uppercase" }}>
          Master Switch: LOCKED | STEEVE-MAX x2260 | Filtrage biogeographique actif | Branche Work1
        </div>
      </div>
    </div>
  );
}
