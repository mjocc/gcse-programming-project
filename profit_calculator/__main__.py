import csv
import io
import pickle
import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flask import Request, Response, send_file
from flask.json import JSONEncoder
from itsdangerous import BadSignature

from profit_calculator import ALLOWED_EXTENSIONS, fp_signer


class Airport:
    all: Dict[str, Any] = {}

    def __init__(self, code, name, distance_from_lpl, distance_from_boh) -> None:
        self.code: str = code
        self.name: str = name
        self.distance_from_lpl: float = float(distance_from_lpl)
        self.distance_from_boh: float = float(distance_from_boh)

    def __repr__(self) -> str:
        return f"Airport: {self.name} ({self.code})"

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def import_data() -> None:
        with open("Airports.txt", "r") as file:
            reader: List[List[str]] = list(csv.reader(file))
        for row in reader:
            Airport.all[row[0]] = Airport(*row)


# noinspection PyShadowingBuiltins
class Aircraft:
    all: List[Any] = []

    def __init__(
        self, type, running_cost, range, max_standard_class, min_first_class, id=None
    ) -> None:
        self.type: str = type
        self.running_cost: float = float(
            running_cost
        )  # running cost per seat per 100km
        self.range: float = float(range)
        self.max_standard_class: int = int(max_standard_class)
        self.min_first_class: int = int(min_first_class)
        self.id = id

    def __repr__(self) -> str:
        return f"Aircraft: {self.type} ({self.id})"

    def __str__(self) -> str:
        return self.type

    @staticmethod
    def import_data() -> None:
        with open("Aircraft.txt", "r") as file:
            reader: List[List[str]] = list(csv.reader(file))
        for index, row in enumerate(reader):
            Aircraft.all.append(Aircraft(*row, id=index))


