# Saga Choreography Example

There are 3 microservices that will work together to demonstrate this pattern. We will try to imitate a simple booking logic that will handle booking requests, billings and parking slots.

## Techstack to implement servers

- FastAPI
- RabbitMQ
- Postgres
- GraphQL

## Saga's Choreography Publish/Subscribe Event

![saga-choreography-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-choreograhpy-example/resources/saga-choreography-pattern.png)

1. _**Booking Service**_ creates a new booking request, set the state to _pending_, publish an event called **CREATE_BOOKING_EVENT**.

1. _**Billing Service**_ listens to **CREATE_BOOKING_EVENT** creates a billing request and charge the customer. When Payment has been made, trigger **BILL_PAID_EVENT**.

1. _**Parking Service**_ listens to **BILL_PAID_EVENT**  then modify parking space status to _reserved_ and fires **RESERVED_BOOKING_EVENT**.

1. _**Booking Service**_ listens to **RESERVED_BOOKING_EVENT** and set the current booking request to _done_.

## Compensating (Rollback) Transaction in Choreograhpy pattern

![saga-choreography-rollback-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-choreograhpy-example/resources/saga-choreography-pattern-rb-transaction.png)

1. _**Parking Service**_ publishes **PARKING_UNAVAILABLE_EVENT**, and _**Booking Service**_ listens to it and updates booking request status to _failed_.

1. _**Billing Service**_ listens to **PARKING_UNAVAILABLE_EVENT** refund payment to customer and updates billing status to _refunded_.

> **Important:** Participating microservices should recognize transactions by using unique identifiers from a certain event to know what transaction is being processed.
