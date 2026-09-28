from proxy_manager import ProxyManager
import os
from typing import List, Optional


class ProxyAdapter:
    """
    Adapter that replaces hardcoded proxy file reading with dynamic API-based proxy retrieval.
    Maintains backward compatibility with existing code that expects a proxy list.
    """

    def __init__(self, render_api_url: str = None, render_api_key: str = None):
        self.proxy_manager = ProxyManager(
            render_api_url=render_api_url,
            render_api_key=render_api_key,
        )
        self._cached_proxies: Optional[List[str]] = None

    def load_proxies_from_api(self, target_url: str, view_count: int = 1000) -> List[str]:
        """
        Load proxies from Render API instead of file.
        
        Args:
            target_url: The target URL for the campaign
            view_count: Number of views requested
        
        Returns:
            List of proxy URLs
        """
        print(f"[ProxyAdapter] Loading proxies from API for {target_url}...")
        self._cached_proxies = self.proxy_manager.get_proxies_sync(
            target_url, view_count
        )
        return self._cached_proxies

    def get_cached_proxies(self) -> List[str]:
        """Return cached proxies."""
        return self._cached_proxies or []

    @staticmethod
    def load_proxies_from_file(filepath: str) -> List[str]:
        """
        Legacy method: Load proxies from file (kept for backward compatibility).
        """
        if not os.path.exists(filepath):
            print(f"[ProxyAdapter] File not found: {filepath}")
            return []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                proxies = [line.strip() for line in f if line.strip()]
            print(f"[ProxyAdapter] Loaded {len(proxies)} proxies from file")
            return proxies
        except Exception as e:
            print(f"[ProxyAdapter] Error reading proxy file: {e}")
            return []

    def get_proxy_count(self) -> int:
        """Return number of currently loaded proxies."""
        return len(self._cached_proxies or [])

    def __repr__(self):
        return f"ProxyAdapter(cached={self.get_proxy_count()} proxies)"
