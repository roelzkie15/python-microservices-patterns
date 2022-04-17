# Saga Choreography Example

There are six microservices that will work together to demonstrate this pattern. We will try to imitate a simple car parking app logic that will handle booking requests, billings, payments, and invoices.

## Techstack to implement servers:
- FastAPI
- Redis (Pub/Sub)
- Postgres

## Saga's Choreography Publish/Subscribe Event

![saga-choreography-pattern](https://github.com/roelzkie15/python-microservice-patterns/blob/75283655fdaa9ed06ca2db77e6946021320ba223/saga-choreograhpy-example/resources/saga-choreography-pattern.png)

1.	_Booking Service_ creates a new booking request, set the state to _pending_, publish an event called _**CREATED_BOOKING_EVENT**_.

1. Then _Manager Service_ listens _**CREATED_BOOKING_EVENT**_, approves the booking request, set the booking state to _approved_, publish _**APPROVED_BOOKING_EVENT**_.

1. The _Billing Service_ listens to the _**APPROVED_BOOKING_EVENT**_ then creates a billing item and publishes an event _**BILLED_BOOKING_EVENT**_.

1. The _Driver Service_ listens to the _**BILLED_BOOKING_EVENT**_, driver will be notified for the billing and be prompted to submit payment that will produce an event called _**PAYMENT_SUBMITTED_BOOKING_EVENT**_.

1. The _Payment Service_ listens to the _**PAYMENT_SUBMITTED_BOOKING_EVENT**_  it will then process and verify the payment that has been made and once successful it will trigger the _**PAID_BOOKING_EVENT**_.

1.	_Invoice Service_ listens to the _**PAID_BOOKING_EVENT**_ it will generate the invoice for the driver and triggers the _**INVOICE_GENERATED_EVENT**_ event.

1. Lastly, the _Booking Service_ listens to the _**INVOICE_GENERATED_EVENT**_ this will determine that the booking was successful and it will set the state into _paid_.