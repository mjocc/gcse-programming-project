from __future__ import annotations

from flask import Response, abort, jsonify

from profit_calculator import app
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
