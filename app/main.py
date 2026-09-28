from datetime import datetime, timezone
from uuid import uuid4
import json
from typing import Optional

from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import AnyHttpUrl, BaseModel

app = FastAPI(title="ContentVIP Pro API", version="1.0.0")


class CampaignRequest(BaseModel):
    """Request model for campaign creation."""
    url: str
    views: int
    name: Optional[str] = None
    metadata: Optional[dict] = None


class ProxyRequest(BaseModel):
    """Request model for proxy fetching."""
    url: str
    count: int = 10


class CampaignResponse(BaseModel):
    """Response model for campaign operations."""
    status: str
    job_id: str
    url: str
    views: int
    created_at: str
    message: str


class ProxyResponse(BaseModel):
    """Response model for proxy operations."""
    status: str
    proxies: list
    count: int
    generated_at: str


# In-memory storage (in production, use database)
campaigns_db = {}
proxies_db = {}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "contentvippro",
        "version": "1.0.0",
        "health": "/health",
        "docs": "/docs",
        "endpoints": {
            "GET /api": "Create campaign via query params",
            "POST /api": "Create campaign via JSON body",
            "GET /api/campaign/{job_id}": "Get campaign status",
            "GET /api/proxies": "Get proxies via query params",
            "POST /api/proxies": "Get proxies via JSON body",
            "GET /api/list/campaigns": "List all campaigns",
            "GET /api/list/proxies": "List all proxies",
        }
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "contentvippro"}


# ==================== CAMPAIGN ENDPOINTS ====================

@app.get("/api")
def create_campaign_get(
    url: str = Query(..., description="Target URL"),
    views: int = Query(0, ge=0, le=500_000, description="Target view count"),
    name: Optional[str] = Query(None, description="Campaign name"),
):
    """
    Create campaign via GET request.
    
    Example:
        /api?url=https://tiktok.com/video/123&views=2500&name=Mycampaign
    """
    return _create_campaign(url, views, name)


@app.post("/api")
def create_campaign_post(request: CampaignRequest):
    """
    Create campaign via POST request.
    
    Example:
        POST /api
        {
            "url": "https://tiktok.com/video/123",
            "views": 2500,
            "name": "Mycampaign",
            "metadata": {"source": "windows_app"}
        }
    """
    return _create_campaign(request.url, request.views, request.name, request.metadata)


def _create_campaign(url: str, views: int, name: str = None, metadata: dict = None) -> dict:
    """Internal function to create campaign."""
    job_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    
    campaign_data = {
        "status": "queued",
        "job_id": job_id,
        "url": url,
        "views": views,
        "name": name or f"campaign_{job_id[:8]}",
        "created_at": timestamp,
        "metadata": metadata or {},
        "message": "Campaign request accepted for internal processing."
    }
    
    campaigns_db[job_id] = campaign_data
    return campaign_data


@app.get("/api/campaign/{job_id}")
def get_campaign_status(job_id: str):
    """
    Get campaign status.
    
    Example:
        /api/campaign/550e8400-e29b-41d4-a716-446655440000
    """
    if job_id not in campaigns_db:
        raise HTTPException(status_code=404, detail=f"Campaign {job_id} not found")
    
    campaign = campaigns_db[job_id]
    # Simulate progress
    campaign["status"] = "processing" if campaign["status"] == "queued" else "completed"
    return campaign


@app.get("/api/list/campaigns")
def list_campaigns(limit: int = Query(10, ge=1, le=100)):
    """
    List all campaigns.
    
    Example:
        /api/list/campaigns?limit=20
    """
    campaigns = list(campaigns_db.values())[-limit:]
    return {
        "count": len(campaigns),
        "total": len(campaigns_db),
        "campaigns": campaigns
    }


# ==================== PROXY ENDPOINTS ====================

@app.get("/api/proxies")
def get_proxies_get(
    url: str = Query(..., description="Target URL"),
    count: int = Query(10, ge=1, le=100, description="Number of proxies to return"),
):
    """
    Get proxies via GET request.
    
    Example:
        /api/proxies?url=https://tiktok.com/video/123&count=20
    """
    return _get_proxies(url, count)


