import platform

from profit_calculator import app

if platform.system() == "Windows":
    from waitress import serve

    if __name__ == "__main__":
        serve(app)  # serves app on localhost:8080
