from typing import List

import strawberry

from app.pydantic_models import (
    PydanticBillingRequest,
    PydanticBillingRequestWithPaymentReconciliation,
    PydanticPaymentReconciliation
)


@strawberry.experimental.pydantic.type(model=PydanticBillingRequest, all_fields=True)
class BillingRequestType:
    pass


@strawberry.experimental.pydantic.type(model=PydanticPaymentReconciliation, all_fields=True)
class PaymentReconciliationType:
    pass


@strawberry.experimental.pydantic.type(model=PydanticBillingRequestWithPaymentReconciliation, all_fields=True)
class BillingRequestWithReconciliationType:
    pass


@strawberry.type
class PaymentOverError:
    message: str = 'Payment amount exceed billing total.'
    status_code: int = 422


@strawberry.type
class BillingAlreadyPaidError:
    message: str = 'Bill is already paid'
    status_code: int = 422


# Create a Union type to represent the 2 results from the mutation
PayBillActionResponse = strawberry.union(
    'PayBillActionResponse', [PaymentReconciliationType,
                              PaymentOverError, BillingAlreadyPaidError]
)
