# ContentVIP Pro - Integration Guide

## Overview

This project integrates a **Windows-based TikTok content visibility client** with a **Render-hosted proxy API service**. Instead of relying on static proxy files, the client dynamically fetches proxies from an API endpoint.

## Architecture

```
┌─────────────────────────────────────┐
│  Windows Client (main.py)           │
│  - Flet GUI                         │
│  - File selectors                   │
│  - Thread management                │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Integration Layer (integration.py) │
│  - ContentVIPProIntegration class   │
│  - Coordinates proxy & campaign mgmt│
└────────────┬────────────────────────┘
             │
        ┌────┴─────┐
        ↓          ↓
   ┌────────┐  ┌──────────────┐
   │ Proxy  │  │ Service      │
   │Adapter │  │ Manager      │
   └────┬───┘  └──────┬───────┘
        │             │
        └─────┬───────┘
              ↓
   ┌─────────────────────────────────┐
   │  Render Service (Deployed)      │
   │  GET /api?url=X&views=Y         │
   │  Returns: {proxies: [...]}      │
   └─────────────────────────────────┘
```

## Key Components

### 1. `proxy_manager.py`
- Manages async proxy fetching from Render API
- Caches proxies to reduce API calls
- Fallback to hardcoded list if API fails

### 2. `proxy_adapter.py`
- Adapter pattern for backward compatibility
- Supports both file-based and API-based proxy loading
- Simple interface: `load_proxies_from_api(url, view_count)`

### 3. `render_service_manager.py`
- Communicates with Render-hosted service
- Creates campaigns via POST requests
- Checks service health via `/health` endpoint
- Retrieves campaign status

### 4. `integration.py`
- Main integration class for Windows client
- Coordinates proxy and campaign management
- Simple interface for client code

### 5. `app/main.py` (FastAPI)
- Render service endpoint
- `GET /api?url=<target_url>&views=<count>`
- Returns JSON with job_id, status, timestamp

## Setup & Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run examples
python examples.py
```

### Render Deployment

1. **Create Render Account**: https://render.com

2. **Connect GitHub Repository**:
   - Go to Dashboard → New → Web Service
   - Connect `ontopcommunity/contentvippro` repo
   - Select `main` branch

3. **Configure Service**:
   - Name: `contentvippro`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free tier is fine

4. **Set Environment Variables**:
   - Go to Environment tab
   - Add: `RENDER_API_KEY=rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa`
   - Add: `RENDER_PROXY_API_URL=https://contentvippro.onrender.com` (your deployed URL)

5. **Deploy**:
   - Save → Service will build and deploy automatically
   - Note the service URL (e.g., `https://contentvippro.onrender.com`)

## Usage in Windows Client

### Replace Proxy File Selection with API Integration

**Before (main.py line ~444):**
```python
def select_proxy(self, e):
    file_path = self.open_file_dialog("Выберите файл с прокси")
    if file_path:
        Settings.get_instance().proxies_file = file_path
        Settings.get_instance().save()
```

**After:**
```python
from integration import ContentVIPProIntegration

def select_proxy(self, e):
    # Instead of selecting file, fetch from API
    integrator = ContentVIPProIntegration(
        render_url=Settings.get_instance().render_url,
        render_key=Settings.get_instance().render_key
    )
    
    target_url = self.post_link_input.value  # Or get from UI
    proxies = integrator.fetch_proxies(target_url, view_count=2500)
    
    # Save to cache or use directly
    Settings.get_instance().cached_proxies = proxies
    Settings.get_instance().save()
    
    integrator.close()
```

### Create Campaign on "Start Upload"

**Modify start_upload method:**
```python
def start_upload(self, e):
    # ... existing validation ...
    
    # Create campaign via Render API
    integrator = ContentVIPProIntegration()
    campaign = integrator.create_campaign(
        target_url=self.post_link_input.value,
        view_count=int(self.views_input.value),
        campaign_name=f"Campaign_{datetime.now().timestamp()}"
    )
    
    if campaign:
        print(f"Campaign created: {campaign['job_id']}")
        # Continue with upload using fetched proxies
    else:
        print("Failed to create campaign")
    
    # Start threads as before...
```

## API Endpoints

### Health Check
```bash
GET https://contentvippro.onrender.com/health

Response:
{"status": "ok"}
```

### Create Campaign / Fetch Proxies
```bash
GET https://contentvippro.onrender.com/api?url=https://tiktok.com/...&views=2500

Response:
{
  "status": "queued",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://www.tiktok.com/@example/video/123456",
  "views": 2500,
  "created_at": "2026-09-28T12:30:00Z",
  "message": "Campaign request accepted..."
}
```

## Configuration

### Environment Variables

Set these on Render:

```
RENDER_API_KEY=rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa
RENDER_PROXY_API_URL=https://contentvippro.onrender.com
RENDER_SERVICE_URL=https://contentvippro.onrender.com
```

Or pass to integration:

```python
integrator = ContentVIPProIntegration(
    render_url="https://contentvippro.onrender.com",
    render_key="rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa"
)
```

## Examples

Run the examples:

```bash
python examples.py
```

Includes:
1. Basic campaign creation
2. Proxy fetching + campaign
3. Batch campaign processing
4. Campaign status monitoring

## Security Notes

⚠️ **Important:**
- Never commit API keys to Git (use `.env` or environment variables)
- Rotate `rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa` regularly
- Validate all user inputs in the FastAPI service
- Use HTTPS only for production
- Implement rate limiting on Render endpoints

## Troubleshooting

### Service Returns 502 Bad Gateway
- Check logs: Render Dashboard → Services → contentvippro → Logs
- Ensure `requirements.txt` includes all dependencies
- Verify `render.yaml` or manual configuration

### Proxy Fetching Returns Empty List
- Check Render service health: `GET /health`
- Verify API key is correct
- Check network connectivity from client to Render

### "Module not found" errors
- Ensure `requirements.txt` is up to date
- Reinstall: `pip install --force-reinstall -r requirements.txt`

## Next Steps

1. Deploy `render.yaml` to Render
2. Test endpoints: `curl "https://contentvippro.onrender.com/health"`
3. Integrate `ContentVIPProIntegration` into Windows client
4. Remove static proxy file selection
5. Add Render URL/key to Settings class
6. Test end-to-end campaign creation and proxy fetching

## License

MIT
