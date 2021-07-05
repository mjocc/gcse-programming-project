from flask import Flask

app = Flask(__name__)
app.secret_key = b"L!.+\xf7w\x80\xec\x15}.\xb2\xaa\x85\xeeF"

from profit_calculator.__main__ import FlightPlan  # noqa
from profit_calculator.__main__ import Aircraft, Airport, FlightPlanJSONEncoder

Airport.import_data()
Aircraft.import_data()
flight_plan = FlightPlan()
app.json_encoder = FlightPlanJSONEncoder

import profit_calculator.api  # noqa
import profit_calculator.views  # noqa
