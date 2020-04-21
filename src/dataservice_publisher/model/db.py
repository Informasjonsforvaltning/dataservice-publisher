"""Db module for implementation of data storage."""
import os
from typing import Any

import click
from flask import g
from flask.cli import with_appcontext
from tinydb import TinyDB

from .loadDB import load_db


def get_db() -> Any:
    """Get the specific db instance."""
    if "db" not in g:
        g.db = TinyDB(os.getcwd() + "/dataservice_publisher/model/db.json")

    return g.db


def close_db(e: Any = None) -> Any:
    """Close the db instance."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db() -> Any:
    """Init the db instance."""
    db = get_db()
    db.purge_tables()
    db.purge()


@click.command("init-db")
@with_appcontext
def init_db_command() -> Any:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("load-db")
@with_appcontext
def load_db_command() -> Any:
    """Loads the db with test data."""
    load_db()
    click.echo("Loaded the database.")


def init_app(app: Any) -> Any:
    """Init function for datastorage module."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_db_command)
