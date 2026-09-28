import os
import httpx
from typing import List, Optional
from datetime import datetime


class ProxyManager:
    """
    Manages proxy fetching from Render-hosted proxy scraper API.
    Replaces hardcoded proxy lists with dynamic API-based retrieval.
    """

    def __init__(
        self,
        render_api_url: str = None,
        render_api_key: str = None,
        timeout: int = 10,
    ):
        # Default Render service URL (set this to your deployed Render service)
        self.render_api_url = (
            render_api_url or os.getenv("RENDER_PROXY_API_URL", "https://contentvippro.onrender.com")
        )
        self.render_api_key = render_api_key or os.getenv("RENDER_API_KEY", "rnd_CI6aJUlOryoe7U1yrkUMmMg9dyZa")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self._cache = {"proxies": [], "last_fetch": None}

    async def fetch_proxies(
        self, target_url: str, view_count: int = 1000, force_refresh: bool = False
    ) -> List[str]:
        """
        Fetch proxies from Render API.
        
        Args:
            target_url: The target URL to process (e.g., TikTok video link)
            view_count: Number of views to target
            force_refresh: Force fresh fetch (bypass cache)
        
        Returns:
            List of proxy URLs
        """
        try:
            # Use cache if available and not forced refresh
            if (
                not force_refresh
                and self._cache["proxies"]
                and self._cache["last_fetch"]
            ):
                return self._cache["proxies"]

            # Build request to Render API
            api_endpoint = f"{self.render_api_url}/api"
            params = {
                "url": target_url,
                "views": view_count,
                "key": self.render_api_key,  # Include API key for auth
            }

            print(
                f"[ProxyManager] Fetching proxies from: {api_endpoint}?url={target_url}&views={view_count}"
            )

            response = await self.client.get(api_endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            print(f"[ProxyManager] API Response: {data}")

            # Extract proxy list from response
            proxies = data.get("proxies", [])
            if not proxies:
                print(
                    "[ProxyManager] WARNING: No proxies returned. Using fallback list."
                )
                return self._get_fallback_proxies()

            # Cache the result
            self._cache["proxies"] = proxies
            self._cache["last_fetch"] = datetime.utcnow()

            print(f"[ProxyManager] Fetched {len(proxies)} proxies successfully")
            return proxies

        except httpx.RequestError as e:
            print(
                f"[ProxyManager] Error fetching from Render API: {e}. Using fallback."
            )
            return self._get_fallback_proxies()
        except Exception as e:
            print(f"[ProxyManager] Unexpected error: {e}. Using fallback.")
            return self._get_fallback_proxies()

    def get_proxies_sync(
        self, target_url: str, view_count: int = 1000
    ) -> List[str]:
        """
        Synchronous wrapper for proxy fetching (for use in non-async contexts).
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.fetch_proxies(target_url, view_count)
        )

    def _get_fallback_proxies(self) -> List[str]:
        """
        Fallback proxy list in case API is unavailable.
        These should be public/free proxies or your own proxy pool.
        """
        return [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "http://proxy3.example.com:8080",
        ]

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def __repr__(self):
        return f"ProxyManager(url={self.render_api_url})"
