# Saga Choreography Example

There are 3 microservices that will work together to demonstrate this pattern. We will try to imitate a simple booking logic that will handle booking requests, billings and parking slots.

## Techstack to implement servers

- FastAPI
- RabbitMQ
- Postgres
- Docker

## Running the applications

You must be in the root directory of this repository (python-microservices-patterns) where the `docker-compose-saga-choreography.yml` file is located at and not in the saga-choreogprahy-example directory.

- Build saga choreograhpy docker images:

    ```
    docker-compose -f docker-compose-saga-choreography.yml build --no-cache
    ```
- Run the services via docker-compose:

    ```
    docker-compose -f docker-compose-saga-choreography.yml up
    ```

- Booking service is running at localhost:8000
- Billing service is running at localhost:8001
- Parking service is running at localhost:8002
- To check the server health just append `/health` url at the end of the `localhost:port` (e.g. `localhost:8000/health`)

## Saga's Choreography Publish/Subscribe Event

![saga-choreography-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-choreograhpy-example/resources/saga-choreography-pattern.png)

### Workflow

1. _**Booking Service**_ creates a new booking request, set the state to _pending_, publish an event called **CREATE_BOOKING_EVENT**.

1. _**Billing Service**_ listens to **CREATE_BOOKING_EVENT** creates a billing request and charge the customer. When Payment has been made, trigger **BILL_PAID_EVENT**.

1. _**Parking Service**_ listens to **BILL_PAID_EVENT**  then modify parking space status to _reserved_ and fires **RESERVED_BOOKING_EVENT**.

1. _**Booking Service**_ listens to **RESERVED_BOOKING_EVENT** and set the current booking request to _done_.

In order to demonstrate the publish and subscribe pattern, we will have to prepare and operate data by creating parking slot, booking the slot and reserving the slot after the customer paid the billing total.

> **Note**: You may need to ssh to the given service container via `docker exec -it <service_container_id> bash` for the CLI to work.

#### Parking Service

Before we book, we will need to create atleast 1 available parking slot.

1. Create an available parking slot.

    ```
    poetry run python -m app.cli create_parking --name='Slot 1'

    # Output:
    uuid:   9f2570bd-021b-4b51-881e-bb04fdce4fda
    name:   Slot 1
    status: available
    ```

1. You can also list all parking slots by:

    ```
    poetry run python -m app.cli parking_slot_list

    # Output
    ...
    {"uuid": "9f2570bd-021b-4b51-881e-bb04fdce4fda", "name": "Slot 1", "status": "available"}
    ```

1. Or get a parking slot details by
    ```
    poetry run python -m app.cli parking_slot_details --uuid='9f2570bd-021b-4b51-881e-bb04fdce4fda'

    # Output
    uuid:   9f2570bd-021b-4b51-881e-bb04fdce4fda
    name:   Slot 1
    status: available
    ```

#### Booking Service

Right after we created an available parking slot, customer will need to request a booking for that specific slot.

1. To request a booking, you may need to:

    ```
    poetry run python -m app.cli create_booking --parking_slot_uuid='9f2570bd-021b-4b51-881e-bb04fdce4fda'

    # Output
    id:                1
    status:            pending
    parking_slot_ref_no: 9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17
    ```

    > **Note**: Notice the additional uuid on the `parking_slot_ref_no` output `<parking_slot_uuid>:<booking_identifier_uuid>`.
    > This will serve as a unique identifier for the booking record to identify transaction.
    > Since customers may happen to book the same parking slot we will use this case
    > to trigger rollback transaction later on.
    >
    > This operation will publish the **CREATE_BOOKING_EVENT**.

1. To list all bookings:

    ```
    poetry run python -m app.cli booking_list

    # Output
    ...
    {"id": 1, "status": "pending", "parking_slot_ref_no": "9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17"}
    ```

1. Or get booking details by:

    ```
    poetry run python -m app.cli booking_details_by_parking_ref_no --uuid='9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17'

    # Output
    id:                1
    status:            pending
    booking_details_by_parking_ref_no: 9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17
    ```

#### Billing Service

A billing request for the customer is created right after booking a parking slot. Customer may pay the bill later on by using this service.

1. Billing service listens to **CREATE_BOOKING_EVENT** which in turn create a new billing request. To get the billing request details you need to:

    ```
    poetry run python -m app.cli billing_request_details_by_reference_no --ref_no='9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17'

    # Output
    billing_request: {
        'id': 1,
        'total': Decimal('100.00'),
        'status': 'pending',
        'reference_no': '9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17'
    }
    reconciliations: []
    ```

    This will show `billing_request` object and the payment `reconciliations` object that should be made by the customer later on.

    > **Note**: `ref_no` should be equal to the `Booking.parking_slot_ref_no`.

1. You can also list all the billing requests using:

    ```
    poetry run python -m app.cli billing_request_list

    # Output
    ...
    {'id': 1, 'total': Decimal('100.00'), 'status': 'pending', 'reference_no': '9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17'}
    ```

1. Customers will then need to pay the bills issued to them. To do that we should do this:

    ```
    poetry run python -m app.cli pay_bill --ref_no='9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17' --amount=100

    # Output
    id:                 1
    amount:             100.00
    billing_request_id: 1
    ```

    > **Note**: All biling-requests total are default to 100.00. Following this action will trigger the **BILL_PAID_EVENT**.

