# Test Credentials — BIONIC OS V20-SUPRA

## Admin institutionnel (captures Playwright)
- Email : `steeve-max-capture@huntiq.com`
- Password : `CaptureOps2026#`
- Role : `admin`
- Usage : Phase XI-SUPRA-C / D Playwright captures, Health Panel access, LEP ingestion admin

## Endpoints de capture
- Frontend capture mode : `{BASE}/territoire-capture-mode?lat=..&lon=..&species=..&zoom=..`
- Backend LEP ingest : POST `{API}/api/v20/territoire/lep/ingest`
- WebSocket alerts : `ws(s)://{BASE}/ws/self-audit-alert`
