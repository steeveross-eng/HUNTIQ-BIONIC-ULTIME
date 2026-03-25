/**
 * ScoreCompare — x4500-ULTRA stub
 * Comparaison de scores entre sites/periodes
 */
import React from 'react';

export const ScoreCompare = ({ scores = [], species = 'CERF' }) => {
  return (
    <div data-testid="score-compare" className="p-4">
      <h3 className="font-semibold text-sm mb-2">Comparaison de scores</h3>
      {scores.length === 0 ? (
        <p className="text-xs text-gray-500">Aucun score a comparer</p>
      ) : (
        <div className="space-y-2">
          {scores.map((s, i) => (
            <div key={i} className="flex justify-between text-xs">
              <span>{s.label || `Site ${i + 1}`}</span>
              <span className="font-mono font-bold">{s.score || 0}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScoreCompare;
