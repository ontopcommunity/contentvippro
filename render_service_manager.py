import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx


class RenderServiceManager:
    """
    Manages communication with the Render-hosted ContentVIP Pro service.
    Handles campaign creation, status tracking, and result retrieval.
    """

    def __init__(
        self,
        service_url: str = None,
        api_key: str = None,
        timeout: int = 30,
    ):
        self.service_url = (
            service_url or os.getenv("RENDER_SERVICE_URL", "https://contentvippro.onrender.com")
        )
        self.api_key = api_key or os.getenv("RENDER_API_KEY", "rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa")
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)
        self._campaigns: Dict[str, Dict[str, Any]] = {}

    def health_check(self) -> bool:
        """
        Check if Render service is running.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = self.client.get(f"{self.service_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"[RenderServiceManager] Health check failed: {e}")
            return False

    def create_campaign(
        self,
        target_url: str,
        view_count: int,
        campaign_name: str = None,
        metadata: Dict[str, Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new campaign on Render service.
        
        Args:
            target_url: Target URL (e.g., TikTok video link)
            view_count: Number of views to target
            campaign_name: Optional campaign name
            metadata: Optional additional metadata
        
        Returns:
            Campaign response dict or None on failure
        """
        try:
            payload = {
                "url": target_url,
                "views": view_count,
                "api_key": self.api_key,
                "name": campaign_name or f"campaign_{datetime.utcnow().timestamp()}",
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            print(f"[RenderServiceManager] Creating campaign: {target_url}")
            response = self.client.post(
                f"{self.service_url}/api",
                json=payload,
            )
            response.raise_for_status()

            campaign_data = response.json()
            campaign_id = campaign_data.get("job_id")

            # Store campaign locally
            if campaign_id:
                self._campaigns[campaign_id] = campaign_data
                print(
                    f"[RenderServiceManager] Campaign created: {campaign_id}"
                )

            return campaign_data

        except Exception as e:
            print(
                f"[RenderServiceManager] Error creating campaign: {e}"
            )
            return None

    def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve campaign status from Render service.
        
        Args:
            campaign_id: Campaign job ID
        
        Returns:
            Campaign status dict or None
        """
        try:
            response = self.client.get(
                f"{self.service_url}/api/status/{campaign_id}",
                params={"key": self.api_key},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[RenderServiceManager] Error fetching status: {e}")
            return None

    def list_campaigns(self, limit: int = 10) -> list:
        """
        List recent campaigns from local cache.
        
        Args:
            limit: Maximum number of campaigns to return
        
        Returns:
            List of campaign dicts
        """
        return list(self._campaigns.values())[-limit:]

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"RenderServiceManager(url={self.service_url}, campaigns={len(self._campaigns)})"
