# Saga Orchestration Example

To demonstrate this pattern we will still have to use the same distributed system architecture from the [Saga Choreography Example](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-choreography-example) but with more simplified version and shorter workflow for booking, billing and parking services.

## Techstack to implement servers

- Starlette (used by FastAPI)
- RabbitMQ (RPC Pattern for Saga Orchestration reply/response)
- SQLite
- Docker


## Running the applications

You must be in the root directory of this repository (python-microservices-patterns) where the `compose/` directory is located and not at the `saga-orchestration-example/` directory.

- Build saga orchestration docker images:

    ```
    docker-compose -f compose/saga-orchestration.yml build --no-cache
    ```

- Run the services via docker-compose:

    ```
    docker-compose -f compose/saga-orchestration.yml up
    ```

- Parking service is running at localhost:8000
- Booking service is running at localhost:8001
- Billing service is running at localhost:8002
- To check the server health just append `/health` url at the end of the `localhost:port` (e.g. `localhost:8000/health` to check parking service health)


## Saga's Orchestration/Command Logic

### Workflow

![saga-orchestration-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/resources/saga-orchestration-pattern.png)

1. Customer initiate a booking request for a parking slot and will start the **Booking Saga Orchestrator** or **BSO** which will create a new booking record with _pending_ status.

1. It will then send a _**parking.block**_ command to **Parking Service** to lock the parking slot. If the parking slot is _available_. Trigger a _PARKING_AVAILABLE_ event to the **BSO** reply channel.

1. The **BSO** will proceed to the next transaction by firing a _**billing.authorize_payment**_ command to **Billing Service**. It will then produce a _PAYMENT_SUCCESSFUL_ event to the **BSO** reply channel.

1. The **BSO** will proceed to another next transaction sending a _**parking.reserve**_ command to  **Parking Service** to set the parking record to _reserved_ and will return a _PARKING_RESERVED_ event to the **BSO** reply channel.

1. Finally, the **BSO** will proceed to the next local transaction by setting the current booking request status to _completed_.

### Workflow in action

Assuming that all docker services are running. We can now execute the above workflow by taking the following steps:

> **Note**: You may need to ssh to the given service container via docker exec -it <service_container_id> bash for the CLI to work.

1. Create a parking slot. Make sure you are within the **Parking Service** container in a bash session:

    ```
    poetry run python -m app.cli create_parking_slot --name='Slot 1'

    # Output:
    uuid:   080435ac-fce7-4e91-8880-30b8a277d830
    name:   Slot 1
    status: available
    ```

1. Booking request for parking slot. Make sure you are within the **Booking Service** container in a bash session:

    ```
    poetry run python -m app.cli create_booking_request '080435ac-fce7-4e91-8880-30b8a277d830'

    # Output:
    INFO:root:Booking request workflow done.
    ```

1. On **Billing Service** bash session:

    ```
    poetry run python -m app.cli billing_request_list

    # Output:
    {'id': 1, 'total': Decimal('100.00'), 'status': 'paid', 'reference_no': '080435ac-fce7-4e91-8880-30b8a277d830:ae949fae-0a91-4e62-be0c-4f950963abaa'}
    ```

    Billing request was paid.

1. On **Parking Service** bash session:

    ```
    poetry run python -m app.cli parking_slot_list

    # Output:
    {"uuid": "080435ac-fce7-4e91-8880-30b8a277d830", "name": "Slot 1", "status": "reserved"}
    ```

    Parking slot was reserved.

1. List booking request:

    ```
    poetry run python -m app.cli booking_list

    # Output:
    {"id": 1, "status": "completed", "parking_slot_ref_no": "080435ac-fce7-4e91-8880-30b8a277d830:ae949fae-0a91-4e62-be0c-4f950963abaa"}
    ```

    Booking request was completed.

## Compensating (Rollback) Transaction in Orchestration pattern

![saga-orchestration-pattern-rb-tx](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/resources/saga-orchestration-pattern-rb-transaction.png)

1. The **BSO** initiate a _**parking.reserve**_ command to the **Parking Service**.

1. The **Parking Service** return a _PARKING_RESERVATION_FAILED_ event to **BSO** reply channel.

1. The **BSO** will listen to the _PARKING_RESERVATION_FAILED_ event and proceed to the next transaction by sending _**billing.refund**_ command to **Billing Service** and produces a _BILL_REFUNDED_ event to the **BSO** reply channel.

1. Also the **BSO** will listen to the _BILL_REFUNDED_ event and execute a local transaction to set the current booking request to _failed_.

# Compensation transaction in action

> **Note**: You may need to ssh to the given service container via docker exec -it <service_container_id> bash for the CLI to work.

1. To allow compensation transaction we need to fail the step 4 transaction of the original workflow by following this [instruction](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-orchestration-example/parking/app/services.py#L98). This will fail reserving the parking slot.

1. Now create a booking request for parking slot. Make sure you are within the **Booking Service** container in a bash session:

    ```
    poetry run python -m app.cli create_booking_request '080435ac-fce7-4e91-8880-30b8a277d830'

    # Output:
    INFO:root:Booking request workflow done.
    ```

1. On **Billing Service** bash session:

    ```
    poetry run python -m app.cli billing_request_list

    # Output:
    {'id': 1, 'total': Decimal('100.00'), 'status': 'refunded', 'reference_no': '080435ac-fce7-4e91-8880-30b8a277d830:ae949fae-0a91-4e62-be0c-4f950963abaa'}
    ```

    The billing request status was set to _refunded_.

1. On **Parking Service** bash session:

    ```
    poetry run python -m app.cli parking_slot_list

    # Output:
    {"uuid": "080435ac-fce7-4e91-8880-30b8a277d830", "name": "Slot 1", "status": "available"}
    ```

    Since reservation _failed_ it will rollback the parking status to _available_. So we can start requesting another booking request for this parking slot again.

1. On **Booking Service** bash session:

    ```
    poetry run python -m app.cli booking_list

    # Output:
    {"id": 1, "status": "failed", "parking_slot_ref_no": "080435ac-fce7-4e91-8880-30b8a277d830:ae949fae-0a91-4e62-be0c-4f950963abaa"}
    ```

    Finally, the booking request status was set to _failed_.

## Benefits and drawbacks of Saga's Orchestration Pattern

- Complex saga orchestration implementation.
- No cyclic dependency.
- Distribution of transactions are centralized.
- Testable Orchestrator commands.
- Handle rollback transaction better.
