import os
from tinydb import TinyDB, where
import json
import requests
import yaml

db = TinyDB(os.getcwd()+'/dataservicecatalog/model/db.json')

def create_catalog(document):
    catalog = {}
    catalog['publisher'] = document['publisher']
    catalog['title'] = document['title']
    catalog['description'] = document['description']
    catalog['dataservices'] = []

    return catalog

def create_dataservice(url):
    dataservice = {}
    dataservice['endpointdescription'] = url
    assert url != None, "There must a endpointdescription"

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
                dataservice['contact']['name'] = description['info']['contact']['name']
    return dataservice

datafile_path = os.getcwd()+'/dataservicecatalog/model/api-catalog_1.json'
datafile = open(datafile_path, 'r')
data = json.load(datafile)
catalogTable = db.table('catalogs')
dataserviceTable = db.table('dataservices')
for d in data:
    c = create_catalog(d)
    for a in d['apis']:
        ds = create_dataservice(a)
        id = dataserviceTable.insert(ds)
        c['dataservices'].append(id)
    catalogTable.insert(c)

db.close()
