# Saga Orchestration Example

To demonstrate this pattern we will still have to use the same distributed system architecture from the [Saga Choreography Example](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-choreograhpy-example) but with more simplified version and shorter workflow for booking, billing and parking services.

## Techstack to implement servers

- Starlette (used by FastAPI)
- RabbitMQ (RPC Pattern for Saga Orchestration)
- SQLite
- Docker

## Saga's Orchestration/Command Logic

### Workflows

![saga-orchestration-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/resources/saga-orchestration-pattern.png)

> NOTE: Image is outdated.

1. Customer request a booking to a parking slot and will start the **Booking Saga Orchestrator** or **BSO**.

1. The **BSO** will create a new booking record with _pending_ status.

1. It will then send a _**parking.reserve**_ command to the **Parking Service** through the **Parking Channel**.

1. The **Parking Service** will check the availability of the parking slot base on the customer's booking request and will send a reply to the **BSO** via **Booking Saga Orchestrator Reply Channel**. If the parking slot is _available_ then the <b>Parking Service</b> will send a <b><i>PARKING_AVAILABLE</i></b> event to the reply channel.

1. The <b>BSO</b> will update the booking status to _approved_.

1. The <b>BSO</b> also fire <b>billing.create</b> command to <b>Billing Service</b> to create a bill to the customer.

1. The **Billing Service** will reply a <b><i>BILL_CREATED</i></b> event to the reply channel and the <b>BSO</b> will update the booking request status into _billed_.

## Compensating (Rollback) Transaction in Orchestration pattern

### Workflows

![saga-orchestration-pattern-rb-transaction](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/resources/saga-orchestration-pattern-rb-transaction.png)

> NOTE: Image is outdated.

1. The <b>Parking Service</b> sent a <i><b>PARKING_UNAVAILABLE</b></i> event to the reply channel.
1. Then <b>BSO</b> will send <b>parking.unblock</b> to the **Parking Service** to unblock the parking slot.
1. Finally, the <b>BSO</b> will update the booking request status to _rejected_.
