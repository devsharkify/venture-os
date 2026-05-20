"""Lightweight admin auth dependency.

Mint Street uses OTP-based auth without JWT sessions. The frontend stores the
authenticated user's phone in localStorage. To gate sensitive admin endpoints
(PII-bearing exports, status updates), we verify an admin phone number passed
either via the `X-Admin-Phone` header or the `admin_phone` query string.

This is intentionally lightweight (no crypto) — it matches the existing
client-side admin gate (`phone === ADMIN_PHONE`) and is sufficient to prevent
casual scraping of /api/admin/* endpoints from public crawlers.
"""
from fastapi import Header, HTTPException, Query
from typing import Optional


ADMIN_PHONE = "7386917770"


def _clean(phone: str) -> str:
    if not phone:
        return ""
    return (
        phone.replace("+91", "").replace("+", "").replace(" ", "").replace("-", "").strip()[-10:]
    )


async def require_admin(
    x_admin_phone: Optional[str] = Header(default=None),
    admin_phone: Optional[str] = Query(default=None),
) -> str:
    """Dependency that blocks non-admin callers.

    Accepts the admin phone via either:
    - Header: X-Admin-Phone: 7386917770
    - Query param: ?admin_phone=7386917770  (useful for browser file downloads
      such as window.open that cannot set headers)

    Raises 401 if not provided, 403 if wrong number.
    """
    phone = _clean(x_admin_phone or admin_phone or "")
    if not phone:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    if phone != ADMIN_PHONE:
        raise HTTPException(status_code=403, detail="Admin access only")
    return phone