class FlightPlan:
    def __init__(
        self,
        uk_airport=None,
        foreign_airport=None,
        distance=None,
        aircraft=None,
        no_first_class=None,
        no_standard_class=None,
        standard_class_price=None,
        first_class_price=None,
        cost_per_seat=None,
        running_cost=None,
        income=None,
        profit=None,
    ) -> None:
        self.uk_airport: Optional[str] = uk_airport
        self.foreign_airport: Optional[Airport] = foreign_airport
        self.distance: Optional[float] = distance

        self.aircraft: Optional[Aircraft] = aircraft
        self.no_first_class: Optional[int] = no_first_class
        self.no_standard_class: Optional[int] = no_standard_class

        self.standard_class_price: Optional[float] = standard_class_price
        self.first_class_price: Optional[float] = first_class_price
        self.cost_per_seat: Optional[float] = cost_per_seat
        self.running_cost: Optional[float] = running_cost
        self.income: Optional[float] = income
        self.profit: Optional[float] = profit

    def import_from_file(self, request_obj: Request) -> Tuple[bool, str]:
        if "flight-plan-file" not in request_obj.files:
            return False, "No flight plan file sent."
        received_file = request_obj.files["flight-plan-file"]
        if not allowed_file(received_file.filename):
            return False, "File does not have an allowed file extension."
        file_data: bytes = received_file.read()
        try:
            pickled_data = fp_signer.unsign(file_data)
            self.__init__(**vars(pickle.loads(pickled_data)))
        except BadSignature:
            return False, "File does not have the correct cryptographic signature."
        if self.foreign_airport is not None:
            self.foreign_airport = Airport.all[self.foreign_airport.code]
        if self.aircraft is not None:
            # noinspection PyUnresolvedReferences
            self.aircraft = Aircraft.all[self.aircraft.id]
        return True, "Data imported from file successfully."

    def export_as_file(self) -> Response:
        pickled_data = pickle.dumps(self)
        file_data = fp_signer.sign(pickled_data)
        file = io.BytesIO(file_data)
        # noinspection PyArgumentList
        return send_file(
            file,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="fp.flightplan",
            last_modified=datetime.now(),
        )

    def airport_details(
        self, uk_airport: str, foreign_airport: str
    ) -> Tuple[bool, str]:
        if uk_airport not in ["LPL", "BOH"]:
            return False, "Not a valid UK airport code."

        if foreign_airport in [airport.code for airport in Airport.all.values()]:
            foreign_airport = Airport.all[foreign_airport]
        else:
            return False, "Not a valid foreign airport code"

        self.uk_airport = uk_airport
        self.foreign_airport = foreign_airport
        if self.uk_airport == "LPL":
            self.distance = self.foreign_airport.distance_from_lpl
        elif self.uk_airport == "BOH":
            self.distance = self.foreign_airport.distance_from_boh

        return True, "Form submitted successfully."

    def airport_details_exist(self) -> bool:
        return self.uk_airport is not None and self.foreign_airport is not None

    def flight_details(self, aircraft_id: str, no_first_class: str) -> Tuple[bool, str]:
        try:
            aircraft_id = int(aircraft_id)
        except ValueError:
            return False, "Not a valid aircraft id."
        if aircraft_id in [craft.id for craft in Aircraft.all]:
            aircraft = Aircraft.all[aircraft_id]
        else:
            return False, "Not a valid aircraft id."

        try:
            no_first_class = int(no_first_class)
        except ValueError:
            return False, "Not a valid number of first class seats - not a number."
        if no_first_class > aircraft.max_standard_class / 2:
            return (
                False,
                f"Too many first class seats - there must be less than "
                f"{aircraft.max_standard_class / 2} first class seats for "
                f"this aircraft.",
            )
        elif no_first_class < aircraft.min_first_class:
            return (
                False,
                f"Too little first class seats - there must be more than "
                f"{aircraft.min_first_class} first class seats for this aircraft.",
            )

        self.aircraft = aircraft
        self.no_first_class = no_first_class
        self.no_standard_class = aircraft.max_standard_class - no_first_class * 2

        return True, "Form submitted successfully."

    def aircraft_details_exist(self) -> bool:
        return self.aircraft is not None and self.no_first_class is not None

    def flight_in_range(self) -> Optional[bool]:
        if self.airport_details_exist() and self.aircraft_details_exist():
            return self.aircraft.range > self.distance
        else:
            return None

    def price_plan(
        self, standard_class_price: str, first_class_price: str
    ) -> Tuple[bool, str]:
        in_range: Optional[bool] = self.flight_in_range()
        if (
            not self.airport_details_exist()
            or not self.aircraft_details_exist()
            or not in_range
            or in_range is None
        ):
            return (
                False,
                "All other information must be submitted first before completing "
                "this form.",
            )

        if standard_class_price[::-1].find(".") > 2:
            return False, "Not a valid standard class price - too many decimal places."
        try:
            standard_class_price = float(standard_class_price)
        except ValueError:
            return False, "Not a valid standard class price - not a number."
        if standard_class_price < 0:
            return False, "Not a valid standard class price - cannot be less than 0."

        if first_class_price[::-1].find(".") > 2:
            return False, "Not a valid first class price - too many decimal places."
        try:
            first_class_price = float(first_class_price)
        except ValueError:
            return False, "Not a valid first class price - not a number."
        if first_class_price < 0:
            return False, "Not a valid first class price - cannot be less than 0."

        self.standard_class_price = standard_class_price
        self.first_class_price = first_class_price
        self.cost_per_seat = self.aircraft.running_cost * (self.distance / 100)
        self.running_cost = self.cost_per_seat * (
            self.no_first_class + self.no_standard_class
        )
        self.income = (
            self.no_first_class * self.first_class_price
            + self.no_standard_class * self.standard_class_price
        )
        self.profit = self.income - self.running_cost
        return True, "Form submitted successfully."

    def complete(self) -> bool:
        return (
            self.airport_details_exist()
            and self.aircraft_details_exist()
            and self.flight_in_range()
            and self.standard_class_price is not None
            and self.first_class_price is not None
        )

    def profit_made(self) -> int:
        if self.complete():
            if self.profit > 0:
                return 1
            elif self.profit == 0:
                return 0
            else:
                return -1

    def insert_test_data(self) -> None:
        self.airport_details(
            random.choice(["LPL", "BOH"]),
            random.choice([airport.code for airport in Airport.all.values()]),
        )
        self.flight_details(
            str(random.randint(0, len(Aircraft.all))), str(random.randint(15, 45))
        )
        self.price_plan(
            str(round(random.uniform(25, 75), 2)),
            str(round(random.uniform(100, 200), 2)),
        )


class FlightPlanJSONEncoder(JSONEncoder):
    def default(self, obj) -> str:
        return obj.__dict__


def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
