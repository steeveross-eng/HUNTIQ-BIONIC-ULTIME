/**
 * BCE-4X — Utilitaires Meteo BIONIC
 * ==================================
 * PURGE OWM COMPLETE — 2026-03-28
 * Seules les fonctions utilitaires actives sont conservees.
 * Source meteo unique: /api/v3/weather (Open-Meteo via weather_v3)
 */

/**
 * Convertit un angle en degres en direction cardinale textuelle.
 * @param {number} degrees - Angle du vent (0-360)
 * @returns {string} Direction (N, NNE, NE, ENE, E, etc.)
 */
export const getWindDirectionText = (degrees) => {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO'];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
};

/**
 * Code meteo WMO en description francaise.
 * @param {number} code - Code WMO standard
 * @returns {string} Description
 */
export const getWeatherDescription = (code) => {
  const descriptions = {
    0: 'Ciel degage',
    1: 'Principalement degage',
    2: 'Partiellement nuageux',
    3: 'Couvert',
    45: 'Brouillard',
    48: 'Brouillard givrant',
    51: 'Bruine legere',
    53: 'Bruine moderee',
    55: 'Bruine dense',
    61: 'Pluie legere',
    63: 'Pluie moderee',
    65: 'Pluie forte',
    71: 'Neige legere',
    73: 'Neige moderee',
    75: 'Neige forte',
    80: 'Averses legeres',
    81: 'Averses moderees',
    82: 'Averses violentes',
    95: 'Orage',
    96: 'Orage avec grele legere',
    99: 'Orage avec grele forte',
  };
  return descriptions[code] || 'Inconnu';
};

export default {
  getWindDirectionText,
  getWeatherDescription,
};
