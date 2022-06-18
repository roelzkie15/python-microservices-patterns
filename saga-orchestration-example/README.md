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

1. Customer initiate a booking request for a parking slot and will start the **Booking Saga Orchestrator** or **BSO** which will create a new booking record with _pending_ status.

1. It will then send a _**parking.block**_ command to **Parking Service** to lock the parking slot. If the parking slot is _available_. Trigger a _PARKING_AVAILABLE_ event to the **BSO** reply channel.

1. The **BSO** will proceed to the next step by updating the booking status to _approved_ and afterward fire a _**billing.pay**_ command to **Billing Service** to create a billing record with _paid_ status. It will then produce a _BILL_PAID_ event to the **BSO** reply channel.

1. Finally **BSO** will proceed to another next step sending a _**parking.reserve**_ command to  **Parking Service** to set the parking record to _reserved_.

## Compensating (Rollback) Transaction in Orchestration pattern (WIP)

![saga-orchestration-pattern-rb-tx](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/resources/saga-orchestration-pattern-rb-transaction.png)

1. The **BSO** initiate the _**pay.bill**_ command to the **Billing Service**.

1. The **Billing Service** failed to record the payment process and produces a  _BILL_FAILED_ event to the **BSO** reply channel.

1. The **BSO** will listen to the _BILL_FAILED_ event from the reply channel and will send _**parking.unblock**_ command to the **Parking Service** to set the parking status to _available_ again.

1. Also the **BSO** will proceed to another _BILL_FAILED_ listener and will invoke local transaction to **Booking Service** to set the current booking request to rejected.
