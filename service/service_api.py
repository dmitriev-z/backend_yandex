import flask
from flask import wrappers

from service import service_framework

app = flask.Flask(__name__)
service = service_framework.Service()


@app.route('/imports', methods=['POST'])
def import_citizens() -> wrappers.Response:
    request_json = flask.request.json
    new_import_id = service.import_citizens(request_json)
    if new_import_id:
        resp_json = {'data': {'import_id': new_import_id}}
        return flask.make_response(flask.jsonify(resp_json), 201)
    return flask.make_response('Bad Request', 400)


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def patch_import_citizen(import_id: int, citizen_id: int) -> wrappers.Response:
    request_json = flask.request.json
    patched_citizen = service.patch_import_citizen(import_id, citizen_id, request_json)
    if patched_citizen:
        resp_json = {'data': patched_citizen}
        return flask.make_response(flask.jsonify(resp_json), 200)
    return flask.make_response('Bad Request', 400)


@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_import_citizens(import_id: int) -> wrappers.Response:
    citizens = service.get_import_citizens(import_id)
    if citizens:
        resp_json = {'data': citizens}
        return flask.make_response(flask.jsonify(resp_json), 200)
    return flask.make_response('Bad Request', 400)


@app.route('/imports/<int:import_id>/citizens/birthdays', methods=['GET'])
def get_import_citizens_birthdays(import_id: int) -> wrappers.Response:
    import_citizens_birthdays = service.get_import_citizens_birthdays(import_id)
    if import_citizens_birthdays:
        resp_json = {'data': import_citizens_birthdays}
        return flask.make_response(flask.jsonify(resp_json), 200)
    return flask.make_response('Bad Request', 400)


@app.route('/imports/<int:import_id>/towns/stat/percentile/age', methods=['GET'])
def get_towns_percentile_age_stats(import_id: int) -> wrappers.Response:
    towns_percentile_age_stats = service.get_towns_percentile_age_stats(import_id)
    if towns_percentile_age_stats:
        resp_json = {'data': towns_percentile_age_stats}
        return flask.make_response(flask.jsonify(resp_json), 200)
    return flask.make_response('Bad Request', 400)
