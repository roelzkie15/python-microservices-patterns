# Saga Orchestration Example

To demonstrate this pattern we will still have to use the same distributed system architecture from the [Saga Choreography Example](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-choreograhpy-example) but with more simplified version and shorter workflow for booking, billing and parking services.

## Techstack to implement servers

- Starlette (used by FastAPI)
- RabbitMQ
- SQLite
- Docker

## Saga's Orchestration/Command Logic

### Workflows

![saga-orchestration-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/resources/saga-orchestration-pattern.png)

1. Customer request a booking to a parking slot and will start the **Booking Saga Orchestrator** or **BSO**.

1. The **BSO** will create a new booking record with _pending_ status.

1. It will then send a _**parking.availability_check**_ command to the **Parking Service** through the **Parking Channel**.

1. The **Parking Service** will check the availability of the parking slot base on the customer's booking request and will send a reply to the **BSO** via **Booking Saga Orchestrator Reply Channel**.

1. If the <b>Parking Service</b> sent a <b><i>parking.available</i></b> to the reply channel, the <b>BSO</b> will fire <b>booking.approved</b> command to <b>Booking Service</b> to update the booking status and <b>billing.create</b> command to <b>Billing Service</b> to create bills to customers.

## Compensating (Rollback) Transaction in Orchestration pattern

### Workflows

1. The <b>Parking Service</b> sent a <i><b>parking.unavailable</b></i> to the reply channel.
1. The <b>BSO</b> will fire <b>booking.rejected<b> command to <b>Booking Service</b> to update the booking status to _rejected_.

    ![saga-orchestration-pattern-rb-transaction](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/resources/saga-orchestration-pattern-rb-transaction.png)
