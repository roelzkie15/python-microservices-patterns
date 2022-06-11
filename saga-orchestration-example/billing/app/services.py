
from typing import List
from uuid import uuid4

from app.db import Session
from app.models import BillingRequest


async def billing_request_list(session: Session) -> List[BillingRequest]:
    return session.query(BillingRequest).all()
