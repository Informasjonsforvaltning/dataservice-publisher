from rdflib import Graph, Namespace, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import FOAF
import uuid
import yaml
import requests

from typing import List

class Catalog:

    def __init__(self, document):
        assert document.id != None, "the document must have an id"
        self.id = str(document.id)
        self.uri = "http://localhost:8080/catalogs/" + self.id
        self.publisherUrl = "https://data.brreg.no/enhetsregisteret/api/enheter/" + document['publisher']
        self.title = document['title']
        self.dataservices = []

class DataService:

    def __init__(self, document):
        assert document.id != None, "the document must have an id"
        self.id = str(document.id)
        self.uri = "http://localhost:8080/dataservices/" + self.id
        self.endpointdescriptionUrl = document['endpointdescription']
        if 'title' in document:
            self.title = document['title']
        if 'description' in document:
            self.description = document['description']

def _add_catalog_to_graph(g: Graph, catalog: Catalog) -> Graph:

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    # Add triples using store's add method.
    g.add( (URIRef(catalog.uri), RDF.type, dcat.Catalog) )
    g.add( (URIRef(catalog.uri), dct.publisher, URIRef(catalog.publisherUrl)) )
    g.add( (URIRef(catalog.uri), dct.title, Literal(catalog.title, lang='nb')) )

    return g

def _add_dataservice_to_graph(g: Graph, dataservice: DataService) -> Graph:

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    g.add( (URIRef(dataservice.uri), RDF.type, dcat.DataService) )
    g.add( (URIRef(dataservice.uri), dcat.endpointdescription, URIRef(dataservice.endpointdescriptionUrl)) )
    if hasattr(dataservice, 'title'):
        g.add( (URIRef(dataservice.uri), dct.title, Literal(dataservice.title, lang='nb')) )
    if hasattr(dataservice, 'description'):
        g.add( (URIRef(dataservice.uri), dct.description, Literal(dataservice.description, lang='nb')) )

    return g

def map_catalogs_to_rdf(catalogs: List[Catalog], format='turtle') -> str:

    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    for c in catalogs:
        g = g + _add_catalog_to_graph(g, c)

    return g.serialize(format=format, encoding='utf-8')


def map_catalog_to_rdf(c: Catalog, format='turtle') -> str:
    """Adds the catalog c to the graph g and returns a serialization as a string according to format"""
    assert type(c) is Catalog, "type must be Catalog"

    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    g = g + _add_catalog_to_graph(g, c)

    for d in c.dataservices:
        dataservice = DataService(d)
        g = g + _add_dataservice_to_graph(g, dataservice)
        g.add( (URIRef(catalog.uri), dcat.service, URIRef(dataservice.uri)) )

    return g.serialize(format=format, encoding='utf-8')

def map_dataservices_to_rdf(dataservices: List[DataService], format='turtle') -> str:

    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    for d in dataservices:
        g = g + _add_dataservice_to_graph(g, d)

    return g.serialize(format=format, encoding='utf-8')


def map_dataservice_to_rdf(dataservice: DataService, format='turtle') -> str:
    """Adds the dataservice c to the graph g and returns a serialization as a string according to format"""
    assert type(dataservice) is DataService, "type must be DataService"

    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    g = g + _add_dataservice_to_graph(g, dataservice)

    return g.serialize(format=format, encoding='utf-8')
