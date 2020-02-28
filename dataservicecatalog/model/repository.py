from typing import List

from dataservicecatalog.lib.mappers import Catalog, DataService
from .db import get_db


def fetch_catalogs() -> List[Catalog]:
    """Returns a list of Catalog objects"""
    db = get_db()
    catalogTable = db.table('catalogs')
    catalogs = catalogTable.all()
    list = []
    for c in catalogs:
        c.id = c.doc_id
        catalog = Catalog(c)
        list.append(catalog)

    return list


def fetch_catalog_by_id(id) -> Catalog:
    """Returns a Catalog object with id = id"""
    assert id is not None, "id can not be empty"
    db = get_db()
    catalogTable = db.table('catalogs')
    dataserviceTable = db.table('dataservices')
    catalog = catalogTable.get(doc_id=id)
    if catalog is None:
        return None
    catalog.id = catalog.doc_id

    _dataservices = []
    for d in catalog['dataservices']:
        _d = {}
        _d = dataserviceTable.get(doc_id=d)
        _d['id'] = _d.doc_id
        _dataservices.append(_d)
    catalog['dataservices'] = _dataservices

    return Catalog(catalog)


def fetch_dataservices() -> List[DataService]:
    """Returns a list of DataService objects"""
    db = get_db()
    dataserviceTable = db.table('dataservices')
    dataservices = dataserviceTable.all()
    list = []
    for d in dataservices:
        d.id = d.doc_id
        dataservice = DataService(d)
        list.append(dataservice)

    return list


def fetch_dataservice_by_id(id) -> DataService:
    """Returns a DataService object with id = id"""
    assert id is not None, "id can not be empty"
    db = get_db()
    dataserviceTable = db.table('dataservices')
    dataservice = dataserviceTable.get(doc_id=id)
    if dataservice is None:
        return None
    dataservice['id'] = dataservice.doc_id
    return DataService(dataservice)
