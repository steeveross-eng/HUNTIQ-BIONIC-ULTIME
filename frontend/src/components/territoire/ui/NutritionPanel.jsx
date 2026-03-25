/**
 * NutritionPanel — Panneau recommandations nutritionnelles ALIMENTATION-V2
 * ========================================================================
 * x4515-FIX: PinnablePanel V2 applique — Fixer/Detacher/Pleine page/Scroll
 */
import { Droplets } from 'lucide-react';
import PinnablePanel from '../PinnablePanel';

export function NutritionPanel({ alimentationV2Data, onClose }) {
  if (!alimentationV2Data) return null;
  return (
    <div className="fixed right-4 top-24 z-[1001]" style={{ width: 380 }}>
      <PinnablePanel
        title="Alimentation V2"
        subtitle={`${alimentationV2Data.species_nom || ''} — Score: ${alimentationV2Data.score_global || 0}/100`}
        icon={Droplets}
        accentColor="#f5a623"
        onClose={onClose}
        defaultWidth={380}
        maxHeight="70vh"
        testId="nutrition-panel"
      >
        <div className="p-4 space-y-4">
          {/* Score global */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">{alimentationV2Data.species_nom}</span>
            <span className="text-xl font-bold text-yellow-400">{alimentationV2Data.score_global}/100</span>
          </div>

          {/* Carences detectees */}
          {alimentationV2Data.carences_detectees?.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-red-400">Carences detectees</div>
              {alimentationV2Data.carences_detectees.map((c, i) => (
                <div key={i} className="flex items-center justify-between text-sm bg-red-500/10 rounded-lg px-3 py-2">
                  <span className="text-red-300">{c.element}</span>
                  <span className="text-red-400 font-bold">-{c.deficit_pct}%</span>
                </div>
              ))}
            </div>
          )}

          {/* Aliments recommandes */}
          <div className="space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-green-400">Aliments recommandes</div>
            {alimentationV2Data.nutrition?.aliments_recommandes?.map((a, i) => (
              <div key={i} className="text-sm bg-gray-800/50 rounded-lg px-3 py-2">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">{a.nom}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${a.priorite === 'haute' ? 'bg-red-500/20 text-red-300' : 'bg-gray-700 text-gray-400'}`}>{a.priorite}</span>
                </div>
                <div className="text-sm text-gray-500 mt-0.5">{a.saison} — {a.apport}</div>
              </div>
            ))}
          </div>

          {/* Proteines */}
          {alimentationV2Data.nutrition?.proteines && (
            <div className="space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-blue-400">Proteines</div>
              <div className="text-sm text-gray-300">Besoin: <span className="text-blue-300 font-bold">{alimentationV2Data.nutrition.proteines.besoin_pct}%</span></div>
              <div className="text-sm text-gray-500">{alimentationV2Data.nutrition.proteines.note}</div>
            </div>
          )}

          {/* Oligo-elements */}
          <div className="space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-purple-400">Oligo-elements</div>
            {alimentationV2Data.nutrition?.oligo_elements?.map((o, i) => (
              <div key={i} className="flex items-center justify-between text-sm bg-gray-800/50 rounded-lg px-3 py-2">
                <span className="text-gray-300">{o.nom}</span>
                <span className="text-purple-300">{o.besoin_mg_jour} mg/j</span>
              </div>
            ))}
          </div>

          {/* Saline composition */}
          {alimentationV2Data.nutrition?.saline_composition && !alimentationV2Data.salines_disabled && (
            <div className="space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-yellow-400">Composition saline recommandee</div>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(alimentationV2Data.nutrition.saline_composition).map(([k, v]) => (
                  <div key={k} className="text-sm bg-yellow-500/10 rounded-lg px-3 py-2">
                    <span className="text-gray-400">{k.replace('_pct', ' %').replace('_ppm', ' ppm').replace('_', ' ')}: </span>
                    <span className="text-yellow-300 font-bold">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Salines disabled message */}
          {alimentationV2Data.salines_disabled && alimentationV2Data.salines_message && (
            <div className="px-4 py-3 bg-amber-900/20 border border-amber-700/30 rounded-lg" data-testid="nutrition-panel-salines-message">
              <div className="text-sm text-amber-300/90 leading-relaxed">{alimentationV2Data.salines_message}</div>
            </div>
          )}

          {/* Carences locales Quebec */}
          {alimentationV2Data.nutrition?.carences_locales?.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-bold uppercase tracking-wider text-orange-400">Carences locales (Quebec)</div>
              {alimentationV2Data.nutrition.carences_locales.map((c, i) => (
                <div key={i} className="text-sm text-orange-300/80 pl-3 border-l-2 border-orange-500/30">{c}</div>
              ))}
            </div>
          )}
        </div>
      </PinnablePanel>
    </div>
  );
}
