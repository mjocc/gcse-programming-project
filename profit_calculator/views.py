from __future__ import annotations

from flask import render_template, request

from profit_calculator import app
from profit_calculator import flight_plan as fp
from profit_calculator.__main__ import Aircraft, Airport


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/airport", methods=["GET", "POST"])
def airport_details() -> str:
    submitted = False
    if request.method == "POST":
        fp.airport_details(request.form["uk-airport"], request.form["o-airport"])
        submitted = True
    return render_template(
        "airport.html", airports=Airport.all.values(), submitted=submitted
    )


@app.route("/flight", methods=["GET", "POST"])
def flight_details() -> str:
    submitted = False
    if request.method == "POST":
        fp.flight_details(
            Aircraft.all[int(request.form["aircraft-type"])],
            request.form["first-class-seats"],
        )
        submitted = True
    return render_template(
        "flight.html",
        aircrafts=Aircraft.all,
        aircraft_data=[
            [aircraft.max_standard_class, aircraft.min_first_class]
            for aircraft in Aircraft.all
        ],
        submitted=submitted,
    )


@app.route("/profit")
def calculate_profit() -> str:
    return render_template("profit.html")


@app.route("/clear")
def clear_data() -> str:
    return render_template("clear.html")
