
from typing import List

from app.db import Session
from app.models import BillingRequest


async def create_billing_request(session: Session, reference_no: str) -> BillingRequest:
    br = BillingRequest(
        # Default total to 100.00
        total=100.0,
        reference_no=reference_no
    )
    session.add(br)
    session.commit()
    session.refresh(br)

    return br


async def billing_request_details_by_reference_no(session: Session, reference_no: str) -> BillingRequest:
    return session.query(BillingRequest).filter(BillingRequest.reference_no == reference_no).one()


async def billing_request_list(session: Session) -> List[BillingRequest]:
    return session.query(BillingRequest).all()
