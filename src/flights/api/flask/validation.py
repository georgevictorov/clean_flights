from werkzeug.exceptions import BadRequest


def required_fields(data, *fields):
    if data is None:
        raise BadRequest('request body must contain data')

    for field in fields:
        if field not in data:
            raise BadRequest('missing required field: {}'.format(field))
