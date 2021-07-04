from __future__ import annotations

from flask import Response, abort, jsonify, send_file

from profit_calculator import app, flight_plan
from profit_calculator.__main__ import Aircraft, Airport


@app.route("/api/airport/<airport_code>")
def get_airport_data(airport_code) -> Response:
    try:
        return jsonify(vars(Airport.all[airport_code.upper()]))
    except KeyError:
        abort(404)
    except:
        abort(500)


@app.route("/api/aircraft/<int:aircraft_id>")
def get_aircraft_data(aircraft_id) -> Response:
    try:
        return jsonify(vars(Aircraft.all[aircraft_id]))
    except KeyError:
        abort(404)
    except:
        abort(500)


@app.route("/api/flight-plan")
def get_flight_plan() -> Response:
    try:
        return jsonify(vars(flight_plan))
    except:
        abort(500)


@app.route("/api")
def get_api_config() -> Response:
    # try:
    return send_file("../insomnia-config.yaml")
    # except:
    #    abort(500)


@app.route("/api/test-data", methods=["PUT"])
def insert_test_data() -> Response:
    try:
        flight_plan.airport_details("LPL", "ORY")
        flight_plan.flight_details(Aircraft.all[2], 50)
        flight_plan.price_plan(50.00, 100.00)
        return jsonify(success=True)
    except:
        return jsonify(success=False)
