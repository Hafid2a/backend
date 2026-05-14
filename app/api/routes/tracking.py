import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_ip import get_client_ip
from app.db.models import ClickEvent, utcnow
from app.db.session import get_db
from app.services.maxmind_geo import evaluate_ip_for_ksa_traffic

router = APIRouter(prefix="/tracking", tags=["tracking"])


class UTMData(BaseModel):
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None


class ClickIds(BaseModel):
    fbclid: Optional[str] = None
    ttclid: Optional[str] = None
    sc_click_id: Optional[str] = None


class ClickEventIn(BaseModel):
    event_id: Optional[str] = None
    landing_page: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    utm: Optional[UTMData] = None
    click_ids: Optional[ClickIds] = None


@router.post("/click", status_code=status.HTTP_202_ACCEPTED)
async def track_click(
    body: ClickEventIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    client_ip = get_client_ip(request)
    validation = await evaluate_ip_for_ksa_traffic(client_ip)
    utm = body.utm
    click_ids = body.click_ids
    event = ClickEvent(
        id=uuid.uuid4(),
        event_id=body.event_id or str(uuid.uuid4()),
        client_ip=client_ip,
        country_code=validation.country_code,
        is_valid_ksa_ip=validation.allowed,
        ip_check_provider=validation.provider,
        ip_reject_reason=validation.reason,
        landing_page=body.landing_page,
        referrer=body.referrer,
        user_agent=body.user_agent or request.headers.get("user-agent"),
        utm_source=utm.utm_source if utm else None,
        utm_medium=utm.utm_medium if utm else None,
        utm_campaign=utm.utm_campaign if utm else None,
        utm_content=utm.utm_content if utm else None,
        utm_term=utm.utm_term if utm else None,
        fbclid=click_ids.fbclid if click_ids else None,
        ttclid=click_ids.ttclid if click_ids else None,
        sc_click_id=click_ids.sc_click_id if click_ids else None,
        created_at=utcnow(),
    )
    db.add(event)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {"ok": True, "counted": validation.allowed, "duplicate": True}
    return {"ok": True, "counted": validation.allowed}
