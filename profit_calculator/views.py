from typing import Optional, Union

from flask import Response, abort, flash, render_template, request, url_for

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
        success, msg = fp.airport_details(
            request.form["uk-airport"], request.form["o-airport"]
        )
        flash(msg, "message" if success else "error")
    return render_template("airport.html", airports=Airport.all.values())


@app.route("/flight", methods=["GET", "POST"])
def flight_details() -> str:
    if request.method == "POST":
        success, msg = fp.flight_details(
            request.form["aircraft-type"],
            request.form["first-class-seats"],
        )
        flash(msg, "message" if success else "error")
    return render_template(
        "flight.html",
        aircrafts=Aircraft.all,
        aircraft_data=[
            [aircraft.max_standard_class, aircraft.min_first_class]
            for aircraft in Aircraft.all
        ],
    )


@app.route("/price", methods=["GET", "POST"])
def price_plan() -> str:
    if request.method == "POST":
        success, msg = fp.price_plan(
            request.form["standard-class-price"], request.form["first-class-price"]
        )
        flash(msg, "message" if success else "error")
    airport_details_exist: bool = fp.airport_details_exist()
    aircraft_details_exist: bool = fp.aircraft_details_exist()
    in_range: Optional[bool] = fp.flight_in_range()
    if not airport_details_exist:
        flash(
            "No airport data has been submitted. This is needed to calculate the "
            f"profit. Press <a href='{url_for('airport_details')}'>here</a> to "
            "enter it.",
            "top-error",
        )
    if not aircraft_details_exist:
        flash(
            "No aircraft data has been submitted. This is needed to calculate the "
            f"profit. Press <a href='{url_for('flight_details')}'>here</a> to "
            "enter it.",
            "top-error",
        )
    if aircraft_details_exist and airport_details_exist and not in_range:
        flash(
            "This route is longer than the range of the aircraft selected. Please "
            f"change the aircraft <a href='{url_for('flight_details')}'>here</a> "
            f"or change the route <a href='{url_for('airport_details')}'>here</a>.",
            "top-error",
        )
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
        disable=disable_form,
    )


@app.route("/profit")
def profit_information() -> Optional[str]:
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
            "profit.html", flight_plan=fp_dict, profit=fp.profit_made()
        )
    else:
        abort(418)
        return None


@app.route("/exports", methods=["GET", "POST"])
def export_form() -> Union[str, Response]:
    if request.method == "POST":
        if request.form["import/export"] == "import":
            success: bool
            msg: Optional[str]
            success, msg = fp.import_from_file(request)
            if msg:
                flash(msg, "error" if success is False else "message")
        elif request.form["import/export"] == "export":
            return fp.export_as_file()
    return render_template("exports.html")


@app.route("/clear")
def clear_data_confirmation() -> str:
    return render_template("clear.html")
