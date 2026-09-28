#!/usr/bin/env python3
"""
Integration module for connecting ContentVIP Pro client (Windows app)
with the Render-hosted proxy API service.

Usage:
    from integration import ContentVIPProIntegration
    
    integrator = ContentVIPProIntegration(
        render_url="https://contentvippro.onrender.com",
        render_key="rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa"
    )
    
    proxies = integrator.fetch_proxies(
        target_url="https://www.tiktok.com/@user/video/123456",
        view_count=2500
    )
    
    campaign = integrator.create_campaign(
        target_url="https://www.tiktok.com/@user/video/123456",
        view_count=2500
    )
"""

import os
from typing import List, Dict, Optional, Any
from proxy_adapter import ProxyAdapter
from render_service_manager import RenderServiceManager


class ContentVIPProIntegration:
    """
    Main integration point for ContentVIP Pro Windows client.
    Coordinates proxy fetching and campaign management via Render service.
    """

    def __init__(
        self,
        render_url: str = None,
        render_key: str = None,
    ):
        self.render_url = (
            render_url or os.getenv("RENDER_URL", "https://contentvippro.onrender.com")
        )
        self.render_key = (
            render_key or os.getenv("RENDER_API_KEY", "rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa")
        )
        
        self.proxy_adapter = ProxyAdapter(
            render_api_url=self.render_url,
            render_api_key=self.render_key,
        )
        self.service_manager = RenderServiceManager(
            service_url=self.render_url,
            api_key=self.render_key,
        )
        
        print(
            f"[ContentVIPProIntegration] Initialized with Render URL: {self.render_url}"
        )

    def fetch_proxies(
        self, target_url: str, view_count: int = 1000
    ) -> List[str]:
        """
        Fetch proxies from Render API.
        
        Args:
            target_url: Target URL for the campaign
            view_count: Number of views requested
        
        Returns:
            List of proxy URLs
        """
        print(f"[Integration] Fetching proxies for {target_url}")
        return self.proxy_adapter.load_proxies_from_api(target_url, view_count)

    def create_campaign(
        self,
        target_url: str,
        view_count: int,
        campaign_name: str = None,
        metadata: Dict[str, Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a campaign on Render service.
        
        Args:
            target_url: Target URL
            view_count: View target
            campaign_name: Optional campaign name
            metadata: Optional additional data
        
        Returns:
            Campaign response or None
        """
        print(f"[Integration] Creating campaign: {target_url}")
        return self.service_manager.create_campaign(
            target_url, view_count, campaign_name, metadata
        )

    def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get campaign status from Render service.
        
        Args:
            campaign_id: Campaign job ID
        
        Returns:
            Campaign status dict or None
        """
        print(f"[Integration] Fetching status for campaign: {campaign_id}")
        return self.service_manager.get_campaign_status(campaign_id)

    def health_check(self) -> bool:
        """
        Check if Render service is online.
        
        Returns:
            True if online, False otherwise
        """
        print("[Integration] Running health check...")
        is_healthy = self.service_manager.health_check()
        status = "✓ Online" if is_healthy else "✗ Offline"
        print(f"[Integration] Render service: {status}")
        return is_healthy

    def close(self):
        """Cleanup resources."""
        self.proxy_adapter.proxy_manager.client.aclose()
        self.service_manager.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return (
            f"ContentVIPProIntegration("
            f"render_url={self.render_url}, "
            f"proxies={self.proxy_adapter.get_proxy_count()}"
            f")"
        )


if __name__ == "__main__":
    # Example usage
    print("\n=== ContentVIP Pro Integration Test ===")
    
    with ContentVIPProIntegration() as integrator:
        # Test health check
        if integrator.health_check():
            print("\n✓ Service is online!")
            
            # Test campaign creation
            campaign = integrator.create_campaign(
                target_url="https://www.tiktok.com/@example/video/123456",
                view_count=2500,
                campaign_name="Test Campaign",
            )
            
            if campaign:
                print(f"✓ Campaign created: {campaign.get('job_id')}")
                print(f"  Response: {campaign}")
            
            # Test proxy fetching
            proxies = integrator.fetch_proxies(
                target_url="https://www.tiktok.com/@example/video/123456",
                view_count=2500,
            )
            print(f"✓ Fetched {len(proxies)} proxies")
        else:
            print("✗ Service is offline. Please deploy to Render first.")
    
    print("\n=== Test Complete ===")
