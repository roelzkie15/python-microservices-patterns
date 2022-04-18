# Saga Choreography Example

There are five microservices that will work together to demonstrate this pattern. We will try to imitate a simple booking logic that will handle booking requests, billings, payments, and invoices.

## Techstack to implement servers:
- FastAPI
- Redis (Pub/Sub)
- Postgres

## Saga's Choreography Publish/Subscribe Event

![saga-choreography-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/f53b949850bb759730c4b97859ea9b7445a2b3e7/saga-choreograhpy-example/resources/saga-choreography-pattern.png)

1.	_Booking Service_ creates a new booking request, set the state to _pending_, publish an event called _**CREATED_BOOKING_EVENT**_.

1. Then _Manager Service_ listens to the _**CREATED_BOOKING_EVENT**_, approves the booking request, set the booking state to _approved_, publish _**APPROVED_BOOKING_EVENT**_.

1. The _Billing Service_ listens to the _**APPROVED_BOOKING_EVENT**_ then creates a billing item and publishes an event _**BILLED_BOOKING_EVENT**_.

1. The _Payment Service_ listens to the _**BILLED_BOOKING_EVENT**_ , payment options will be available for the customer and once the user submitted a a successful payment transaction, it will publish the _**PAID_BOOKING_EVENT**_.

1.	_Invoice Service_ listens to the _**PAID_BOOKING_EVENT**_ it will generate the invoice for the customer and triggers the _**INVOICE_GENERATED_EVENT**_.

1. Lastly, the _Booking Service_ listens to the _**INVOICE_GENERATED_EVENT**_ this will determine that the booking was successful and it will set the booking state into _reserved_.

## Compensating (Rollback) Transaction in Choreograhpy pattern

![saga-choreography-rollback-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/f53b949850bb759730c4b97859ea9b7445a2b3e7/saga-choreograhpy-example/resources/saga-choreography-pattern-rollback.png)

1. The _Payment service_ listens to the _**BILLED_BOOKING_EVENT**_, payment options will appear on the customer user interface and will submit  a payment transaction, then the payment service will check the customer available credits against the transaction and if the fund is not enough it will fire the _**INSUFFICIENT_FUND_EVENT**_.

2. The _Booking_ and _Billing_ services are listening to the _**INSUFFICIENT_FUND_EVENT**_ , it will then set both the booking request and the billing item to _failed_ states.
