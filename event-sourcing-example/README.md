# Event Sourcing

To utilize this example we will rely on python [eventsourcing](https://github.com/pyeventsourcing/eventsourcing) library to handle basic event sourcing pattern. It will also have a [CQRS](https://github.com/roelzkie15/python-microservices-patterns/tree/master/cqrs-example) pattern which is necessary to separate event store (storing of events) and projector (presentation of data) data source.

## Techstack to implement servers
- Starlette (used by FastAPI)
- RabbitMQ
- PostgreSQL
- SQLite3
- SQLAlchemy
- Docker
- Pyeventsourcing


## Running the applications

You must be in the root directory of this repository (python-microservices-patterns) where the `compose/` directory is located and not at the `event-sourcing-example/` directory.

- Build event-sourcing docker images:

        docker-compose -f compose/event-sourcing.yml build --no-cache

- Run the services via docker-compose:

        docker-compose -f compose/event-sourcing.yml up

- There'll be no UI presentation for this example but successfull indications are it would run these servers:
    - `es-event-store-db` PostgreSQL server for storing events.
    - `es-projector-db` PostgreSQL server for data presentation.
    - **Booking Service**.
    - **Parking Service**.
    - RabbitMQ server.

## Event Sourcing

### Workflow

![event-sourcing-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/e4ed20fff485dbcb1bcdf1850f7956c6486c09c4/event-sourcing-example/resources/event-sourcing-pattern.png)

1. On the **Parking Service**.
    - Create parking slot.
1. On the **Booking Service**.
    - Create booking request for a parking slot. Stores the `BookingCreated` event to the event store database.
    - Set the booking as reserved. Stores the  `BookingReserved` event to the event store database.
    - Set the booking as completed. Stores the `BookingCompleted` event to the event store database.
    - Retrieve booking details or list from the projector database.
    - Retrive booking event history from the event store database.
1. On the `Parking` service again.
    - `Parking` service is also subscribed to each events (`BookingCreated`, `BookingReserved`, and `BookingCompleted`) and it will also update the parking slot status based on the produced event.
    - Retrieve parking slot details or list from the `Parking` service.

### Workflow in action

Assuming that all docker services are running. We can now execute the above workflow by taking the following steps:

> **Note**: You may need to start a bash session to the event-sourcing services containers via docker exec -it <service_container_id> bash for the CLI to work.

1. Create a parking slot on a **Parking Service**.

    ```
    poetry run python -m app.cli create_parking_slot 'Slot 1'

    # Output:
    uuid:   c9ed7097-05ee-4ab6-8361-3a2a3dee00e3
    name:   Slot 1
    status: available
    ```

    This will create a parking slot with a status `available`. You can create as many as you want to test.

1. Create a booking request for a parking slot on **Booking Service**.

    ```
    poetry run python -m app.cli create_booking_request c9ed7097-05ee-4ab6-8361-3a2a3dee00e3

    # Output:
    daab05c7-5d8f-4480-9a95-8d042e2948db
    ```

    The returned UUID value is the `Booking` object domain uuid. Under the hood there are several things that are happening on this booking object:

    - This will create a `BookingCreated` event of the given booking request aggregate on the event-store database. You can view the booking history by taking the domain UUID value.

        ```
        poetry run python -m app.cli get_booking_events daab05c7-5d8f-4480-9a95-8d042e2948db

        # Output
        {
            'id': UUID('daab05c7-5d8f-4480-9a95-8d042e2948db'),
            'version': 1,
            'parking_slot_ref_no': 'c9ed7097-05ee-4ab6-8361-3a2a3dee00e3',
            'status': 'created'
        }
        ```

        At this point we only have the `BookingCreated` event in the event-store. Also keep in mind that a single `Booking` instance can have multiple events stored on the event-store database. We will go through it in a later section of this example.

    - A `Booking` instance is created for this event, stored on the projector database as a single representation of this data. This data shows the actual and the most recent data of the `Booking` instance.

        ```
        poetry run python -m app.cli get_booking_details daab05c7-5d8f-4480-9a95-8d042e2948db

        # Output
        id:                  3
        domain_uuid:         daab05c7-5d8f-4480-9a95-8d042e2948db
        status:              created
        parking_slot_ref_no: c9ed7097-05ee-4ab6-8361-3a2a3dee00e3
        ```

    - After the `BookingCreated` event is created. The **Parking Service** listens to every events that happened to the `Booking` instance and will also update the parking instance in the **Parking Service**. This pattern utilized the basic [Saga Choreography](https://github.com/roelzkie15/python-microservices-patterns/tree/master/saga-choreography-example) pattern. See the current state of the parking slot.

        ```
        poetry run python -m app.cli parking_slot_details c9ed7097-05ee-4ab6-8361-3a2a3dee00e3

        # Output
        uuid:   c9ed7097-05ee-4ab6-8361-3a2a3dee00e3
        name:   Slot 1
        status: blocked
        ```

        Now it's `blocked` because someone made a request for this parking slot and is pending whether to approve or reject the booking but for the sake of simplicity we will not cover the whole booking process workflow and leave the reject operation and focus on event-sourcing pattern on the `Booking` instance.

1. Now the booking request must be reserved. On the **Booking Service** execute the reservation command:

    ```
    poetry run python -m app.cli reserve_booking daab05c7-5d8f-4480-9a95-8d042e2948db

    # Output
    daab05c7-5d8f-4480-9a95-8d042e2948db
    ```

    This command will return the same `Booking` domain uuid. The same logic will happen back on Point 2 the difference is it will create the `BookingReserved` event to the event store and update the `Booking` instance status and the `ParkingSlot` status to `reserved`.

    To see the booking events:

        poetry run python -m app.cli get_booking_events daab05c7-5d8f-4480-9a95-8d042e2948db

        # Output
        {
            'id': UUID('daab05c7-5d8f-4480-9a95-8d042e2948db'),
            'version': 1,
            'parking_slot_ref_no': 'c9ed7097-05ee-4ab6-8361-3a2a3dee00e3',
            'status': 'created'
        }
        {
            'id': UUID('daab05c7-5d8f-4480-9a95-8d042e2948db'),
            'version': 2,
            'status': 'reserved'
        }


    To see the current state of the `Booking` instance.

        poetry run python -m app.cli get_booking_details daab05c7-5d8f-4480-9a95-8d042e2948db

        # Output
        id:                  3
        domain_uuid:         daab05c7-5d8f-4480-9a95-8d042e2948db
        status:              reserved
        parking_slot_ref_no: c9ed7097-05ee-4ab6-8361-3a2a3dee00e3

    To see the current state of the `ParkingSlot` instance on the **Parking Service**.

        python -m app.cli parking_slot_details c9ed7097-05ee-4ab6-8361-3a2a3dee00e3

        # Output
        uuid:   c9ed7097-05ee-4ab6-8361-3a2a3dee00e3
        name:   Slot 1
        status: reserved

1. Finally the booking request must be marked as `completed`. On the **Booking Service** execute the following command.

    ```
    poetry run python -m app.cli complete_booking daab05c7-5d8f-4480-9a95-8d042e2948db

    # Output
    daab05c7-5d8f-4480-9a95-8d042e2948db
    ```

    As usual it will return the the domain uuid.

1. Now get the `Booking` instance current state.

    ```
    poetry run python -m app.cli get_booking_details daab05c7-5d8f-4480-9a95-8d042e2948db

    # Output

    id:                  3
    domain_uuid:         daab05c7-5d8f-4480-9a95-8d042e2948db
    status:              completed
    parking_slot_ref_no: c9ed7097-05ee-4ab6-8361-3a2a3dee00e3
    ```

1. Get the `Booking` instance events.

    ```
    {
        'id': UUID('daab05c7-5d8f-4480-9a95-8d042e2948db'),
        'version': 1,
        'parking_slot_ref_no': 'c9ed7097-05ee-4ab6-8361-3a2a3dee00e3',
        'status': 'created'
    }
    {
        'id': UUID('daab05c7-5d8f-4480-9a95-8d042e2948db'),
        'version': 2,
        'status': 'reserved'
    }
    {
        'id': UUID('daab05c7-5d8f-4480-9a95-8d042e2948db'),
        'version': 3,
        'status': 'completed'
    }
    ```

    If you noticed the last two records do not have the `parking_slot_ref_no` property. This is because the stored event is only recording properties that has been newly created or has been modified.

1. Get the `ParkingSlot` instance current state.

    ```
    poetry run python -m app.cli parking_slot_details c9ed7097-05ee-4ab6-8361-3a2a3dee00e3

    # Output
    uuid:   c9ed7097-05ee-4ab6-8361-3a2a3dee00e3
    name:   Slot 1
    status: reserved
    ```

## Benefits and drawbacks of Event Sourcing Pattern

WIP

