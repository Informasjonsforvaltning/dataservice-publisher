from rdflib import Graph, Namespace, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import FOAF
import uuid
import yaml
import requests

class DataService:

    def __init__(self, endpointdescription):
        self.id = str(uuid.uuid4())
        self.uri = URIRef("http://localhost:8080/dataservices/" + self.id)
        self.endpointdescriptionUrl = URIRef(endpointdescription)

        assert endpointdescription != None, "There must a endpointdescription"
        # TODO: Refactor this code out of flask and into load-db script
        resp = requests.get(endpointdescription)
        print(resp.status_code)
        if resp.status_code == 200:
            description = yaml.safe_load(resp.text)
            self.title = description['info']['title']
            self.description = description['info']['description']

def map_catalogs_to_rdf(catalogs, format='turtle'):
    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    for c in catalogs:
        catalog = URIRef("http://localhost:8080/catalogs/" + str(c.doc_id))
        publisher = URIRef("https://data.brreg.no/enhetsregisteret/api/enheter/" + str(c['publisher']))
        title = Literal(str(c['title']), lang='nb')
        # Add triples using store's add method.
        g.add( (catalog, RDF.type, dcat.Catalog) )
        g.add( (catalog, dct.publisher, publisher) )
        g.add( (catalog, dct.title, title) )

        # TODO: Consider dropping the apis from the list of catalogs. Should belong to getCatalogById
        for a in c['apis']:
            dataService = DataService(a)

            g.add( (dataService.uri, RDF.type, dcat.DataService) )
            g.add( (dataService.uri, dcat.endpointdescription, URIRef(dataService.endpointdescriptionUrl)) )
            if hasattr(dataService, 'title'):
                g.add( (dataService.uri, dct.title, Literal(dataService.title, lang='nb')) )
            if hasattr(dataService, 'description'):
                g.add( (dataService.uri, dct.description, Literal(dataService.description, lang='nb')) )
            g.add( (catalog, dcat.service, dataService.uri) )

            # TODO: parse the openAPI-document and map it to dataService properties

    return g.serialize(format=format, encoding='utf-8')


def map_catalog_to_rdf(c, format='turtle'):
    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    catalog = URIRef("http://localhost:8080/catalogs/" + str(c.doc_id))
    publisher = URIRef("https://data.brreg.no/enhetsregisteret/api/enheter/" + str(c['publisher']))
    title = Literal(str(c['title']), lang='nb')
    # Add triples using store's add method.
    g.add( (catalog, RDF.type, dcat.Catalog) )
    g.add( (catalog, dct.publisher, publisher) )
    g.add( (catalog, dct.title, title) )

    # TODO: Consider dropping the apis from the list of catalogs. Should belong to getCatalogById
    for a in c['apis']:
        dataService = DataService(a)

        g.add( (dataService.uri, RDF.type, dcat.DataService) )
        g.add( (dataService.uri, dcat.endpointdescription, URIRef(dataService.endpointdescriptionUrl)) )
        if hasattr(dataService, 'title'):
            g.add( (dataService.uri, dct.title, Literal(dataService.title, lang='nb')) )
        if hasattr(dataService, 'description'):
            g.add( (dataService.uri, dct.description, Literal(dataService.description, lang='nb')) )
        g.add( (catalog, dcat.service, dataService.uri) )

        # TODO: parse the openAPI-document and map it to dataService properties

    return g.serialize(format=format, encoding='utf-8')
