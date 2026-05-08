/**
 * layer_icon_registry_omega.js — P20 cleanup · icon mapping
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Mapping fonction → lucide-react icon. Source UNIQUE.
 * V30_LOCK : INVIOLÉ.
 * ═══════════════════════════════════════════════════════════════
 */
import {
  Mountain, TreePine, SatelliteDish, Droplets, Map, Snowflake,
  Triangle, Layers, Navigation, Crosshair, Flame, Wind, Eye, Brain,
  Microscope, Target, MapPin, Binoculars, Compass, Activity, Database,
  ShieldCheck, Bitcoin, Mail, RefreshCw, FileText, BookOpen,
  HardDrive, BarChart3, Anchor,
} from 'lucide-react';

export const LAYER_ICON_REGISTRY_OMEGA = Object.freeze({
  // Couches BIO-Ω
  zones:         Layers,
  corridors:     Navigation,
  affuts:        Crosshair,
  salines:       Droplets,
  hotspots:      Flame,
  // Environnement
  vent:          Wind,
  contamination: Eye,
  sensoriel:     Compass,
  // HF
  lidar_hd:      Mountain,
  canopy:        TreePine,
  orthophoto:    SatelliteDish,
  hydrology:     Droplets,
  forest_roads:  Map,
  snow_ground:   Snowflake,
  slope_dem:     Triangle,
  // Inspection
  cursor:        Binoculars,
  bio:           Microscope,
  ndvi:          Activity,
  // Méta
  intel:         Brain,
  species:       Target,
  waypoint:      MapPin,
  // Doctrine BCE-4X
  merkle:        Anchor,
  bitcoin:       Bitcoin,
  multisig:      ShieldCheck,
  validation:    BookOpen,
  messaging:     Mail,
  ots:           RefreshCw,
  report:        FileText,
  manual:        BookOpen,
  bundle:        HardDrive,
  visualizer:    BarChart3,
  database:      Database,
});

export default LAYER_ICON_REGISTRY_OMEGA;
