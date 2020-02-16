import os
from tinydb import TinyDB, where
import json

db = TinyDB(os.getcwd()+'/dataservicecatalog/db.json')

datafile_path = os.getcwd()+'/dataservicecatalog/api-catalog_1.json'
datafile = open(datafile_path, 'r')
data = json.load(datafile)
for d in data:
    print(d)
    db.insert(d)

db.close()
