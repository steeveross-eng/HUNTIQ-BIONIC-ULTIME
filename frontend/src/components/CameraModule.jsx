/**
 * CameraModule — Module Cameras BIONIC
 * CAM-Omega: Gestion cameras, upload photos, galerie, carte
 */
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/components/GlobalAuth';
import {
  Camera, Plus, Upload, Image, Grid, List, MapPin, Clock, Eye,
  Trash2, Settings, Loader2, X, CheckCircle, AlertCircle, RefreshCw,
  Activity, BarChart3, Filter, ChevronRight, Copy, ArrowLeft
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MANUFACTURERS = [
  { value: 'spypoint', label: 'Spypoint' },
  { value: 'tactacam', label: 'Tactacam' },
  { value: 'cuddeback', label: 'Cuddeback' },
  { value: 'bushnell', label: 'Bushnell' },
  { value: 'moultrie', label: 'Moultrie' },
  { value: 'reconyx', label: 'Reconyx' },
  { value: 'stealth_cam', label: 'Stealth Cam' },
  { value: 'browning', label: 'Browning' },
  { value: 'wildgame', label: 'Wildgame' },
  { value: 'other', label: 'Autre' }
];

const STATUS_COLORS = {
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  inactive: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  maintenance: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  offline: 'bg-red-500/20 text-red-400 border-red-500/30'
};

const getAuthHeaders = (token) => ({
  headers: { Authorization: `Bearer ${token}` }
});

const CameraModule = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState('cameras');

  // Data
  const [cameras, setCameras] = useState([]);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showCreateCamera, setShowCreateCamera] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [showCameraDetail, setShowCameraDetail] = useState(false);

  // Upload state
  const [uploadFiles, setUploadFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadCameraId, setUploadCameraId] = useState('');

  // Create camera form
  const [newCamera, setNewCamera] = useState({
    name: '', manufacturer: 'spypoint', model: '', serial: '',
    waypoint_id: '', gps_lat: '', gps_lon: '', integration_type: 'manual'
  });

  // Load data
  const loadCameras = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API}/v1/camera/cameras`, getAuthHeaders(token));
      setCameras(res.data.cameras || []);
    } catch (err) {
      console.error('Error loading cameras:', err);
    }
  }, [token]);

  const loadEvents = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API}/v1/camera/events?limit=50`, getAuthHeaders(token));
      setEvents(res.data.events || []);
    } catch (err) {
      console.error('Error loading events:', err);
    }
  }, [token]);

  const loadStats = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get(`${API}/v1/camera/stats`, getAuthHeaders(token));
      setStats(res.data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      setLoading(true);
      Promise.all([loadCameras(), loadEvents(), loadStats()])
        .finally(() => setLoading(false));
    }
  }, [token, loadCameras, loadEvents, loadStats]);

  // Create camera
  const handleCreateCamera = async () => {
    if (!newCamera.name || !newCamera.waypoint_id) {
      toast.error('Nom et waypoint sont obligatoires');
      return;
    }
    try {
      const payload = {
        ...newCamera,
        gps_lat: newCamera.gps_lat ? parseFloat(newCamera.gps_lat) : null,
        gps_lon: newCamera.gps_lon ? parseFloat(newCamera.gps_lon) : null
      };
      await axios.post(`${API}/v1/camera/cameras`, payload, getAuthHeaders(token));
      toast.success('Camera creee avec succes!');
      setShowCreateCamera(false);
      setNewCamera({ name: '', manufacturer: 'spypoint', model: '', serial: '', waypoint_id: '', gps_lat: '', gps_lon: '', integration_type: 'manual' });
      loadCameras();
      loadStats();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur lors de la creation');
    }
  };

  // Delete camera
  const handleDeleteCamera = async (cameraId) => {
    if (!confirm('Desactiver cette camera?')) return;
    try {
      await axios.delete(`${API}/v1/camera/cameras/${cameraId}`, getAuthHeaders(token));
      toast.success('Camera desactivee');
      loadCameras();
      loadStats();
    } catch (err) {
      toast.error('Erreur lors de la suppression');
    }
  };

  // Upload photos
  const handleUploadPhotos = async () => {
    if (!uploadCameraId || uploadFiles.length === 0) {
      toast.error('Selectionnez une camera et des photos');
      return;
    }
    setUploading(true);
    setUploadProgress(0);
    try {
      const formData = new FormData();
      formData.append('camera_id', uploadCameraId);
      uploadFiles.forEach(f => formData.append('files', f));

      const res = await axios.post(`${API}/v1/camera/photos/upload`, formData, {
        ...getAuthHeaders(token),
        headers: { ...getAuthHeaders(token).headers, 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          setUploadProgress(Math.round((e.loaded / e.total) * 100));
        }
      });

      toast.success(`${res.data.events_created} photo(s) importee(s)!`);
      setShowUpload(false);
      setUploadFiles([]);
      setUploadCameraId('');
      loadEvents();
      loadCameras();
      loadStats();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur lors de l\'upload');
    } finally {
      setUploading(false);
    }
  };

  // Copy email alias
  const copyEmailAlias = (alias) => {
    navigator.clipboard.writeText(alias);
    toast.success('Alias email copie!');
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center" data-testid="camera-auth-required">
        <Card className="bg-zinc-900 border-zinc-800 max-w-md">
          <CardContent className="p-8 text-center">
            <Camera className="h-12 w-12 text-amber-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Module Cameras</h2>
            <p className="text-zinc-400">Connectez-vous pour acceder a vos cameras de chasse</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-white" data-testid="camera-module">
      {/* Header */}
      <div className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)} data-testid="camera-back-btn">
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <Camera className="h-6 w-6 text-amber-500" />
            <div>
              <h1 className="text-lg font-bold">Cameras de Chasse</h1>
              <p className="text-xs text-zinc-500">Gestion et suivi de vos cameras trail</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" className="border-zinc-700" onClick={() => setShowUpload(true)} data-testid="camera-upload-btn">
              <Upload className="h-4 w-4 mr-1" /> Importer
            </Button>
            <Button size="sm" className="bg-amber-600 hover:bg-amber-700" onClick={() => setShowCreateCamera(true)} data-testid="camera-add-btn">
              <Plus className="h-4 w-4 mr-1" /> Camera
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6" data-testid="camera-stats">
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-4 text-center">
                <Camera className="h-5 w-5 text-amber-500 mx-auto mb-1" />
                <p className="text-2xl font-bold">{stats.total_cameras}</p>
                <p className="text-xs text-zinc-500">Cameras</p>
              </CardContent>
            </Card>
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-4 text-center">
                <Activity className="h-5 w-5 text-green-500 mx-auto mb-1" />
                <p className="text-2xl font-bold">{stats.active_cameras}</p>
                <p className="text-xs text-zinc-500">Actives</p>
              </CardContent>
            </Card>
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-4 text-center">
                <Image className="h-5 w-5 text-blue-500 mx-auto mb-1" />
                <p className="text-2xl font-bold">{stats.total_photos}</p>
                <p className="text-xs text-zinc-500">Photos</p>
              </CardContent>
            </Card>
            <Card className="bg-zinc-900/50 border-zinc-800">
              <CardContent className="p-4 text-center">
                <Eye className="h-5 w-5 text-purple-500 mx-auto mb-1" />
                <p className="text-2xl font-bold">{stats.total_events}</p>
                <p className="text-xs text-zinc-500">Evenements</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-zinc-900 border border-zinc-800 mb-4">
            <TabsTrigger value="cameras" data-testid="tab-cameras">Cameras</TabsTrigger>
            <TabsTrigger value="gallery" data-testid="tab-gallery">Galerie</TabsTrigger>
            <TabsTrigger value="events" data-testid="tab-events">Evenements</TabsTrigger>
          </TabsList>

          {/* CAMERAS TAB */}
          <TabsContent value="cameras">
            {loading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-amber-500" /></div>
            ) : cameras.length === 0 ? (
              <Card className="bg-zinc-900/50 border-zinc-800 border-dashed" data-testid="camera-empty-state">
                <CardContent className="p-12 text-center">
                  <Camera className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-zinc-300 mb-2">Aucune camera enregistree</h3>
                  <p className="text-zinc-500 mb-4">Ajoutez votre premiere camera de chasse pour commencer</p>
                  <Button className="bg-amber-600 hover:bg-amber-700" onClick={() => setShowCreateCamera(true)}>
                    <Plus className="h-4 w-4 mr-1" /> Ajouter une camera
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3" data-testid="camera-grid">
                {cameras.map(cam => (
                  <Card key={cam.id} className="bg-zinc-900/50 border-zinc-800 hover:border-zinc-700 transition-colors cursor-pointer" data-testid={`camera-card-${cam.id}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Camera className="h-5 w-5 text-amber-500" />
                          <div>
                            <p className="font-medium text-sm">{cam.name || 'Camera'}</p>
                            <p className="text-xs text-zinc-500">{cam.manufacturer}</p>
                          </div>
                        </div>
                        <Badge className={`text-xs ${STATUS_COLORS[cam.status] || STATUS_COLORS.inactive}`}>
                          {cam.status}
                        </Badge>
                      </div>
                      <div className="space-y-1.5 text-xs text-zinc-400">
                        {cam.model && <p>Modele: {cam.model}</p>}
                        <p className="flex items-center gap-1">
                          <Image className="h-3 w-3" /> {cam.photo_count} photos
                        </p>
                        {cam.email_alias && (
                          <div className="flex items-center gap-1">
                            <span className="truncate font-mono text-amber-400/70">{cam.email_alias}</span>
                            <Button variant="ghost" size="icon" className="h-5 w-5" onClick={(e) => { e.stopPropagation(); copyEmailAlias(cam.email_alias); }}>
                              <Copy className="h-3 w-3" />
                            </Button>
                          </div>
                        )}
                      </div>
                      <div className="flex gap-1.5 mt-3">
                        <Button size="sm" variant="outline" className="flex-1 h-7 text-xs border-zinc-700" onClick={() => { setUploadCameraId(cam.id); setShowUpload(true); }}>
                          <Upload className="h-3 w-3 mr-1" /> Upload
                        </Button>
                        <Button size="sm" variant="ghost" className="h-7 text-xs text-red-400 hover:text-red-300" onClick={() => handleDeleteCamera(cam.id)}>
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* GALLERY TAB */}
          <TabsContent value="gallery">
            {events.length === 0 ? (
              <Card className="bg-zinc-900/50 border-zinc-800 border-dashed">
                <CardContent className="p-12 text-center">
                  <Image className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-zinc-300 mb-2">Aucune photo</h3>
                  <p className="text-zinc-500">Importez des photos depuis vos cameras pour les voir ici</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3" data-testid="photo-gallery">
                {events.map(evt => (
                  <Card key={evt.id} className="bg-zinc-900/50 border-zinc-800 overflow-hidden group" data-testid={`gallery-event-${evt.id}`}>
                    <div className="aspect-square bg-zinc-800 flex items-center justify-center relative">
                      {evt.thumbnail_url ? (
                        <img src={`${API}/v1/camera/photos/${evt.id}/thumbnail`} alt="Camera" className="w-full h-full object-cover" />
                      ) : (
                        <Camera className="h-8 w-8 text-zinc-600" />
                      )}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <Eye className="h-6 w-6 text-white" />
                      </div>
                    </div>
                    <CardContent className="p-2">
                      <p className="text-xs text-zinc-400 truncate">{new Date(evt.timestamp).toLocaleString('fr-CA')}</p>
                      {evt.species && <Badge className="text-xs bg-amber-500/20 text-amber-400 mt-1">{evt.species}</Badge>}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* EVENTS TAB */}
          <TabsContent value="events">
            {events.length === 0 ? (
              <Card className="bg-zinc-900/50 border-zinc-800 border-dashed">
                <CardContent className="p-12 text-center">
                  <Activity className="h-16 w-16 text-zinc-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-zinc-300 mb-2">Aucun evenement</h3>
                  <p className="text-zinc-500">Les evenements apparaitront ici lorsque des photos seront importees</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2" data-testid="events-list">
                {events.map(evt => (
                  <Card key={evt.id} className="bg-zinc-900/50 border-zinc-800" data-testid={`event-${evt.id}`}>
                    <CardContent className="p-3 flex items-center gap-3">
                      <div className="h-10 w-10 rounded bg-zinc-800 flex items-center justify-center flex-shrink-0">
                        <Camera className="h-5 w-5 text-amber-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">Camera: {evt.camera_id?.slice(0, 8)}</p>
                        <p className="text-xs text-zinc-500">{new Date(evt.timestamp).toLocaleString('fr-CA')}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {evt.species && <Badge className="text-xs bg-green-500/20 text-green-400">{evt.species}</Badge>}
                        <Badge className="text-xs bg-zinc-700 text-zinc-300">{evt.source || 'manual'}</Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* CREATE CAMERA MODAL */}
      <Dialog open={showCreateCamera} onOpenChange={setShowCreateCamera}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-w-md" data-testid="create-camera-modal">
          <DialogHeader>
            <DialogTitle className="text-white">Nouvelle Camera</DialogTitle>
            <DialogDescription>Enregistrez une camera de chasse</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label className="text-zinc-300 text-sm">Nom *</Label>
              <Input className="bg-zinc-800 border-zinc-700" value={newCamera.name} onChange={e => setNewCamera(p => ({ ...p, name: e.target.value }))} placeholder="Camera Nord-Est" data-testid="camera-name-input" />
            </div>
            <div>
              <Label className="text-zinc-300 text-sm">Fabricant</Label>
              <Select value={newCamera.manufacturer} onValueChange={v => setNewCamera(p => ({ ...p, manufacturer: v }))}>
                <SelectTrigger className="bg-zinc-800 border-zinc-700" data-testid="camera-manufacturer-select"><SelectValue /></SelectTrigger>
                <SelectContent>{MANUFACTURERS.map(m => <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label className="text-zinc-300 text-sm">Modele</Label>
                <Input className="bg-zinc-800 border-zinc-700" value={newCamera.model} onChange={e => setNewCamera(p => ({ ...p, model: e.target.value }))} placeholder="FLEX-DARK" />
              </div>
              <div>
                <Label className="text-zinc-300 text-sm">No serie</Label>
                <Input className="bg-zinc-800 border-zinc-700" value={newCamera.serial} onChange={e => setNewCamera(p => ({ ...p, serial: e.target.value }))} placeholder="SP-12345" />
              </div>
            </div>
            <div>
              <Label className="text-zinc-300 text-sm">Waypoint ID *</Label>
              <Input className="bg-zinc-800 border-zinc-700" value={newCamera.waypoint_id} onChange={e => setNewCamera(p => ({ ...p, waypoint_id: e.target.value }))} placeholder="ID du waypoint associe" data-testid="camera-waypoint-input" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label className="text-zinc-300 text-sm">Latitude</Label>
                <Input className="bg-zinc-800 border-zinc-700" value={newCamera.gps_lat} onChange={e => setNewCamera(p => ({ ...p, gps_lat: e.target.value }))} placeholder="47.1234" />
              </div>
              <div>
                <Label className="text-zinc-300 text-sm">Longitude</Label>
                <Input className="bg-zinc-800 border-zinc-700" value={newCamera.gps_lon} onChange={e => setNewCamera(p => ({ ...p, gps_lon: e.target.value }))} placeholder="-71.5678" />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-zinc-700" onClick={() => setShowCreateCamera(false)}>Annuler</Button>
            <Button className="bg-amber-600 hover:bg-amber-700" onClick={handleCreateCamera} data-testid="camera-create-submit">Creer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* UPLOAD MODAL */}
      <Dialog open={showUpload} onOpenChange={setShowUpload}>
        <DialogContent className="bg-zinc-900 border-zinc-800 max-w-md" data-testid="upload-photos-modal">
          <DialogHeader>
            <DialogTitle className="text-white">Importer des Photos</DialogTitle>
            <DialogDescription>Selectionnez les photos a importer (max 20)</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label className="text-zinc-300 text-sm">Camera</Label>
              <Select value={uploadCameraId} onValueChange={setUploadCameraId}>
                <SelectTrigger className="bg-zinc-800 border-zinc-700" data-testid="upload-camera-select"><SelectValue placeholder="Selectionnez une camera" /></SelectTrigger>
                <SelectContent>
                  {cameras.filter(c => c.status === 'active').map(c => (
                    <SelectItem key={c.id} value={c.id}>{c.name || c.id.slice(0, 8)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-zinc-300 text-sm">Photos</Label>
              <div className="border-2 border-dashed border-zinc-700 rounded-lg p-6 text-center hover:border-amber-500/50 transition-colors cursor-pointer"
                onClick={() => document.getElementById('photo-upload-input')?.click()} data-testid="upload-drop-zone">
                <Upload className="h-8 w-8 text-zinc-500 mx-auto mb-2" />
                <p className="text-sm text-zinc-400">Cliquez pour selectionner des photos</p>
                <p className="text-xs text-zinc-600 mt-1">JPEG, TIFF, HEIC — Max 50 MB chacune</p>
              </div>
              <input id="photo-upload-input" type="file" accept="image/*" multiple className="hidden"
                onChange={e => setUploadFiles(Array.from(e.target.files || []))} />
              {uploadFiles.length > 0 && (
                <div className="mt-2 space-y-1" data-testid="upload-file-list">
                  {uploadFiles.map((f, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-zinc-400">
                      <CheckCircle className="h-3 w-3 text-green-500" />
                      <span className="truncate">{f.name}</span>
                      <span className="text-zinc-600">({(f.size / 1024).toFixed(0)} KB)</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {uploading && (
              <div>
                <Progress value={uploadProgress} className="h-2" />
                <p className="text-xs text-zinc-500 mt-1 text-center">{uploadProgress}%</p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" className="border-zinc-700" onClick={() => setShowUpload(false)} disabled={uploading}>Annuler</Button>
            <Button className="bg-amber-600 hover:bg-amber-700" onClick={handleUploadPhotos} disabled={uploading || !uploadCameraId || uploadFiles.length === 0} data-testid="upload-submit-btn">
              {uploading ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Upload className="h-4 w-4 mr-1" />}
              {uploading ? 'Import en cours...' : `Importer ${uploadFiles.length} photo(s)`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CameraModule;
