import sys
import threading
import webbrowser
from view import create_app


def cli():
    args = sys.argv[1:]
    webbrowser.open(f"http://127.0.0.1:5000/")
    view()


def view():
    app = create_app()
    threading.Thread(target=lambda: app.run(port=5000)).run()

if __name__ == "__main__":
    cli()