from profit_calculator import app

from waitress import serve

if __name__ == "__main__":
    serve(app)  # runs on localhost:8080
