from rdflib import Graph, Namespace, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import FOAF
import uuid
import yaml
import requests

from typing import List

class Catalog:

    def __init__(self, document):
        assert document.doc_id != None, "the document must have an id"
        self.id = str(document.doc_id)
        self.publisherUrl = "https://data.brreg.no/enhetsregisteret/api/enheter/" + document['publisher']
        self.title = document['title']
        self.description = document['description']
        self.dataservices = []
        for d in document['dataservices']:
            self.dataservices.append(d)

class Contact:
    def __init__(self, document):
        assert document['name'] != None, "the contact must have a name"
        self.name = document['name']
        if 'email' in document:
            self.email = document['email']
        if 'url' in document:
            self.url = document['url']

class DataService:

    def __init__(self, document):
        assert document.doc_id != None, "the document must have an id"
        self.id = str(document.doc_id)
        self.endpointdescription = document['endpointdescription']
        if 'title' in document:
            self.title = document['title']
        if 'description' in document:
            self.description = document['description']
        if 'endpointUrl' in document:
            self.endpointUrl = document['endpointUrl']
        if 'contact' in document:
            self.contactpoint = Contact(document['contact'])

def _add_catalog_to_graph(g: Graph, catalog: Catalog) -> Graph:

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    uri = "http://localhost:8080/catalogs/" + catalog.id

    # Add triples using store's add method.
    g.add( (URIRef(uri), RDF.type, dcat.Catalog) )
    g.add( (URIRef(uri), dct.publisher, URIRef(catalog.publisherUrl)) )
    g.add( (URIRef(uri), dct.title, Literal(catalog.title, lang='nb')) )

    return g

def _add_dataservice_to_graph(g: Graph, dataservice: DataService) -> Graph:

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)
    vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
    g.bind('vcard', vcard)
    dataservice_uri = "http://localhost:8080/dataservices/" + dataservice.id

    g.add( (URIRef(dataservice_uri), RDF.type, dcat.DataService) )
    g.add( (URIRef(dataservice_uri), dcat.endpointdescription, URIRef(dataservice.endpointdescription)) )
    if hasattr(dataservice, 'title'):
        g.add( (URIRef(dataservice_uri), dct.title, Literal(dataservice.title, lang='nb')) )
    if hasattr(dataservice, 'description'):
        g.add( (URIRef(dataservice_uri), dct.description, Literal(dataservice.description, lang='nb')) )
    if hasattr(dataservice, 'endpointUrl'):
        g.add( (URIRef(dataservice_uri), dcat.endpointUrl, URIRef(dataservice.endpointUrl)) )
    if hasattr(dataservice, 'contactpoint'):
        contactpoint = BNode()
        g.add( (URIRef(dataservice_uri), dcat.contactPoint, contactpoint) )
        g.add( (contactpoint, RDF.type, vcard.Organization) )
        if hasattr(dataservice.contactpoint, 'name'):
            g.add( (contactpoint, vcard.hasOrganizationName, Literal(dataservice.contactpoint.name, lang='nb')) )
        if hasattr(dataservice.contactpoint, 'email'):
            g.add( (contactpoint, vcard.hasEmail, URIRef('mailto:' + dataservice.contactpoint.email)) )
        if hasattr(dataservice.contactpoint, 'url'):
            g.add( (contactpoint, vcard.hasURL, URIRef(dataservice.contactpoint.url)) )

    return g

def map_catalogs_to_rdf(catalogs: List[Catalog], format='turtle') -> str:

    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    for c in catalogs:
        g = g + _add_catalog_to_graph(g, c)
        catalog_uri = "http://localhost:8080/catalogs/" + c.id
        for d in c.dataservices:
            dataservice_uri = "http://localhost:8080/dataservices/" + str(d)
            g.add( (URIRef(catalog_uri), dcat.service, URIRef(dataservice_uri)) )

    return g.serialize(format=format, encoding='utf-8')


def map_catalog_to_rdf(catalog: Catalog, format='turtle') -> str:
    """Adds the catalog c to the graph g and returns a serialization as a string according to format"""
    assert type(catalog) is Catalog, "type must be Catalog"

    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    catalog_uri = "http://localhost:8080/catalogs/" + catalog.id

    g = g + _add_catalog_to_graph(g, catalog)
    for d in catalog.dataservices:
        dataservice = DataService(d)
        dataservice_uri = "http://localhost:8080/dataservices/" + dataservice.id
        g = g + _add_dataservice_to_graph(g, dataservice)
        g.add( (URIRef(catalog_uri), dcat.service, URIRef(dataservice_uri)) )

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
