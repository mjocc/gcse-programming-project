import os
import platform

from flask import Flask

if platform.system() == "Windows":
    from dotenv import load_dotenv

    load_dotenv()

app = Flask(__name__)
app.secret_key = (
    bytes(os.environ["SECRET_KEY"], "utf-8").decode("unicode_escape").encode("latin-1")
)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1000 * 1000  # 1 MB limit for pickle file uploads
ALLOWED_EXTENSIONS = {"flightplan"}

from profit_calculator.__main__ import FlightPlan  # noqa
from profit_calculator.__main__ import (Aircraft, Airport,  # noqa
                                        FlightPlanJSONEncoder)

Airport.import_data()
Aircraft.import_data()
flight_plan = FlightPlan()
app.json_encoder = FlightPlanJSONEncoder

import profit_calculator.api  # noqa
import profit_calculator.views  # noqa