1. Now let us check the billing-request details once again:

    ```
    poetry run python -m app.cli billing_request_details_by_reference_no --ref_no='9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17'

    # Output
    billing_request: {
        'id': 1,
        'total': Decimal('100.00'),
        'status': 'paid',
        'reference_no': '9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17'
    }
    reconciliations: [
        {
            'id': 1,
            'amount': Decimal('100.00'),
            'billing_request_id': 1
        }
    ]
    ```

    Now the payment reconciliation made by the customer is shown and the billing request status is set to `paid`.

#### Parking and Booking Services

1. After payment has been made. Parking Service listen to **BILL_PAID_EVENT** and if payment is successful it will set the parking slot status to `reserved`. To confirm that we can get the parking slot details again using:

    ```
    poetry run python -m app.cli parking_slot_details --uuid='9f2570bd-021b-4b51-881e-bb04fdce4fda'

    # Output
    uuid:   9f2570bd-021b-4b51-881e-bb04fdce4fda
    name:   Slot 1
    status: reserved
    ```

    Parking **Slot 1** has been reserved.

    > **Note**: After the parking slot is set to `reserved`, it will fire the **RESERVED_BOOKING_EVENT**.

1. Also Booking Service listens to **RESERVED_BOOKING_EVENT**, once it receive an event it will set the booking request status to `done`.

    ```
    poetry run python -m app.cli booking_details_by_parking_ref_no --uuid='9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17'

    # Output
    id:                1
    status:            done
    parking_slot_uuid: 9f2570bd-021b-4b51-881e-bb04fdce4fda:3698f6d0-bfad-41d5-b675-e58684cbde17
    ```

## Compensating (Rollback) Transaction in Choreograhpy pattern

![saga-choreography-rollback-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-choreograhpy-example/resources/saga-choreography-pattern-rb-transaction.png)

### Workflow

1. _**Parking Service**_ publishes **PARKING_UNAVAILABLE_EVENT**, and _**Booking Service**_ listens to it and updates booking request status to _failed_.

1. _**Billing Service**_ listens to **PARKING_UNAVAILABLE_EVENT** refund payment to customer and updates billing status to _refunded_.

> **Note**: Participating microservices should recognize transactions by using unique identifiers from a certain event to know what transaction is being processed.

To produce this workflow we will have to request a new booking request for an already _reserved_ parking slot. In this case it's the parking slot record with `9f2570bd-021b-4b51-881e-bb04fdce4fda` uuid.

> **Note**: You may need to ssh to the given service container via `docker exec -it <service_container_id> bash` for the CLI to work.

#### Booking Service

1. Create a booking for an already reserved parking slot.

    ```
    poetry run python -m app.cli create_booking --parking_slot_uuid='9f2570bd-021b-4b51-881e-bb04fdce4fda'

    # Output
    id:                2
    status:            pending
    parking_slot_uuid: 9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552
    ```

    This will trigger the **CREATED_BOOKING_EVENT** and will create a new billing request for this booking.

#### Billing Service

1. Check the newly created billing request by getting the billing details

    ```
    poetry run python -m app.cli billing_request_details_by_reference_no --ref_no='9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552'

    # Output
    billing_request: {
        'id': 2,
        'total': Decimal('100.00'),
        'status': 'pending',
        'reference_no': '9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552'
    }
    reconciliations: []
    ```

1. Attempt to pay the billing-request that is associated to the already _reserved_ parking slot booking request.

    ```
    poetry run python -m app.cli pay_bill --ref_no='9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552' --amount=100

    # Output
    id:                 2
    amount:             100.00
    billing_request_id: 2
    ```

    This action will fire **BILL_PAID_EVENT** where _**Parking Service**_ listens to. The parking service will try to evaluate the status of the parking slot. In our case this is already _reserved_ and will fire a new event called **PARKING_UNAVAILABLE_EVENT**.

#### Booking Service

This service listens to the **PARKING_UNAVAILABLE_EVENT**. If a message was received, it will set the booking record status to _failed_.

1. Check the status of the given booking transaction:

    ```
    poetry run python -m app.cli booking_details_by_parking_ref_no --uuid='9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552'

    # Output
    id:                  2
    status:              failed
    parking_slot_ref_no: 9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552
    ```

#### Billing Service

This service listens to the **PARKING_UNAVAILABLE_EVENT**. If a message was received, it will set the billing status to _refunded_. Customer may need to be refunded for all failed parking reservations.

1. Check the status of the billing record:

    ```
    poetry run python -m app.cli billing_request_details_by_reference_no --ref_no='9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552'

    # Output
    billing_request: {
        'id': 2,
        'total': Decimal('100.00'),
        'status': 'refunded',
        'reference_no': '9f2570bd-021b-4b51-881e-bb04fdce4fda:946eed09-eb61-4d88-a49a-ebc520d54552'
    }
    reconciliations: [
        {'id': 2, 'amount': Decimal('100.00'), 'billing_request_id': 2}
    ]
    ```

If you follow the above workflow and instructions correctly, you should notice the interservice communications between participating microservices via publish/subscribe event by using Saga Choreography pattern.

## Benefits and drawbacks of Saga's Choreograhpy Pattern

- No additional complexity for coordination logic.
- Very simple and easy to implement with smaller workflows.
- Hard to maintain when it grows.
- Cyclic dependency between partipating services.
