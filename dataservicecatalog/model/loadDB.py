import os
from tinydb import TinyDB, where
import json
import requests
import yaml

db = TinyDB(os.getcwd()+'/dataservicecatalog/model/db.json')

class Catalog:

    def __init__(self, document):
        self.publisher = "https://data.brreg.no/enhetsregisteret/api/enheter/" + document['publisher']
        self.title = document['title']
        self.dataservices = []

class DataService:

    def __init__(self, url):
        self.endpointdescription = url
        assert url != None, "There must a endpointdescription"
        # TODO: Refactor this code out of flask and into load-db script
        resp = requests.get(url)
        if resp.status_code == 200:
            description = yaml.safe_load(resp.text)
            self.title = description['info']['title']
            self.description = description['info']['description']

datafile_path = os.getcwd()+'/dataservicecatalog/model/api-catalog_1.json'
datafile = open(datafile_path, 'r')
data = json.load(datafile)
catalogTable = db.table('catalogs')
dataserviceTable = db.table('dataservices')
for d in data:
    c = Catalog(d)
    for a in d['apis']:
        ds = DataService(a)
        print(ds.__dict__)
        id = dataserviceTable.insert(ds.__dict__)
        c.dataservices.append(id)
    catalogTable.insert(c.__dict__)

db.close()
