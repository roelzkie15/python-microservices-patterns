# Python Microservice Patterns

##### Table of Contents
[Saga](#saga)

## Saga
When you use architecture with Database per Service then Saga pattern is a way to go for distributed transactions.

A Saga is a sequence of a local transactions and each transaction will publish messages or events that triggers the next local transaction.

In Saga pattern if something went wrong to a participating service there should be a compensating transaction to undo the changes that were made by the preceding local transactions.

There are two types of Saga patterns:
- __Choreography__ - Where microservices publish a message/event from a local transaction and trigger subscribers or participating microservices for next local transaction.

- __Orchestration__ - Where microservices have an orchestrator to command what participating services should trigger local transaction.
