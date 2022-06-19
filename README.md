# Python Microservices Patterns

##### Table of Contents
[Saga](#saga)

## Saga
When you use **Database per Service** design you will need to consider **Saga** for distributed transactions to maintain data consistency across multiple services.

A Saga is a sequence of local transactions and each transaction will publish messages or events that trigger the next local transaction.

If something goes wrong to a participating microservice, there should be a compensating transaction to undo the changes that were made by the preceding local transactions.

There are two popular Saga patterns:
- [__Choreography__](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-choreography-example) - Where microservices publish a message/event from a local transaction and trigger subscribers or participating microservices for the next local transaction.

- [__Orchestration__](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-orchestration-example) - Where microservices have an orchestrator to command what participating microservices should trigger the next local transaction and should receive a reply from that local transaction.

## WIP: More patterns to come...
