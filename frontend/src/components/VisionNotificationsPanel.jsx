/**
 * VisionNotificationsPanel — Panneau de notifications IA
 * VIS-E: 7 types de notifications IA intégrées
 */
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Bell, Crown, Activity, MapPin, AlertTriangle, Route, Eye,
  Loader2, X, ChevronRight
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const NOTIF_ICONS = {
  alpha_detected: Crown,
  activity_spike: Activity,
  corridor_active: Route,
  encounter_high: Eye,
  anomaly_activity_drop: AlertTriangle,
  anomaly_alpha_disappearance: AlertTriangle,
  anomaly_camera_offline: AlertTriangle,
  anomaly_species_disappearance: AlertTriangle
};

const NOTIF_COLORS = {
  high: 'border-l-amber-500 bg-amber-500/5',
  medium: 'border-l-blue-500 bg-blue-500/5',
  low: 'border-l-zinc-500 bg-zinc-500/5'
};

const VisionNotificationsPanel = ({ token, isOpen, onClose }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API}/v1/vision/notifications`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(res.data.notifications || []);
    } catch (err) {
      console.error('Notifications load error:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { if (isOpen) load(); }, [isOpen, load]);

  if (!isOpen) return null;

  return (
    <div className="fixed right-0 top-14 w-80 max-h-[70vh] bg-zinc-950 border-l border-zinc-800 shadow-2xl z-50 flex flex-col" data-testid="vision-notifications-panel">
      <div className="flex items-center justify-between p-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Bell className="h-4 w-4 text-amber-500" />
          <span className="text-sm font-medium text-white">Alertes IA</span>
          {notifications.length > 0 && (
            <Badge className="text-[10px] bg-amber-500/20 text-amber-400">{notifications.length}</Badge>
          )}
        </div>
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {loading && <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin text-amber-500" /></div>}
        {!loading && notifications.length === 0 && (
          <div className="text-center py-8 text-zinc-500 text-xs">
            <Bell className="h-6 w-6 mx-auto mb-2 text-zinc-600" />
            Aucune alerte IA
          </div>
        )}
        {notifications.map(n => {
          const Icon = NOTIF_ICONS[n.type] || Bell;
          return (
            <div key={n.id} className={`p-3 border-b border-zinc-800/50 border-l-2 ${NOTIF_COLORS[n.priority] || NOTIF_COLORS.low}`} data-testid={`notif-${n.id}`}>
              <div className="flex items-start gap-2">
                <Icon className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-zinc-200">{n.title}</p>
                  <p className="text-[10px] text-zinc-500 mt-0.5">{n.detail}</p>
                  {n.timestamp && (
                    <p className="text-[10px] text-zinc-600 mt-0.5">{new Date(n.timestamp).toLocaleString('fr-CA')}</p>
                  )}
                </div>
                <Badge className={`text-[9px] flex-shrink-0 ${n.priority === 'high' ? 'bg-amber-500/20 text-amber-400' : 'bg-zinc-700 text-zinc-400'}`}>
                  {n.priority}
                </Badge>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default VisionNotificationsPanel;
