from typing import Optional, Union

from flask import Response, flash, redirect, render_template, request, url_for

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
        flash(msg, "form-submit" if success else "error")
        if success:
            flash(
                {
                    "uk_airport": fp.uk_airport,
                    "foreign_airport_code": fp.foreign_airport.code,
                    "foreign_airport_name": fp.foreign_airport.name,
                    "distance_between_airports": fp.distance,
                },
                "page-data",
            )
    return render_template("airport.html", airports=Airport.all.values())


@app.route("/flight", methods=["GET", "POST"])
def flight_details() -> str:
    page_data: dict = {}
    if request.method == "POST":
        success, msg = fp.flight_details(
            request.form["aircraft-type"],
            request.form["first-class-seats"],
        )
        flash(msg, "form-submit" if success else "error")
        if success:
            flash(
                {
                    **vars(fp.aircraft),
                    "number_of_first_class": fp.no_first_class,
                    "number_of_standard_class": fp.no_standard_class,
                },
                "page-data",
            )
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
        flash(msg, "form-submit" if success else "error")
        if success:
            flash(
                {
                    "standard_class_price": fp.standard_class_price,
                    "first_class_price": fp.first_class_price,
                    "cost_per_seat": fp.cost_per_seat,
                    "running_cost": fp.running_cost,
                    "income": fp.income,
                    "profit": fp.profit,
                },
                "page-data",
            )
    airport_details_exist: bool = fp.airport_details_exist()
    aircraft_details_exist: bool = fp.aircraft_details_exist()
    in_range: Optional[bool] = fp.flight_in_range()
    if not airport_details_exist:
        flash(
            f"No airport data has been submitted. This is needed to calculate the "
            f"profit. Press <a href='{url_for('airport_details')}'>here</a> to "
            f"enter it.",
            "top-error",
        )
    if not aircraft_details_exist:
        flash(
            f"No aircraft data has been submitted. This is needed to calculate the "
            f"profit. Press <a href='{url_for('flight_details')}'>here</a> to "
            f"enter it.",
            "top-error",
        )
    if aircraft_details_exist and airport_details_exist and not in_range:
        flash(
            f"This route is longer than the range of the aircraft selected. Please "
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
        return redirect(url_for("index"))


@app.route("/exports", methods=["GET", "POST"])
def export_form() -> Union[str, Response]:
    if request.method == "POST":
        if request.form["import/export"] == "import":
            success: bool
            msg: str
            success, msg = fp.import_from_file(request)
            flash(msg, "message" if success else "error")
        elif request.form["import/export"] == "export":
            return fp.export_as_file()
    return render_template("exports.html")


@app.route("/clear")
def clear_data_confirmation() -> str:
    return render_template("clear.html")
