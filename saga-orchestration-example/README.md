# Saga Orchestration Example

To demonstrate this pattern we will still have to use the same distributed system architecture from the [Saga Choreography Example](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-choreograhpy-example) but with more simplified version and shorter workflow for booking, billing and parking services.

## Techstack to implement servers

- Starlette (used by FastAPI)
- RabbitMQ
- SQLite
- Docker

## Saga's Orchestration/Command Logic

### Workflows

1. Customers request a booking for a parking slot and will start the **Booking Saga Orchestrator** or **BSO**.

1. The **BSO** will create a new booking record with _pending_ status. It will then send a _**parking.check_availability**_ command to the **Parking Service** through the **Parking Channel**.

1. The **Parking Service** will check the availability of the parking slot base on the customer's booking and will send a reply to the **BSO** via **Booking Saga Orchestrator Reply Channel**. The **BSO** will either reject or approve the booking based on the outcome of the **Parking Service** reply.
