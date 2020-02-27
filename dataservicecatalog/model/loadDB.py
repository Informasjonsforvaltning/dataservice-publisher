import os
from tinydb import TinyDB
import json
import requests
import yaml


def _create_catalog(document):
    return {
      'publisher': document['publisher'],
      'title': document['title'],
      'description': document['description'],
      'dataservices': []
    }


def _create_dataservice(url):
    dataservice = {}
    dataservice['endpointdescription'] = url
    assert url is not None, "There must a endpointdescription"

    resp = requests.get(url)
    if resp.status_code == 200:
        description = yaml.safe_load(resp.text)
        dataservice['title'] = description['info']['title']
        dataservice['description'] = description['info']['description']
        if 'servers' in description:
            dataservice['endpointUrl'] = description['servers'][0]['url']
        if 'contact' in description['info']:
            dataservice['contact'] = {}
            if 'name' in description['info']['contact']:
                dataservice['contact']['name'] = (
                    description['info']['contact']['name']
                )
            if 'email' in description['info']['contact']:
                dataservice['contact']['email'] = (
                   description['info']['contact']['email']
                )
            if 'url' in description['info']['contact']:
                dataservice['contact']['url'] = (
                   description['info']['contact']['url']
                )
    return dataservice


def load_db():
    db = TinyDB(os.getcwd()+'/dataservicecatalog/model/db.json')
    datafile_path = os.getcwd()+'/dataservicecatalog/model/api-catalog_1.json'
    datafile = open(datafile_path, 'r')
    data = json.load(datafile)
    catalogTable = db.table('catalogs')
    dataserviceTable = db.table('dataservices')
    for d in data:
        c = _create_catalog(d)
        for a in d['apis']:
            ds = _create_dataservice(a)
            id = dataserviceTable.insert(ds)
            c['dataservices'].append(id)
        catalogTable.insert(c)

    db.close()


if __name__ == "__main__":
    load_db()