@app.post("/api/proxies")
def get_proxies_post(request: ProxyRequest):
    """
    Get proxies via POST request.
    
    Example:
        POST /api/proxies
        {
            "url": "https://tiktok.com/video/123",
            "count": 20
        }
    """
    return _get_proxies(request.url, request.count)


def _get_proxies(url: str, count: int) -> dict:
    """Internal function to generate proxies."""
    # Generate dummy proxies (in production, scrape from real sources)
    proxies = [
        f"http://proxy-{i}.example.com:8080" for i in range(1, count + 1)
    ]
    
    proxy_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    
    proxy_data = {
        "status": "success",
        "proxy_id": proxy_id,
        "url": url,
        "proxies": proxies,
        "count": len(proxies),
        "generated_at": timestamp,
        "message": f"Generated {len(proxies)} proxies for internal processing."
    }
    
    proxies_db[proxy_id] = proxy_data
    return proxy_data


@app.get("/api/list/proxies")
def list_proxies(limit: int = Query(10, ge=1, le=100)):
    """
    List all proxy batches.
    
    Example:
        /api/list/proxies?limit=20
    """
    proxies = list(proxies_db.values())[-limit:]
    return {
        "count": len(proxies),
        "total": len(proxies_db),
        "batches": proxies
    }


# ==================== COMBINED ENDPOINT ====================

@app.get("/api/process")
def process_campaign_get(
    url: str = Query(..., description="Target URL"),
    views: int = Query(0, ge=0, le=500_000, description="Target view count"),
    proxy_count: int = Query(10, ge=1, le=100, description="Number of proxies needed"),
    name: Optional[str] = Query(None, description="Campaign name"),
):
    """
    Create campaign AND fetch proxies in one request.
    
    Example:
        /api/process?url=https://tiktok.com/video/123&views=2500&proxy_count=20&name=MyJob
    """
    campaign = _create_campaign(url, views, name)
    proxies = _get_proxies(url, proxy_count)
    
    return {
        "campaign": campaign,
        "proxies": proxies,
        "combined_at": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/process")
def process_campaign_post(
    url: str = Body(...),
    views: int = Body(...),
    proxy_count: int = Body(10),
    name: Optional[str] = Body(None),
):
    """
    Create campaign AND fetch proxies via POST.
    
    Example:
        POST /api/process
        {
            "url": "https://tiktok.com/video/123",
            "views": 2500,
            "proxy_count": 20,
            "name": "MyJob"
        }
    """
    campaign = _create_campaign(url, views, name)
    proxies = _get_proxies(url, proxy_count)
    
    return {
        "campaign": campaign,
        "proxies": proxies,
        "combined_at": datetime.now(timezone.utc).isoformat()
    }


# ==================== BULK OPERATIONS ====================

@app.post("/api/bulk/campaigns")
def bulk_create_campaigns(
    campaigns: list = Body(..., description="List of campaign configs")
):
    """
    Create multiple campaigns at once.
    
    Example:
        POST /api/bulk/campaigns
        [
            {"url": "https://tiktok.com/video/1", "views": 1000},
            {"url": "https://tiktok.com/video/2", "views": 2500},
            {"url": "https://tiktok.com/video/3", "views": 5000}
        ]
    """
    results = []
    for config in campaigns:
        campaign = _create_campaign(
            url=config.get("url"),
            views=config.get("views", 0),
            name=config.get("name"),
            metadata=config.get("metadata")
        )
        results.append(campaign)
    
    return {
        "status": "success",
        "count": len(results),
        "campaigns": results,
        "created_at": datetime.now(timezone.utc).isoformat()
    }


# ==================== STATISTICS ====================

@app.get("/api/stats")
def get_statistics():
    """
    Get API statistics.
    
    Example:
        /api/stats
    """
    return {
        "total_campaigns": len(campaigns_db),
        "total_proxy_batches": len(proxies_db),
        "campaigns_queued": sum(1 for c in campaigns_db.values() if c["status"] == "queued"),
        "campaigns_processing": sum(1 for c in campaigns_db.values() if c["status"] == "processing"),
        "campaigns_completed": sum(1 for c in campaigns_db.values() if c["status"] == "completed"),
        "total_views_targeted": sum(c["views"] for c in campaigns_db.values()),
        "total_proxies_generated": sum(p["count"] for p in proxies_db.values()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
