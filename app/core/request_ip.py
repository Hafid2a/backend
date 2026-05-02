from typing import Optional

from fastapi import Request


def get_client_ip(request: Request) -> Optional[str]:
    """Best-effort client IP: X-Forwarded-For first hop, then X-Real-IP, then direct client."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip() or None
    if request.client:
        return request.client.host
    return None
