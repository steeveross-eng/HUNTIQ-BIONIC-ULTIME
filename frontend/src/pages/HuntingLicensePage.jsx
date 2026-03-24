/**
 * HuntingLicensePage — Module Permis + Enregistrement du gibier
 * STEEVE-MAX x2200-FINAL-V2 + x2290-V3
 *
 * Onglets: Achat de Permis | Enregistrement du gibier
 * Filtrage biogeographique obligatoire (x2260-V2)
 */
import React, { useState, useMemo, useEffect, useCallback } from 'react';
import axios from 'axios';
import { ExternalLink, MapPin, FileText, Shield, ClipboardList, Search, CheckCircle2, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { GlobalContainer } from '@/core/layouts';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const HUNTING_LICENSE_DATA = {
  canada: {
    label: "Canada", flag: "\u{1F1E8}\u{1F1E6}", code: "CA",
    regions: [
      { id: "qc", code: "QC", name: "Quebec", url: "https://www.quebec.ca/tourisme-loisirs-sport/activites-sportives-et-de-plein-air/chasse-sportive/permis-certificat/acheter-permis", regUrl: "https://www.quebec.ca/tourisme-loisirs-sport/activites-sportives-et-de-plein-air/chasse-sportive/enregistrement-gibier" },
      { id: "on", code: "ON", name: "Ontario", url: "https://www.huntandfishontario.com", regUrl: "https://www.ontario.ca/page/report-hunting-kills" },
      { id: "on-nr", code: "ON", name: "Ontario (non-residents)", url: "https://www.ontario.ca/page/hunting-licence-non-residents", regUrl: "https://www.ontario.ca/page/report-hunting-kills" },
      { id: "sk", code: "SK", name: "Saskatchewan", url: "https://hal.saskatchewan.ca", regUrl: "https://hal.saskatchewan.ca" },
      { id: "ab", code: "AB", name: "Alberta", url: "https://www.albertarelm.com", regUrl: "https://www.albertarelm.com" },
      { id: "bc", code: "BC", name: "British Columbia", url: "https://www2.gov.bc.ca/gov/content/sports-culture/recreation/fishing-hunting/hunting", regUrl: "https://www2.gov.bc.ca/gov/content/sports-culture/recreation/fishing-hunting/hunting/mandatory-reporting" },
      { id: "mb", code: "MB", name: "Manitoba", url: "https://www.manitobaelicensing.ca", regUrl: "https://www.manitobaelicensing.ca" },
      { id: "nb", code: "NB", name: "New Brunswick", url: "https://www.gnb.ca/naturalresources", regUrl: "https://www.gnb.ca/naturalresources" },
      { id: "ns", code: "NS", name: "Nova Scotia", url: "https://www.hmc.gov.ns.ca", regUrl: "https://www.hmc.gov.ns.ca" },
      { id: "pe", code: "PE", name: "Prince Edward Island", url: "https://www.princeedwardisland.ca/en/topic/hunting-and-fishing", regUrl: "https://www.princeedwardisland.ca/en/topic/hunting-and-fishing" },
      { id: "nl", code: "NL", name: "Newfoundland & Labrador", url: "https://www.gov.nl.ca/ffa/wildlife/hunting", regUrl: "https://www.gov.nl.ca/ffa/wildlife/hunting" },
      { id: "yt", code: "YT", name: "Yukon", url: "https://yukon.ca/en/hunting-licences-permits", regUrl: "https://yukon.ca/en/hunting-licences-permits" },
      { id: "nt", code: "NT", name: "Northwest Territories", url: "https://www.enr.gov.nt.ca", regUrl: "https://www.enr.gov.nt.ca" },
      { id: "nu", code: "NU", name: "Nunavut", url: "https://www.gov.nu.ca", regUrl: "https://www.gov.nu.ca" },
    ]
  },
  usa: {
    label: "Etats-Unis", flag: "\u{1F1FA}\u{1F1F8}", code: "US",
    regions: [
      { id: "al", code: "AL", name: "Alabama", url: "https://www.outdooralabama.com", regUrl: "https://www.outdooralabama.com/game-check" },
      { id: "ak", code: "AK", name: "Alaska", url: "https://www.adfg.alaska.gov/store", regUrl: "https://www.adfg.alaska.gov/index.cfm?adfg=harvest.main" },
      { id: "az", code: "AZ", name: "Arizona", url: "https://license.azgfd.gov", regUrl: "https://license.azgfd.gov" },
      { id: "co", code: "CO", name: "Colorado", url: "https://cpw.state.co.us/buyapply", regUrl: "https://cpw.state.co.us/learn/Pages/HarvestReporting.aspx" },
      { id: "id", code: "ID", name: "Idaho", url: "https://idfg.idaho.gov/buy", regUrl: "https://idfg.idaho.gov/hunt/harvest-report" },
      { id: "me", code: "ME", name: "Maine", url: "https://www.maine.gov/ifw", regUrl: "https://www.maine.gov/ifw/hunting-trapping/harvest-reporting" },
      { id: "mi", code: "MI", name: "Michigan", url: "https://www.mdnr-elicense.com", regUrl: "https://www.michigan.gov/dnr/things-to-do/hunting/harvest-report" },
      { id: "mn", code: "MN", name: "Minnesota", url: "https://www.dnr.state.mn.us", regUrl: "https://www.dnr.state.mn.us/hunting/harvest" },
      { id: "mt", code: "MT", name: "Montana", url: "https://ols.fwp.mt.gov", regUrl: "https://ols.fwp.mt.gov" },
      { id: "nh", code: "NH", name: "New Hampshire", url: "https://www.wildlife.state.nh.us", regUrl: "https://www.wildlife.state.nh.us" },
      { id: "ny", code: "NY", name: "New York", url: "https://decals.licensing.east.kalkomey.com", regUrl: "https://www.dec.ny.gov/outdoor/8316.html" },
      { id: "or", code: "OR", name: "Oregon", url: "https://odfw.huntfishoregon.com", regUrl: "https://odfw.huntfishoregon.com" },
      { id: "pa", code: "PA", name: "Pennsylvania", url: "https://huntfish.pa.gov", regUrl: "https://huntfish.pa.gov" },
      { id: "vt", code: "VT", name: "Vermont", url: "https://vtfishandwildlife.com", regUrl: "https://vtfishandwildlife.com" },
      { id: "wa", code: "WA", name: "Washington", url: "https://fishhunt.dfw.wa.gov", regUrl: "https://fishhunt.dfw.wa.gov" },
      { id: "wi", code: "WI", name: "Wisconsin", url: "https://gowild.wi.gov", regUrl: "https://gowild.wi.gov/game-harvest-reporting" },
      { id: "wy", code: "WY", name: "Wyoming", url: "https://wgfd.wyo.gov/apply-or-buy", regUrl: "https://wgfd.wyo.gov/apply-or-buy" },
    ]
  }
};

const HuntingLicensePage = () => {
  const [activeTab, setActiveTab] = useState("permis");
  const [selectedCountry, setSelectedCountry] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("");
  const [localSpecies, setLocalSpecies] = useState([]);
  const [registrationHistory, setRegistrationHistory] = useState([]);

  const availableRegions = useMemo(() => {
    if (!selectedCountry) return [];
    return HUNTING_LICENSE_DATA[selectedCountry]?.regions || [];
  }, [selectedCountry]);

  const selectedRegionData = useMemo(() => {
    return availableRegions.find(r => r.id === selectedRegion);
  }, [selectedRegion, availableRegions]);

  const licenseUrl = selectedRegionData?.url || null;
  const registrationUrl = selectedRegionData?.regUrl || null;

  const fetchBioFilter = useCallback(async () => {
    if (!selectedCountry || !selectedRegion || !selectedRegionData) return;
    const countryCode = HUNTING_LICENSE_DATA[selectedCountry]?.code;
    const provCode = selectedRegionData.code;
    if (!countryCode || !provCode) return;
    try {
      const defaultCoords = { QC: [47.3, -71.2], ON: [44.3, -79.8], AB: [53.5, -113.5], BC: [49.3, -123.1], MB: [50.0, -97.1], SK: [52.1, -106.7] };
      const coords = defaultCoords[provCode] || [47.3, -71.2];
      const res = await axios.get(`${API}/v1/ecological-intelligence/biogeography/filter?lat=${coords[0]}&lng=${coords[1]}`);
      if (res.data?.species) setLocalSpecies(res.data.species);
    } catch { setLocalSpecies([]); }
  }, [selectedCountry, selectedRegion, selectedRegionData]);

  useEffect(() => { fetchBioFilter(); }, [fetchBioFilter]);

  const handleCountryChange = (value) => {
    setSelectedCountry(value);
    setSelectedRegion("");
    setLocalSpecies([]);
  };

  const openPortal = (url) => { if (url) window.open(url, '_blank', 'noopener,noreferrer'); };

  const TABS = [
    { id: "permis", label: "Achat de Permis", icon: FileText },
    { id: "enregistrement", label: "Enregistrement Gibier", icon: ClipboardList },
  ];

  return (
    <GlobalContainer>
      <div className="min-h-[calc(100vh-64px)] py-8 px-4" data-testid="hunting-license-page">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#f5a623]/20 mb-4">
            <Shield className="h-8 w-8 text-[#f5a623]" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">Permis & Enregistrement</h1>
          <p className="text-gray-400 max-w-xl mx-auto text-sm">Accedez aux portails officiels pour l'achat de permis et l'enregistrement obligatoire du gibier.</p>
        </div>

        {/* TABS */}
        <div className="flex justify-center gap-2 mb-8" data-testid="permis-tabs">
          {TABS.map(t => {
            const Icon = t.icon;
            return (
              <button key={t.id} onClick={() => setActiveTab(t.id)} data-testid={`tab-${t.id}`}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  activeTab === t.id
                    ? 'bg-[#f5a623]/20 text-[#f5a623] border border-[#f5a623]/40'
                    : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'
                }`}>
                <Icon className="h-4 w-4" /> {t.label}
              </button>
            );
          })}
        </div>

        <Card className="max-w-xl mx-auto bg-gray-900/50 border-gray-800" data-testid="hunting-license-card">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-xl text-white flex items-center justify-center gap-2">
              <MapPin className="h-5 w-5 text-[#f5a623]" />
              {activeTab === "permis" ? "Achat de Permis" : "Enregistrement du Gibier"}
            </CardTitle>
            <CardDescription className="text-gray-400">
              {activeTab === "permis"
                ? "Selectionnez votre localisation pour acceder au portail officiel"
                : "Enregistrez votre gibier aupres de l'autorite competente"}
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-5 pt-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Pays</label>
              <Select value={selectedCountry} onValueChange={handleCountryChange} data-testid="country-select">
                <SelectTrigger className="w-full bg-gray-800 border-gray-700 text-white h-12">
                  <SelectValue placeholder="Selectionnez un pays" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {Object.entries(HUNTING_LICENSE_DATA).map(([key, data]) => (
                    <SelectItem key={key} value={key} className="text-white hover:bg-gray-700 cursor-pointer">
                      <span className="flex items-center gap-2"><span>{data.flag}</span><span>{data.label}</span></span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Province / Etat</label>
              <Select value={selectedRegion} onValueChange={setSelectedRegion} disabled={!selectedCountry} data-testid="region-select">
                <SelectTrigger className={`w-full h-12 ${selectedCountry ? 'bg-gray-800 border-gray-700 text-white' : 'bg-gray-800/50 border-gray-700/50 text-gray-500'}`}>
                  <SelectValue placeholder={selectedCountry ? "Selectionnez une province/Etat" : "Choisissez d'abord un pays"} />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700 max-h-[300px]">
                  {availableRegions.map((region) => (
                    <SelectItem key={region.id} value={region.id} className="text-white hover:bg-gray-700 cursor-pointer">{region.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Biogeographic species badge */}
            {localSpecies.length > 0 && selectedRegion && (
              <div className="bg-[#4ECDC4]/10 border border-[#4ECDC4]/30 rounded-lg p-3" data-testid="species-bio-badge">
                <div className="flex items-center gap-2 mb-2">
                  <Search className="h-4 w-4 text-[#4ECDC4]" />
                  <span className="text-xs font-medium text-[#4ECDC4]">Especes presentes dans cette juridiction ({localSpecies.length})</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {localSpecies.map(sp => (
                    <span key={sp} className="text-[10px] bg-[#4ECDC4]/15 border border-[#4ECDC4]/25 text-[#4ECDC4] rounded px-2 py-0.5">{sp.replace(/_/g, ' ')}</span>
                  ))}
                </div>
              </div>
            )}

            {/* CTA Buttons */}
            {activeTab === "permis" ? (
              <Button onClick={() => openPortal(licenseUrl)} disabled={!licenseUrl} data-testid="buy-license-btn"
                className={`w-full h-14 text-lg font-semibold transition-all duration-300 ${licenseUrl ? 'bg-[#f5a623] hover:bg-[#e09000] text-black shadow-lg shadow-[#f5a623]/20' : 'bg-gray-700 text-gray-400 cursor-not-allowed'}`}>
                <ExternalLink className="h-5 w-5 mr-2" />
                {licenseUrl ? "Acheter mon permis" : "Selectionnez votre localisation"}
              </Button>
            ) : (
              <Button onClick={() => openPortal(registrationUrl)} disabled={!registrationUrl} data-testid="register-game-btn"
                className={`w-full h-14 text-lg font-semibold transition-all duration-300 ${registrationUrl ? 'bg-[#2ECC71] hover:bg-[#27AE60] text-black shadow-lg shadow-[#2ECC71]/20' : 'bg-gray-700 text-gray-400 cursor-not-allowed'}`}>
                <ClipboardList className="h-5 w-5 mr-2" />
                {registrationUrl ? "Enregistrer mon gibier" : "Selectionnez votre localisation"}
              </Button>
            )}

            {(licenseUrl || registrationUrl) && selectedRegionData && (
              <div className="flex items-center justify-center gap-2 text-sm text-gray-400 bg-gray-800/50 rounded-lg py-3 px-4">
                <Shield className="h-4 w-4 text-green-500" />
                <span>Redirection vers le portail officiel de <strong className="text-white">{selectedRegionData.name}</strong></span>
              </div>
            )}

            {/* Registration info */}
            {activeTab === "enregistrement" && selectedRegion && (
              <div className="bg-[#FF6B35]/10 border border-[#FF6B35]/30 rounded-lg p-4 space-y-2" data-testid="registration-info">
                <div className="flex items-center gap-2 text-[#FF6B35] font-medium text-sm">
                  <CheckCircle2 className="h-4 w-4" /> Rappel — Enregistrement obligatoire
                </div>
                <ul className="text-xs text-gray-300 space-y-1.5 ml-6">
                  <li className="flex items-start gap-2"><ChevronRight className="h-3 w-3 mt-0.5 text-[#FF6B35] flex-shrink-0" />L'enregistrement du gibier est obligatoire dans la plupart des juridictions</li>
                  <li className="flex items-start gap-2"><ChevronRight className="h-3 w-3 mt-0.5 text-[#FF6B35] flex-shrink-0" />Delai habituel : 24-48h apres la recolte</li>
                  <li className="flex items-start gap-2"><ChevronRight className="h-3 w-3 mt-0.5 text-[#FF6B35] flex-shrink-0" />Informations requises : espece, sexe, zone, date, numero de permis</li>
                  <li className="flex items-start gap-2"><ChevronRight className="h-3 w-3 mt-0.5 text-[#FF6B35] flex-shrink-0" />Un echantillon biologique peut etre exige (dent, tissu)</li>
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="max-w-xl mx-auto mt-8 text-center">
          <p className="text-xs text-gray-500">Les liens redirigent vers les sites gouvernementaux officiels. BIONIC n'est pas responsable du contenu des sites externes.</p>
        </div>
      </div>
    </GlobalContainer>
  );
};

export default HuntingLicensePage;
