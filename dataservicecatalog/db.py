from tinydb import TinyDB, Query
import json

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = TinyDB('db.json')

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.purge()

def load_db():
    import os
    datafile_path = os.getcwd()+'/dataservicecatalog/api-catalog_1.json'
    datafile = open(datafile_path, 'r')
    data = json.load(datafile)
    db = get_db()
    for d in data:
        print(d)
        db.insert(d)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('load-db')
@with_appcontext
def load_db_command():
    """Loads the db with test data."""
    load_db()
    click.echo('Loaded the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_db_command)
