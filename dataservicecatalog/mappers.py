from rdflib import Graph, Namespace, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import FOAF
import uuid
import yaml
import requests

class Catalog:

    def __init__(self, catalog):
        print(catalog)
        self.id = str(catalog.doc_id)
        self.uri = "http://localhost:8080/catalogs/" + self.id
        self.publisherUrl = "https://data.brreg.no/enhetsregisteret/api/enheter/" + catalog['publisher']
        self.title = catalog['title']

class DataService:

    def __init__(self, endpointdescription):
        self.id = str(uuid.uuid4())
        self.uri = "http://localhost:8080/dataservices/" + self.id
        self.endpointdescriptionUrl = endpointdescription

        assert endpointdescription != None, "There must a endpointdescription"
        # TODO: Refactor this code out of flask and into load-db script
        resp = requests.get(endpointdescription)
        print(resp.status_code)
        if resp.status_code == 200:
            description = yaml.safe_load(resp.text)
            self.title = description['info']['title']
            self.description = description['info']['description']

def _add_catalog_to_graph(g, catalog):

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    # Add triples using store's add method.
    g.add( (URIRef(catalog.uri), RDF.type, dcat.Catalog) )
    g.add( (URIRef(catalog.uri), dct.publisher, URIRef(catalog.publisherUrl)) )
    g.add( (URIRef(catalog.uri), dct.title, Literal(catalog.title, lang='nb')) )

    return g

def _add_dataservice_to_graph(g, dataService):

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    g.add( (URIRef(dataService.uri), RDF.type, dcat.DataService) )
    g.add( (URIRef(dataService.uri), dcat.endpointdescription, URIRef(dataService.endpointdescriptionUrl)) )
    if hasattr(dataService, 'title'):
        g.add( (URIRef(dataService.uri), dct.title, Literal(dataService.title, lang='nb')) )
    if hasattr(dataService, 'description'):
        g.add( (URIRef(dataService.uri), dct.description, Literal(dataService.description, lang='nb')) )

    return g

def map_catalogs_to_rdf(catalogs, format='turtle'):
    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    for c in catalogs:
        catalog = Catalog(c)
        g = g + _add_catalog_to_graph(g, catalog)

    return g.serialize(format=format, encoding='utf-8')


def map_catalog_to_rdf(c, format='turtle'):
    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    catalog = Catalog(c)
    g = g + _add_catalog_to_graph(g, catalog)

    for a in c['apis']:
        dataService = DataService(a)
        g = g + _add_dataservice_to_graph(g, dataService)
        g.add( (URIRef(catalog.uri), dcat.service, URIRef(dataService.uri)) )

    return g.serialize(format=format, encoding='utf-8')
