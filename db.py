import sqlite3

import click
from flask import current_app, g

from model import configurationmodel


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES  # why not columns?
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db(location):
    db = get_db()

    # Run setup queries
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # Save download location setting
    configuration = configurationmodel.configuration(location, "", "")
    configurationmodel.initialconfiguration(configuration)


@click.command('init-db')
@click.argument("downloadlocation")
def init_db_command(downloadlocation):
    init_db(downloadlocation)
    click.echo('Initialised db.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
