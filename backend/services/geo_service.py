"""
Geolocation service for IP address tracking
Uses ip-api.com (free, no API key needed for non-commercial use)
Alternative: ipapi.co, ipinfo.io (require API keys for high volume)
"""

import httpx
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class GeoLocationService:
    def __init__(self):
        self.enabled = True
        self.api_url = "http://ip-api.com/json/"
        self.timeout = 2.0  # Quick timeout to avoid slowing down requests
        
    async def get_location_data(self, ip_address: str) -> Optional[Dict]:
        """
        Get geolocation data for an IP address
        
        Returns dict with: country, city, region, lat, lon, timezone, isp, etc.
        Returns None if lookup fails
        """
        # Skip private/local IPs
        if self._is_private_ip(ip_address):
            logger.debug(f"Skipping geolocation for private IP: {ip_address}")
            return {
                "country": "Local",
                "city": "Local",
                "region": "Local",
                "lat": None,
                "lon": None,
                "timezone": None,
                "isp": "Local Network"
            }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}{ip_address}",
                    params={
                        "fields": "status,message,country,countryCode,region,regionName,city,lat,lon,timezone,isp,org,as"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "success":
                        return {
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "region": data.get("regionName"),
                            "region_code": data.get("region"),
                            "city": data.get("city"),
                            "lat": str(data.get("lat")) if data.get("lat") else None,
                            "lon": str(data.get("lon")) if data.get("lon") else None,
                            "timezone": data.get("timezone"),
                            "isp": data.get("isp"),
                            "org": data.get("org"),
                            "as": data.get("as")
                        }
                    else:
                        logger.warning(f"Geolocation lookup failed: {data.get('message')}")
                        
        except Exception as e:
            logger.error(f"Error getting geolocation for {ip_address}: {e}")
        
        return None
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/local"""
        if not ip or ip == "unknown":
            return True
        
        # Common private IP ranges and special addresses
        private_prefixes = [
            "127.",      # Loopback
            "10.",       # Private Class A
            "172.16.",   # Private Class B
            "172.17.",
            "172.18.",
            "172.19.",
            "172.20.",
            "172.21.",
            "172.22.",
            "172.23.",
            "172.24.",
            "172.25.",
            "172.26.",
            "172.27.",
            "172.28.",
            "172.29.",
            "172.30.",
            "172.31.",
            "192.168.",  # Private Class C
            "169.254.",  # Link-local
            "::1",       # IPv6 loopback
            "fc00:",     # IPv6 private
            "fd00:",     # IPv6 private
            "fe80:",     # IPv6 link-local
        ]
        
        return any(ip.startswith(prefix) for prefix in private_prefixes)

# Singleton instance
geo_service = GeoLocationService()
