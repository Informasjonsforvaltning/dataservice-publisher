import os
from tinydb import TinyDB
import json
import requests
import yaml

DB = TinyDB(os.getcwd() + "/dataservice_publisher/model/db.json")


def _create_catalog(document):
    return {
        "publisher": document["publisher"],
        "title": document["title"],
        "description": document["description"],
        "dataservices": [],
    }


def _create_dataservice(url):
    dataservice = {}
    dataservice["endpointDescription"] = url
    assert url is not None, "There must a endpointDescription"

    resp = requests.get(url)
    if resp.status_code == 200:
        description = yaml.safe_load(resp.text)
        dataservice["title"] = description["info"]["title"]
        dataservice["description"] = description["info"]["description"]
        if "servers" in description:
            dataservice["endpointURL"] = description["servers"][0]["url"]
        if "contact" in description["info"]:
            dataservice["contact"] = {}
            if "name" in description["info"]["contact"]:
                dataservice["contact"]["name"] = description["info"]["contact"]["name"]
            if "email" in description["info"]["contact"]:
                dataservice["contact"]["email"] = description["info"]["contact"][
                    "email"
                ]
            if "url" in description["info"]["contact"]:
                dataservice["contact"]["url"] = description["info"]["contact"]["url"]
    return dataservice


def init_db():
    DB.purge_tables()
    DB.purge()


def load_db():
    datafile_path = os.getcwd() + "/dataservice_publisher/model/api-catalog_1.json"
    datafile = open(datafile_path, "r")
    data = json.load(datafile)
    catalogTable = DB.table("catalogs")
    dataserviceTable = DB.table("dataservices")
    for dataservice in data:
        catalog = _create_catalog(dataservice)
        for api in dataservice["apis"]:
            _dataservice = _create_dataservice(api)
            id = dataserviceTable.insert(_dataservice)
            catalog["dataservices"].append(id)
        catalogTable.insert(catalog)

    DB.close()


if __name__ == "__main__":
    init_db()
    load_db()
