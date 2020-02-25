import os
from tinydb import TinyDB, where
import json

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = TinyDB(os.getcwd()+'/dataservicecatalog/model/db.json')

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.purge_tables()
    db.purge()

def load_db():
    datafile_path = os.getcwd()+'/dataservicecatalog/model/api-catalog_1.json'
    datafile = open(datafile_path, 'r')
    data = json.load(datafile)
    db = get_db()
    catalogTable = db.table('catalogs')
    for d in data:
        catalogTable.insert(d)


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