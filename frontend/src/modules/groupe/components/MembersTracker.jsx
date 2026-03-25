/**
 * MembersTracker — x4500-ULTRA stub
 * Composant de suivi des membres du groupe
 */
import React from 'react';

export const MembersTracker = ({ groupId, members = [] }) => {
  return (
    <div data-testid="members-tracker" className="p-4">
      <h3 className="font-semibold text-sm mb-2">Membres actifs</h3>
      {members.length === 0 ? (
        <p className="text-xs text-gray-500">Aucun membre en ligne</p>
      ) : (
        <ul className="space-y-1">
          {members.map((m, i) => (
            <li key={i} className="text-xs flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              {m.name || `Membre ${i + 1}`}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default MembersTracker;
