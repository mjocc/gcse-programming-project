from flask import Flask, session

app = Flask(__name__)
app.secret_key = b"3Fn9cPqKo5qDpEFXnGrI"

from profit_calculator.__main__ import (Aircraft, Airport, FlightPlan,
                                        FlightPlanJSONEncoder)

Airport.import_data()
Aircraft.import_data()
flight_plan = FlightPlan()
app.json_encoder = FlightPlanJSONEncoder

import profit_calculator.api
import profit_calculator.views
