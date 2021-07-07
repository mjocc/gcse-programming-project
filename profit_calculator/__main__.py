import csv
import hmac
import io
import pickle
import random
from typing import Any, Dict, List, Optional

from flask.json import JSONEncoder

from profit_calculator import ALLOWED_EXTENSIONS, app


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

    def import_from_file(self, request_obj) -> bool:
        if "flight-plan-file" not in request_obj.files:
            return False
        received_file = request_obj.files["flight-plan-file"]
        received_digest, pickled_data = received_file.read().split(
            b"   "
        )  # separator is 3 spaces
        check_digest = hmac.digest(app.secret_key, pickled_data, "sha256")
        if hmac.compare_digest(received_digest, check_digest):
            self.__init__(**vars(pickle.loads(pickled_data)))
        else:
            return False
        if self.foreign_airport is not None:
            self.foreign_airport = Airport.all[self.foreign_airport.code]
        if self.aircraft is not None:
            # noinspection PyUnresolvedReferences
            self.aircraft = Aircraft.all[self.aircraft.id]
        return True

    def export_as_file(self):
        pickled_data = pickle.dumps(self)
        digest = hmac.digest(app.secret_key, pickled_data, "sha256")
        file = io.BytesIO(digest + b"   " + pickled_data)
        return file, digest  # File must be closed after use

    def airport_details(self, uk_airport, foreign_airport) -> None:
        self.uk_airport = uk_airport
        self.foreign_airport = Airport.all[foreign_airport]
        if self.uk_airport == "LPL":
            self.distance = self.foreign_airport.distance_from_lpl
        elif self.uk_airport == "BOH":
            self.distance = self.foreign_airport.distance_from_boh

    def airport_details_exist(self) -> bool:
        return self.uk_airport is not None and self.foreign_airport is not None

    def flight_details(self, aircraft, no_first_class) -> None:
        self.aircraft = aircraft
        self.no_first_class = int(no_first_class)
        self.no_standard_class = aircraft.max_standard_class - self.no_first_class * 2

    def flight_details_exist(self) -> bool:
        return self.aircraft is not None and self.no_first_class is not None

    def flight_in_range(self) -> Optional[bool]:
        if self.airport_details_exist() and self.flight_details_exist():
            return self.aircraft.range > self.distance
        else:
            return None

    def price_plan(self, standard_class_price, first_class_price) -> None:
        self.standard_class_price = float(standard_class_price)
        self.first_class_price = float(first_class_price)
        self.cost_per_seat = self.aircraft.running_cost * (self.distance / 100)
        self.running_cost = float(
            self.cost_per_seat * (self.no_first_class + self.no_standard_class)
        )
        self.income = float(
            self.no_first_class * self.first_class_price
            + self.no_standard_class * self.standard_class_price
        )
        self.profit = float(self.income - self.running_cost)

    def complete(self) -> bool:
        return (
            self.airport_details_exist()
            and self.flight_details_exist()
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


class FlightPlanJSONEncoder(JSONEncoder):
    def default(self, obj) -> str:
        return obj.__dict__


def insert_test_data(flight_plan) -> None:
    flight_plan.airport_details(
        random.choice(["LPL", "BOH"]),
        random.choice([airport.code for airport in Airport.all.values()]),
    )
    flight_plan.flight_details(random.choice(Aircraft.all), random.randint(15, 45))
    flight_plan.price_plan(
        round(random.uniform(25, 75), 2), round(random.uniform(100, 200), 2)
    )


def allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
