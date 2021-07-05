from waitress import serve

from profit_calculator import app

if __name__ == "__main__":
    serve(app)  # serves app on localhost:8080
