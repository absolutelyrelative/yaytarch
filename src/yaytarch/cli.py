import sys
import threading
import webbrowser
import argparse
from view import create_app
from tools import videodownload


# Defines the behaviour of the user side CLI
def cli():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-f", "--folder", nargs='?', help="Open viewer on folder.", default='')
    argparser.add_argument("-d", "--download", help="Download video, playlist, or channel.", default='')
    args = argparser.parse_args()

    #  -f argument
    if args.folder != '':  # specifies folder for use in local mode
        webbrowser.open("http://127.0.0.1:5000/local")
        view()
    else:
        webbrowser.open("http://127.0.0.1:5000")
        view()

    #  -d argument
    if args.download != '':
        # videodownload.dl(args.download) # TODO: DEFINE local download
        sys.exit(0)


def view():
    app = create_app()
    threading.Thread(target=lambda: app.run(port=5000)).run()


if __name__ == "__main__":
    cli()
