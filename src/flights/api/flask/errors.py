import logging

from flask import jsonify
from werkzeug.exceptions import BadRequest

from flights.domain import errors

logger = logging.getLogger(__name__)

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
        logger.exception("infrastructure error: %s", error)

        return jsonify({'msg': "try back later"}), 500

    @flask_app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({'msg': error.description}), 400

    @flask_app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("unhandled exception: %s", error)

        return jsonify({"msg": "try back later"}), 500
