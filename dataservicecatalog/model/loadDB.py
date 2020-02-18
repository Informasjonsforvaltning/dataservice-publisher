import os
from tinydb import TinyDB, where
import json
import requests
import yaml

db = TinyDB(os.getcwd()+'/dataservicecatalog/model/db.json')

# TODO: consider just using simple dicts, not classes here
class Catalog:

    def __init__(self, document):
        self.publisher = document['publisher']
        self.title = document['title']
        self.dataservices = []

class DataService:

    def __init__(self, url):
        self.endpointdescription = url
        assert url != None, "There must a endpointdescription"

        resp = requests.get(url)
        if resp.status_code == 200:
            description = yaml.safe_load(resp.text)
            self.title = description['info']['title']
            self.description = description['info']['description']
            # TODO: add more attributes to DataService from openAPI

datafile_path = os.getcwd()+'/dataservicecatalog/model/api-catalog_1.json'
datafile = open(datafile_path, 'r')
data = json.load(datafile)
catalogTable = db.table('catalogs')
dataserviceTable = db.table('dataservices')
for d in data:
    c = Catalog(d)
    for a in d['apis']:
        ds = DataService(a)
        id = dataserviceTable.insert(ds.__dict__)
        c.dataservices.append(id)
    catalogTable.insert(c.__dict__)

db.close()
