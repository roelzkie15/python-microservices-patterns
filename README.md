# Python Microservice Patterns

##### Table of Contents
[Saga](#saga)

## Saga
When you use architecture with Database per Service then Saga is a way to go for distributed transactions.

A Saga is a sequence of local transactions and each transaction will publish messages or events that triggers the next local transaction.

If something went wrong to a participating microservice there should be a compensating transaction to undo the changes that were made by the preceding local transactions.

There are two types of Saga patterns:
- [__Choreography__](https://github.com/roelzkie15/python-microservice-patterns/tree/master/saga-choreograhpy-example) - Where microservices publish a message/event from a local transaction and trigger subscribers or participating microservices for the next local transaction.

- __Orchestration__ - Where microservices have an orchestrator to command what participating microservices should trigger the next local transaction and should receive a reply from that local transaction.

## WIP: More patterns to come...
