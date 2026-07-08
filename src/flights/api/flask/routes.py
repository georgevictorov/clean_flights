from flask import jsonify, request

from flights.api.flask.validation import required_fields
from flights.service_layer import commands


def register_routes(app, service):
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({"msg": "hey"}), 200

    @app.route('/create_flight', methods=['POST'])
    def create_flight():
        data = request.get_json()

        required_fields(data, 'flight_id', 'seats')

        cmd = commands.CreateFlight(
            data['flight_id'],
            data['seats'],
        )

        service.create_flight(cmd)

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

        service.reserve_seat(cmd)

        return "", 204

    @app.route('/cancel_reservation', methods=['POST'])
    def cancel_reservation():
        data = request.get_json()

        required_fields(data, 'flight_id', 'passenger_id')

        cmd = commands.CancelReservation(
            data['flight_id'],
            data['passenger_id'],
        )

        service.cancel_reservation(cmd)

        return "", 204
