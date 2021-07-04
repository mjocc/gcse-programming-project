from __future__ import annotations

from typing import Optional, Union

from flask import Response, abort, jsonify, render_template, request

from profit_calculator import app
from profit_calculator import flight_plan as fp
from profit_calculator.__main__ import Aircraft, Airport


@app.context_processor
def insert_variables() -> dict:
    return dict(complete=fp.complete())


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/airport", methods=["GET", "POST"])
def airport_details() -> str:
    if request.method == "POST":
        fp.airport_details(request.form["uk-airport"], request.form["o-airport"])
        submitted = True
    else:
        submitted = False
    return render_template(
        "airport.html", airports=Airport.all.values(), submitted=submitted
    )


@app.route("/flight", methods=["GET", "POST"])
def flight_details() -> str:
    if request.method == "POST":
        fp.flight_details(
            Aircraft.all[int(request.form["aircraft-type"])],
            request.form["first-class-seats"],
        )
        submitted = True
    else:
        submitted = False
    return render_template(
        "flight.html",
        aircrafts=Aircraft.all,
        aircraft_data=[
            [aircraft.max_standard_class, aircraft.min_first_class]
            for aircraft in Aircraft.all
        ],
        submitted=submitted,
    )


@app.route("/price", methods=["GET", "POST"])
def price_plan() -> str:
    if request.method == "POST":
        fp.price_plan(
            request.form["standard-class-price"], request.form["first-class-price"]
        )
        submitted = True
    else:
        submitted = False
    airport_details_exist: bool = fp.airport_details_exist()
    aircraft_details_exist: bool = fp.flight_details_exist()
    in_range: Optional[bool] = fp.flight_in_range()
    if (
        not airport_details_exist
        or not aircraft_details_exist
        or not in_range
        or in_range is None
    ):
        disable_form: bool = True
    else:
        disable_form = False
    return render_template(
        "price.html",
        airport_data=airport_details_exist,
        aircraft_data=aircraft_details_exist,
        in_range=in_range,
        disable=disable_form,
        submitted=submitted,
    )


@app.route("/profit")
def profit_information() -> str:
    if fp.complete():
        fp_dict: dict = vars(fp).copy()
        for key, value in fp_dict.items():
            if isinstance(value, float) and key not in ["distance"]:
                fp_dict[key] = "£{:,.2f}".format(value)
        fp_dict["distance"] = f"{fp_dict['distance']} km"
        if fp_dict["uk_airport"] == "LPL":
            fp_dict["uk_airport"] = "Liverpool John Lennon"
        elif fp_dict["uk_airport"] == "BOH":
            fp_dict["uk_airport"] = "Bournemouth International Airport"
        return render_template(
            "profit.html", flight_plan=fp_dict, profit=fp.profit_made
        )
    else:
        abort(409)


@app.route("/clear", methods=["GET", "DELETE"])
def clear_data() -> Union[str, Response]:
    if request.method == "DELETE":
        fp.__init__()
        return jsonify(success=True)
    elif request.method == "GET":
        return render_template("clear.html")
