"""
AGTR Merkezi - Request Helper Functions
Request'lerden bilgi almak için yardımcı fonksiyonlar
"""

from typing import Optional

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    Request'ten gerçek client IP'sini al (proxy arkasında bile)

    Args:
        request: FastAPI Request object

    Returns:
        str: Client IP adresi
    """
    # X-Forwarded-For header'ı kontrol et (proxy arkasında)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Birden fazla proxy varsa ilk IP'yi al
        return forwarded.split(",")[0].strip()

    # X-Real-IP header'ı kontrol et
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # CF-Connecting-IP (Cloudflare)
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()

    # Direkt client IP
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> Optional[str]:
    """
    Request'ten User-Agent bilgisini al

    Args:
        request: FastAPI Request object

    Returns:
        str: User agent string veya None
    """
    return request.headers.get("User-Agent")


def get_referer(request: Request) -> Optional[str]:
    """
    Request'ten Referer bilgisini al

    Args:
        request: FastAPI Request object

    Returns:
        str: Referer URL veya None
    """
    return request.headers.get("Referer")


def is_ajax_request(request: Request) -> bool:
    """
    Request AJAX mi kontrol et

    Args:
        request: FastAPI Request object

    Returns:
        bool: AJAX request ise True
    """
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def is_mobile_request(request: Request) -> bool:
    """
    Request mobil cihazdan mı kontrol et (basit)

    Args:
        request: FastAPI Request object

    Returns:
        bool: Mobil cihazdan ise True
    """
    user_agent = get_user_agent(request)
    if not user_agent:
        return False

    mobile_keywords = [
        "Mobile", "Android", "iPhone", "iPad", "iPod",
        "BlackBerry", "Windows Phone", "Opera Mini"
    ]

    return any(keyword in user_agent for keyword in mobile_keywords)


def get_request_metadata(request: Request) -> dict:
    """
    Request'ten tüm önemli metadata'yı topla

    Args:
        request: FastAPI Request object

    Returns:
        dict: Request metadata'sı
    """
    return {
        "ip": get_client_ip(request),
        "user_agent": get_user_agent(request),
        "referer": get_referer(request),
        "is_ajax": is_ajax_request(request),
        "is_mobile": is_mobile_request(request),
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path
    }


def get_client_country(request: Request) -> Optional[str]:
    """
    Request'ten client ülke bilgisini al (Cloudflare veya benzeri kullanıyorsa)

    Args:
        request: FastAPI Request object

    Returns:
        str: Ülke kodu (ISO 3166-1 alpha-2) veya None
    """
    # Cloudflare
    cf_country = request.headers.get("CF-IPCountry")
    if cf_country and cf_country != "XX":
        return cf_country

    # AWS CloudFront
    cloudfront_country = request.headers.get("CloudFront-Viewer-Country")
    if cloudfront_country:
        return cloudfront_country

    return None
