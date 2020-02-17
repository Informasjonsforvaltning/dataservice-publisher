import uuid
import yaml
import requests
from tinydb.database import Document
from typing import List

from dataservicecatalog.lib.mappers import Catalog
from .db import get_db

def fetch_catalogs() -> List[Catalog]:
    """Returns a list of Catalog objects"""
    db = get_db()
    catalogs = db.all()
    list = []
    for c in catalogs:
        c.id = c.doc_id
        catalog = Catalog(c)
        list.append(catalog)

    return list

def fetch_catalog_by_id(id) -> Catalog:
    """Returns Catalog objects with id = id"""
    assert id != None, "id can not be empty"
    db = get_db()
    c = db.get(doc_id=id)
    c.id = c.doc_id

    return Catalog(c)
