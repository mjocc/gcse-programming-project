from flask import Flask

app = Flask(__name__)

from profit_calculator.__main__ import Aircraft, Airport, FlightPlan

Airport.import_data()
Aircraft.import_data()
flight_plan = FlightPlan()

import profit_calculator.api
import profit_calculator.views
