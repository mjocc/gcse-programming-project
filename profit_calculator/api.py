from flask import Response, abort, jsonify, render_template, send_file

from profit_calculator import app
from profit_calculator import flight_plan as fp
from profit_calculator.__main__ import Aircraft, Airport


@app.route("/api")
def get_api_docs() -> str:
    return render_template("api-docs.html")


@app.route("/logo.png")
def get_logo() -> Response:
    return send_file("static/api-docs/logo.png")


@app.route("/api/config")
def get_api_config() -> Response:
    return send_file("../api-docs/insomnia-config.json")


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
    fp.airport_details("LPL", "ORY")
    fp.flight_details(Aircraft.all[2], 50)
    fp.price_plan(50.00, 100.00)
    return jsonify(success=True)


@app.route("/api/clear", methods=["DELETE"])
def clear_data() -> Response:
    fp.__init__()  # type: ignore[misc]
    return jsonify(success=True)
