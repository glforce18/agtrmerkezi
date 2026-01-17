"""
IP Geolocation Service
Free IP geolocation using ip-api.com with caching
"""

import logging
from typing import Optional, Dict, Any
from datetime import timedelta

import httpx
from fastapi import Request

from app.core.redis_manager import redis_manager

logger = logging.getLogger(__name__)


class GeolocationService:
    """IP geolocation service with Redis caching"""

    # Using ip-api.com free tier (45 req/min limit)
    API_URL = "http://ip-api.com/json/{ip}"
    BATCH_API_URL = "http://ip-api.com/batch"

    # Cache TTL - 7 days (IP locations don't change often)
    CACHE_TTL = 7 * 24 * 60 * 60

    @staticmethod
    def _get_cache_key(ip: str) -> str:
        """Get Redis cache key for IP"""
        return f"geo:{ip}"

    @staticmethod
    async def get_location(ip: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get geolocation data for IP address

        Returns:
            {
                "ip": "8.8.8.8",
                "country": "United States",
                "countryCode": "US",
                "region": "CA",
                "regionName": "California",
                "city": "Mountain View",
                "zip": "94035",
                "lat": 37.386,
                "lon": -122.084,
                "timezone": "America/Los_Angeles",
                "isp": "Google LLC",
                "org": "Google Public DNS",
                "as": "AS15169 Google LLC"
            }
        """
        # Skip private IPs
        if ip.startswith(("127.", "10.", "172.16.", "192.168.", "localhost")):
            return {
                "ip": ip,
                "country": "Private",
                "countryCode": "XX",
                "city": "Local",
                "isPrivate": True
            }

        # Check cache first
        if use_cache:
            cache_key = GeolocationService._get_cache_key(ip)
            cached = await redis_manager.get(cache_key)

            if cached:
                logger.debug(f"Geolocation cache hit for {ip}")
                return eval(cached)  # Convert string back to dict

        # Fetch from API
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    GeolocationService.API_URL.format(ip=ip)
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check if successful
                    if data.get("status") == "success":
                        # Cache the result
                        if use_cache:
                            cache_key = GeolocationService._get_cache_key(ip)
                            await redis_manager.set(
                                cache_key,
                                str(data),
                                ttl=GeolocationService.CACHE_TTL
                            )

                        logger.info(f"Geolocation fetched for {ip}: {data.get('city')}, {data.get('country')}")
                        return data

                    else:
                        logger.warning(f"Geolocation API error for {ip}: {data.get('message')}")
                        return None

                else:
                    logger.error(f"Geolocation API HTTP error: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.warning(f"Geolocation API timeout for {ip}")
            return None
        except Exception as e:
            logger.error(f"Geolocation API error: {e}")
            return None

    @staticmethod
    async def get_locations_batch(ips: list[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get geolocation for multiple IPs (max 100)

        Returns:
            {
                "8.8.8.8": {...geo_data...},
                "1.1.1.1": {...geo_data...}
            }
        """
        if not ips or len(ips) > 100:
            logger.error("Batch geolocation requires 1-100 IPs")
            return {}

        results = {}

        # Check cache for all IPs first
        uncached_ips = []
        for ip in ips:
            cache_key = GeolocationService._get_cache_key(ip)
            cached = await redis_manager.get(cache_key)

            if cached:
                results[ip] = eval(cached)
            else:
                uncached_ips.append(ip)

        # Fetch uncached IPs
        if uncached_ips:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        GeolocationService.BATCH_API_URL,
                        json=uncached_ips
                    )

                    if response.status_code == 200:
                        batch_data = response.json()

                        for data in batch_data:
                            if data.get("status") == "success":
                                ip = data.get("query")
                                results[ip] = data

                                # Cache result
                                cache_key = GeolocationService._get_cache_key(ip)
                                await redis_manager.set(
                                    cache_key,
                                    str(data),
                                    ttl=GeolocationService.CACHE_TTL
                                )

            except Exception as e:
                logger.error(f"Batch geolocation error: {e}")

        return results

    @staticmethod
    async def is_vpn_or_proxy(ip: str) -> bool:
        """
        Detect if IP is from VPN/Proxy/Tor
        Note: This is a basic check. For production, use specialized services like:
        - IPQualityScore
        - IPHub
        - ProxyCheck.io
        """
        geo = await GeolocationService.get_location(ip)

        if not geo:
            return False

        # Check for common VPN/proxy indicators
        org = geo.get("org", "").lower()
        isp = geo.get("isp", "").lower()

        vpn_keywords = [
            "vpn", "proxy", "tor", "tunnel", "relay",
            "cloud", "hosting", "datacenter", "colocation"
        ]

        for keyword in vpn_keywords:
            if keyword in org or keyword in isp:
                logger.warning(f"Potential VPN/Proxy detected: {ip} ({org}, {isp})")
                return True

        return False

    @staticmethod
    async def calculate_distance(ip1: str, ip2: str) -> Optional[float]:
        """
        Calculate distance between two IPs in kilometers

        Returns distance in km or None if geolocation fails
        """
        from math import radians, sin, cos, sqrt, atan2

        geo1 = await GeolocationService.get_location(ip1)
        geo2 = await GeolocationService.get_location(ip2)

        if not geo1 or not geo2:
            return None

        # Haversine formula
        lat1, lon1 = radians(geo1.get("lat", 0)), radians(geo1.get("lon", 0))
        lat2, lon2 = radians(geo2.get("lat", 0)), radians(geo2.get("lon", 0))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Earth radius in km
        radius = 6371

        distance = radius * c

        logger.debug(f"Distance between {ip1} and {ip2}: {distance:.2f} km")

        return distance

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        Extract client IP from request

        Handles X-Forwarded-For, X-Real-IP headers
        """
        # Check X-Forwarded-For (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP in chain (original client)
            ip = forwarded_for.split(",")[0].strip()
            return ip

        # Check X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback to direct connection
        return request.client.host

    @staticmethod
    async def get_request_geolocation(request: Request) -> Optional[Dict[str, Any]]:
        """
        Get geolocation for incoming request

        Convenience method for endpoints
        """
        ip = GeolocationService.get_client_ip(request)
        return await GeolocationService.get_location(ip)


class SuspiciousLocationDetector:
    """Detect suspicious location patterns"""

    @staticmethod
    async def detect_impossible_travel(
        user_id: int,
        current_ip: str,
        last_ip: str,
        last_login_time: Any
    ) -> bool:
        """
        Detect impossible travel (e.g., Tokyo to New York in 10 minutes)

        Returns True if travel is physically impossible
        """
        from datetime import datetime

        # Calculate distance
        distance = await GeolocationService.calculate_distance(current_ip, last_ip)

        if distance is None:
            return False

        # Calculate time difference
        if isinstance(last_login_time, str):
            last_login_time = datetime.fromisoformat(last_login_time)

        time_diff = (datetime.utcnow() - last_login_time).total_seconds() / 3600  # hours

        # Maximum reasonable travel speed: 900 km/h (commercial airplane)
        max_speed = 900

        required_speed = distance / time_diff if time_diff > 0 else float('inf')

        if required_speed > max_speed:
            logger.critical(
                f"Impossible travel detected for user {user_id}: "
                f"{distance:.0f}km in {time_diff:.1f}h "
                f"({required_speed:.0f} km/h required)"
            )
            return True

        return False

    @staticmethod
    async def detect_country_mismatch(
        user_id: int,
        current_ip: str,
        expected_country_code: str
    ) -> bool:
        """
        Detect login from unexpected country

        Returns True if country doesn't match user's typical location
        """
        geo = await GeolocationService.get_location(current_ip)

        if not geo:
            return False

        current_country = geo.get("countryCode")

        if current_country != expected_country_code:
            logger.warning(
                f"Country mismatch for user {user_id}: "
                f"Expected {expected_country_code}, got {current_country}"
            )
            return True

        return False

    @staticmethod
    async def get_user_country_pattern(user_id: int, db) -> Optional[str]:
        """
        Get user's most common login country

        Analyzes login_history to determine typical location
        """
        from sqlalchemy import func
        from app.models.database import LoginHistory

        # Get most common country from last 30 days
        result = db.query(
            func.json_extract(LoginHistory.geo_location, '$.countryCode').label('country'),
            func.count().label('count')
        ).filter(
            LoginHistory.user_id == user_id,
            LoginHistory.is_successful == True
        ).group_by('country').order_by(func.count().desc()).first()

        if result:
            return result[0]  # Return country code

        return None


# Global geolocation service instance
geo_service = GeolocationService()
