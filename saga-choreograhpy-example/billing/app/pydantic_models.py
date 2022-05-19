from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from app.models import BillingRequest

PydanticBillingRequest = sqlalchemy_to_pydantic(BillingRequest)
