import strawberry

from app.pydantic_models import PydanticBillingRequest

@strawberry.experimental.pydantic.type(model=PydanticBillingRequest, all_fields=True)
class BillingRequestType:
    pass
