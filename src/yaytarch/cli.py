import click
from flask import current_app, Blueprint

from .db import get_db
from .model import configurationmodel
from src.yaytarch.tools import backup

# This blueprint takes care of the CLI and any future feature of it

bp = Blueprint('cli', __name__)


def init_db(location):
    db = get_db()

    # Run setup queries
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # Save download location setting
    configuration = configurationmodel.configuration(location, "", "")
    configurationmodel.initialconfiguration(configuration)


@bp.cli.command('init-db')
@click.argument("downloadlocation")
def init_db_command(downloadlocation):
    init_db(downloadlocation)
    click.echo('Initialised db.')


@bp.cli.command('lazyrestore')
@click.argument('location')
def lazyrestore(location):
    backup.lazyrestore(location)
