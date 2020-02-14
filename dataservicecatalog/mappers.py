from rdflib import Graph, Namespace, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import FOAF
import uuid

def map_to_rdf(catalogs, format='turtle'):
    g = Graph()

    dct = Namespace('http://purl.org/dc/terms/')
    g.bind('dct', dct)
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    g.bind('dcat', dcat)

    for c in catalogs:
        catalog = URIRef("http://localhost:8080/catalogs/" + str(c.doc_id))
        publisher = URIRef("https://data.brreg.no/enhetsregisteret/api/enheter/" + str(c['publisher']))
        title = Literal(str(c['title']))
        # Add triples using store's add method.
        g.add( (catalog, RDF.type, dcat.Catalog) )
        g.add( (catalog, dct.publisher, publisher) )
        g.add( (catalog, dct.title, title) )

        for a in c['apis']:
            api = URIRef("http://localhost:8080/dataservices/" + str(uuid.uuid4()))
            endpointdescription = URIRef(a)
            g.add( (api, RDF.type, dcat.DataService) )
            g.add( (api, dcat.endpointdescription, endpointdescription) )
            g.add( (catalog, dcat.service, api) )

            # TODO: parse the openAPI-document and map it to dataservice properties

    return g.serialize(format=format, encoding='utf-8')
