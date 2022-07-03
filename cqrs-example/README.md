# Command Query Responsibility Segregation (CQRS) Example

This example will have a single domain (Parking) to test CQRS read and write operations.

## Techstack to implement servers

- Starlette (used by FastAPI)
- RabbitMQ
- Postgres
- SQLAlchemy (Handle read and write router)
- Docker

## Running the applications

You must be in the root directory of this repository (python-microservices-patterns) where the `compose` directory is located and not at the `saga-orchestration-example/` directory.

- Build CQRS docker images:

        docker-compose -f compose/cqrs.yml build --no-cache

- Run the services via docker-compose:

        docker-compose -f compose/cqrs.yml up

- **CQRS Service** should be running at localhost:8000.
- The Event Consumer server should be waiting for events with the following console message:

        Event consumer for parking slot replication is running...

## CQRS 

### Workflow

![cqrs-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/cqrs/cqrs-example/resources/cqrs-pattern.png)

1. Create a parking slot in **CQRS Service**, this will trigger _**parking.create**_ event. Also within this event it will create parking slot record to the primary database.
2. The **Event Consumer** listens to _**parking.create**_ event and create the parking slot data to the replicate database.
3. After creation parking slot data is printed into the console, at this point the data were pulled from the replica database.

## Workflow in action

Assuming that all docker services are running. We can now execute the above workflow by taking the following steps:

> **Note**: You may need to ssh to the cqrs service container via docker exec -it <service_container_id> bash for the CLI to work.

1. Create a parking slot. Make sure you are within the**CQRS Service** container in a bash session:

    ```
    poetry run python -m app.cli create_parking_slot --name='Slot 1'

    # Output:
    uuid:   2e817460-b54d-4119-b2fc-61bc86943aca
    name:   Slot 1
    status: available
    ```

1. Check if the data created above is also replicated to the replica database go to its server bash session and execute the following

    ```
    postgres=# select * from parking_slots;

    # Output:

                    uuid                 |       name        |  status   
    --------------------------------------+-------------------+-----------
    2e817460-b54d-4119-b2fc-61bc86943aca | Slot 1            | available
    ```

    > You can also do the same for the primary database server to check the data.

1. Now it's not obvious if the **CQRS Service** is getting its data from the replica database. You can modify the replica record just for the sake of example and execute the parking slot list command line within the **CQRS Service** and see if it displays data from the replica database.

    Make sure you are in the replica database server psql session.
    ```
    # Update parking slot
    postgres=# update parking_slots set name='Slot 1 replicated' where uuid = '2e817460-b54d-4119-b2fc-61bc86943aca';

    # Output:
    UPDATE 1

    # List parking slots
    postgres=# select * from parking_slots;

    # Output
                        uuid                 |       name        |  status   
    --------------------------------------+-------------------+-----------
    2e817460-b54d-4119-b2fc-61bc86943aca | Slot 1 replicated | available
    ```

    Now open bash session in **CQRS Service** and list all created parking slot by using the following command line:

    ```
    poetry run python -m app.cli parking_slot_list

    # Output:
    {"uuid": "2e817460-b54d-4119-b2fc-61bc86943aca", "name": "Slot 1 replicated", "status": "available"}
    ```

    The result should display data from the replica database.

## Benefits and drawbacks of CQRS Pattern

- Faster response delivery as you can use a SQL data store for write operation and NoSQL data store for read operation.
- Highly availabity and scalability as it can be placed to a geolocation where data consumer can access information with reduced response latency.
- Replica database can be stale (Eventual consistency).
- Can add complexity to the project and may lead to put the system at risk.
- Using more replica databases may lead to more problems if not handled properly.


## When to use CQRS

- You should only use this within the part of a system that have overwhelming read activity than write activity.

## When not to use CQRS

- Smaller systems that have a minimal read activity.
- Where CRUD operation is enough.

