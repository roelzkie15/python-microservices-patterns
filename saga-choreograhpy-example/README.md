# Saga Choreography Example

There are six microservices that will work together to demonstrate this pattern. We will try to imitate a simple car parking app logic that will handle booking requests, billings, payments, and invoices.

Techstack to implement servers:
- FastAPI
- Redis (Pub/Sub)
- Postgres

Use case:

![saga-choreography-pattern](https://github.com/roelzkie15/python-microservice-patterns/blob/75283655fdaa9ed06ca2db77e6946021320ba223/saga-choreograhpy-example/resources/saga-choreography-pattern.png)
