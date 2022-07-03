# Python Microservices Patterns

## Table of Contents
1. [Command Query Responsibility Segregation (CQRS)](#cqrs)
1. [Event Sourcing](#event-sourcing)
1. [Saga](#saga)
    - [Choreography](#saga-choreography)
    - [Orchestration](#saga-orchestration)
1. [API Gateway](#api-gateway)
1. [Backend for Frontend (BFF)](#bff)
1. [Circuit Breaker](#circuit-breaker)

<div id="cqrs"/>

## Command Query Responsibility Segregation (CQRS)

CQRS is a popular architectural pattern that separates write (Command) part and read (Query) part to boost system overall performance and promotes better response delivery.

When the system has an overwhelming read activity than write activity this pattern helps lessen the database workloads and avoid system bottleneck.

It also amplify scalability as read databases or replicas data sources can be placed in a geolocation where data consumer can access information with reduced response latency.

See python CQRS example [here](https://github.com/roelzkie15/python-microservices-patterns/tree/cqrs/cqrs-example).

<div id="event-sourcing"/>

## Event Sourcing

WIP

<div id="saga"/>

## Saga
When you use **Database per Service** design you will need to consider **Saga** for distributed transactions to maintain data consistency across multiple services.

A Saga is a sequence of local transactions and each transaction will publish messages or events that trigger the next local transaction.

If something goes wrong to a participating microservice, there should be a compensating transaction to undo the changes that were made by the preceding local transactions.

There are two popular Saga patterns:

<div id="saga-choreography"/>

- [__Choreography__](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-choreography-example) - Where microservices publish a message/event from a local transaction and trigger subscribers or participating microservices for the next local transaction.

<div id="saga-orchestration"/>

- [__Orchestration__](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-orchestration-example) - Where microservices have an orchestrator to command what participating microservices should trigger the next local transaction and should receive a reply from that local transaction.


<div id="api-gateway"/>

## API Gateway

WIP

<div id="bff"/>

## Backend for Frontend

WIP

<div id="circuit-breaker"/>

## Circuit Breaker

WIP