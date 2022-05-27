# Saga Choreography Example

There are 3 microservices that will work together to demonstrate this pattern. We will try to imitate a simple booking logic that will handle booking requests, billings and parking slots.

## Techstack to implement servers

- FastAPI
- RabbitMQ
- Postgres

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
    uuid:   76cd294f-7b4c-4e72-b204-44fb542104b4
    name:   Slot 1
    status: available
    ```

1. You can also list all parking slots by:

    ```
    poetry run python -m app.cli parking_slot_list

    # Output
    ...
    {"uuid": "76cd294f-7b4c-4e72-b204-44fb542104b4", "name": "Slot 1", "status": "available"}
    ```

1. Or get a parking slot details by
    ```
    poetry run python -m app.cli parking_slot_details --uuid='76cd294f-7b4c-4e72-b204-44fb542104b4'

    # Output
    uuid:   76cd294f-7b4c-4e72-b204-44fb542104b4
    name:   Slot 1
    status: available
    ```

#### Booking service

Right after we created an available parking slot, customer will need to request a booking for that specific slot.

1. To request a booking, you may need to:

    ```
    poetry run python -m app.cli create_booking --parking_slot_uuid='76cd294f-7b4c-4e72-b204-44fb542104b4'

    # Output
    id:                43
    status:            pending
    parking_slot_uuid: 76cd294f-7b4c-4e72-b204-44fb542104b4
    ```

    > **Note**: This operation will publish the _**CREATE_BOOKING_EVENT**_.

1. To list all bookings:

    ```
    poetry run python -m app.cli booking_list

    # Output
    ...
    {"id": 43, "status": "pending", "parking_slot_uuid": "76cd294f-7b4c-4e72-b204-44fb542104b4"}
    ```

1. Or get booking details by:

    ```
    poetry run python -m app.cli booking_details_by_parking_slot_uuid --uuid='76cd294f-7b4c-4e72-b204-44fb542104b4'

    # Output
    id:                43
    status:            pending
    parking_slot_uuid: 76cd294f-7b4c-4e72-b204-44fb542104b4
    ```

#### Billing Service

A billing request for the customer is created right after booking a parking slot. Customer may pay the bill later on by using this service.

1. Billing service listens to _**CREATE_BOOKING_EVENT**_ which in turn create a new billing request. To get the billing request details you need to:

    ```
    poetry run python -m app.cli billing_request_details_by_reference_no --ref_no='76cd294f-7b4c-4e72-b204-44fb542104b4'

    # Output
    billing_request: {
        'id': 41,
        'total': Decimal('100.00'),
        'status': 'pending',
        'reference_no': '76cd294f-7b4c-4e72-b204-44fb542104b4'
    }
    reconciliations: []
    ```

    This will show `billing_request` object and the payment `reconciliations` object that should be made by the customer.

    > **Note**: `ref_no` should be equal to the `parking_slot_uuid`.

1. You can also list all the billing requests using:

    ```
    poetry run python -m app.cli billing_request_list

    # Output
    ...
    {'id': 41, 'total': Decimal('100.00'), 'status': 'pending', 'reference_no': '76cd294f-7b4c-4e72-b204-44fb542104b4'}
    ```

1. Customers will then need to pay the bills issued to them. To do that we should use this:

    ```
    poetry run python -m app.cli pay_bill --ref_no='76cd294f-7b4c-4e72-b204-44fb542104b4' --amount=100

    # Output
    id:                 46
    amount:             100.00
    billing_request_id: 41
    ```

    > **Note**: All biling-request total is default to 100.00. Following this action will trigger the _**BILL_PAID_EVENT**_.

1. Now let us check the billing-request details once again:

    ```
    poetry run python -m app.cli billing_request_details_by_reference_no --ref_no='76cd294f-7b4c-4e72-b204-44fb542104b4'

    # Output
    billing_request: {
        'id': 41,
        'total': Decimal('100.00'),
        'status': 'paid',
        'reference_no': '76cd294f-7b4c-4e72-b204-44fb542104b4'
    }
    reconciliations: [
        {
            'id': 46,
            'amount': Decimal('100.00'),
            'billing_request_id': 41
        }
    ]
    ```

    Now the payment reconciliation made by the customer is shown and the billing request status is set to `paid`.

#### Parking and Booking Services

1. After payment has been made. Parking Service listen to _**BILL_PAID_EVENT**_ and if payment is successful it will set the parking slot status to `reserved`. To confirm that we can get the parking slot details again using:

    ```
    poetry run python -m app.cli parking_slot_details --uuid='76cd294f-7b4c-4e72-b204-44fb542104b4'

    # Output
    uuid:   76cd294f-7b4c-4e72-b204-44fb542104b4
    name:   Slot 1
    status: reserved
    ```

    Parking **Slot 1** has been reserved.

    > **Note**: After the parking slot is set to `reserved`, it will fire the _**RESERVED_BOOKING_EVENT**_.

1. Also Booking Service listens to _**RESERVED_BOOKING_EVENT**_, once it receive an event it will set the booking request status to `done`.

    ```
    poetry run python -m app.cli booking_details_by_parking_slot_uuid --uuid='76cd294f-7b4c-4e72-b204-44fb542104b4'

    # Output
    id:                43
    status:            done
    parking_slot_uuid: 76cd294f-7b4c-4e72-b204-44fb542104b4
    ```

If you follow the above workflow and instructure correctly, you should notice the interservice communication between participating microservices.

## Compensating (Rollback) Transaction in Choreograhpy pattern

![saga-choreography-rollback-pattern](https://github.com/roelzkie15/python-microservices-patterns/blob/master/saga-choreograhpy-example/resources/saga-choreography-pattern-rb-transaction.png)

1. _**Parking Service**_ publishes **PARKING_UNAVAILABLE_EVENT**, and _**Booking Service**_ listens to it and updates booking request status to _failed_.

1. _**Billing Service**_ listens to **PARKING_UNAVAILABLE_EVENT** refund payment to customer and updates billing status to _refunded_.

> **Note:** Participating microservices should recognize transactions by using unique identifiers from a certain event to know what transaction is being processed.
