import atexit

from flask import Flask, current_app, request, jsonify
from werkzeug.exceptions import BadRequest

from flights.bootstrap import Container
from flights.service_layer import commands
from flights.domain import errors


def create_app():
    flask_app = Flask(__name__)
    container = Container()

    flask_app.extensions['service'] = container.service

    register_error_handlers(flask_app)

    atexit.register(container.close)

    return flask_app


def service():
    return current_app.extensions["service"]


def required_fields(data, *fields):
    if data is None:
        raise BadRequest('request body must contain data')

    for field in fields:
        if field not in data:
            raise BadRequest('missing required field: {}'.format(field))


app = create_app()


@app.route('/create_flight', methods=['POST'])
def create_flight():
    data = request.get_json()

    required_fields(data, 'flight_id', 'seats')

    cmd = commands.CreateFlight(
        data['flight_id'],
        data['seats'],
    )

    service().create_flight(cmd)

    return jsonify({"msg": "ok"}), 201


@app.route('/reserve_seat', methods=['POST'])
def reserve_seat():
    data = request.get_json()

    required_fields(data, 'flight_id', 'passenger_id', 'seat_id')

    cmd = commands.ReserveSeat(
        data['flight_id'],
        data['passenger_id'],
        data['seat_id'],
    )

    service().reserve_seat(cmd)

    return "", 204


@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    data = request.get_json()

    required_fields(data, 'flight_number', 'passenger_id')

    cmd = commands.CancelReservation(
        data['flight_id'],
        data['passenger_id'],
    )

    service().cancel_reservation(cmd)

    return "", 204


ERROR_CODES = {
    errors.FlightNotFound: 404,
    errors.SeatDoesNotExist: 404,

    errors.FlightAlreadyExists: 409,
    errors.SeatAlreadyReserved: 409,
    errors.PassengerAlreadyRegistered: 409,
    errors.FlightClosed: 409,
    errors.FlightDeparted: 409,
    errors.NotReservationOwner: 409,
    errors.ConcurrencyError: 409,
}


def register_error_handlers(flask_app):
    @flask_app.errorhandler(errors.DomainError)
    def handle_domain_error(error):
        return jsonify({'msg': str(error)}), ERROR_CODES.get(type(error), 400)

    @flask_app.errorhandler(errors.InfrastructureError)
    def handle_infrastructure_error(error):
        return jsonify({'msg': "try back later"}), 500

    @flask_app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({'msg': error.description}), 400
