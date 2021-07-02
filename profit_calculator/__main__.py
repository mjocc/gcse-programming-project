from __future__ import annotations

import csv
from typing import Optional


class Airport:
    all: dict[str, Airport] = {}

    def __init__(self, code, name, distance_from_lpl, distance_from_boh) -> None:
        self.code: str = code
        self.name: str = name
        self.distance_from_lpl: float = float(distance_from_lpl)
        self.distance_from_boh: float = float(distance_from_boh)

    def __repr__(self) -> str:
        return f"{self.code}: {self.name}"

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def import_data() -> None:
        with open("Airports.txt", "r") as file:
            reader: list[str] = list(csv.reader(file))
        for row in reader:
            __class__.all[row[0]] = Airport(*row)


class Aircraft:
    all: list[Aircraft] = []

    def __init__(
        self, type, running_cost, range, max_standard_class, min_first_class
    ) -> None:
        self.type: str = type
        self.running_cost: float = float(
            running_cost
        )  # running cost per seat per 100km
        self.max_standard_class: int = int(max_standard_class)
        self.min_first_class: int = int(min_first_class)

    def __repr__(self) -> str:
        return f"{__class__.all.index(self)}: {self.type}"

    def __str__(self) -> str:
        return self.type

    @staticmethod
    def import_data() -> None:
        with open("Aircraft.txt", "r") as file:
            reader: list[str] = list(csv.reader(file))
        for row in reader:
            __class__.all.append(Aircraft(*row))


class FlightPlan:
    def __init__(self) -> None:
        self.uk_airport: Optional[str] = None
        self.foreign_airport: Optional[Airport] = None
        self.distance: Optional[float] = None

        self.aircraft: Optional[Aircraft] = None
        self.no_first_class: Optional[int] = None
        self.no_standard_class: Optional[int] = None

        self.standard_class_price: Optional[float] = None
        self.first_class_price: Optional[float] = None
        self.cost_per_seat: Optional[float] = None
        self.running_cost: Optional[float] = None
        self.income: Optional[float] = None
        self.profit: Optional[float] = None

    def airport_details(self, uk_airport, foreign_airport):
        self.uk_airport = uk_airport
        self.foreign_airport = Airport.all[foreign_airport]
        if self.uk_airport == "LPL":
            self.distance = self.foreign_airport.distance_from_lpl
        elif self.uk_airport == "BOH":
            self.distance = self.foreign_airport.distance_from_boh

    def flight_details(self, aircraft, no_first_class):
        self.aircraft = aircraft
        self.no_first_class = int(no_first_class)
        self.no_standard_class = aircraft.max_standard_class - self.no_first_class * 2

    def price_plan(self, standard_class_price, first_class_price):
        self.standard_class_price = float(standard_class_price)
        self.first_class_price = float(first_class_price)
        self.cost_per_seat = self.aircraft.running_cost
        self.running_cost = float(
            self.cost_per_seat * (self.no_first_class + self.no_standard_class)
        )
        self.income = float(
            self.no_first_class * self.first_class_price
            + self.no_standard_class * self.standard_class_price
        )
        self.profit = float(self.flight_income - self.flight_cost)


def clear_data():
    pass
