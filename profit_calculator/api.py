from typing import Optional

from flask import Response, abort, jsonify, render_template, request, send_file

from profit_calculator import app
from profit_calculator import flight_plan as fp
from profit_calculator.__main__ import Aircraft, Airport


@app.route("/api")
def get_api_docs() -> str:
    return render_template("api-docs.html")


@app.route("/logo.png")  # Needed for Insomnia Documenter to work
def get_logo() -> Response:
    return send_file("static/api-docs/logo.png")


@app.route("/api/config")
def get_api_config() -> Response:
    return send_file("static/api-docs/insomnia.json")


@app.route("/api/airport/<airport_code>")
def get_airport_data(airport_code) -> Response:
    try:
        return jsonify(vars(Airport.all[airport_code.upper()]))
    except KeyError:
        abort(404)


@app.route("/api/aircraft/<int:aircraft_id>")
def get_aircraft_data(aircraft_id) -> Response:
    try:
        return jsonify(vars(Aircraft.all[aircraft_id]))
    except KeyError:
        abort(404)


@app.route("/api/flight-plan")
def get_flight_plan() -> Response:
    return jsonify(vars(fp))


@app.route("/api/test-data", methods=["PUT"])
def insert_test_data() -> Response:
    fp.insert_test_data()
    return jsonify(success=True)


@app.route("/api/import-data", methods=["POST"])
def import_file_data() -> Response:
    success: bool
    err_msg: str
    success, err_msg = fp.import_from_file(request)
    response_dict = dict(success=success)
    if success is False:
        response_dict["message"] = err_msg
    return jsonify(response_dict)


@app.route("/api/export-data")
def export_file_data() -> Response:
    file = fp.export_as_file()
    return file


@app.route("/api/clear", methods=["DELETE"])
def clear_data() -> Response:
    fp.__init__()  # type: ignore[misc]
    return jsonify(success=True)
