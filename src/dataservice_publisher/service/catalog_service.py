"""Repository module for service layer."""
import logging
from os import environ as env

from datacatalogtordf import Catalog
from dotenv import load_dotenv
from oastodcat import OASDataService
from rdflib.graph import Graph, Literal, URIRef
import requests
from SPARQLWrapper import POST, SPARQLWrapper, TURTLE
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
import yaml

from dataservice_publisher.exceptions.exceptions import ErrorInRequstBodyException

load_dotenv()
DATASERVICE_PUBLISHER_URL = env.get("DATASERVICE_PUBLISHER_URL")
DATASET = env.get("FUSEKI_DATASET_1", "ds")
FUSEKI_PASSWORD = env.get("FUSEKI_PASSWORD")
FUSEKI_HOST_URL = env.get("FUSEKI_HOST_URL", "http://fuseki:3030")


def fetch_catalogs() -> Graph:
    """Returns a list of Catalog objects."""
    try:
        # Find all catalogs from all named graph
        # Find a specific catalog
        query_endpoint = f"{FUSEKI_HOST_URL}/{DATASET}/query"

        querystring = """
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            CONSTRUCT { ?s a dcat:Catalog .}
            WHERE { GRAPH ?g { ?s a dcat:Catalog .} }
        """
        sparql = SPARQLWrapper(query_endpoint)

        sparql.setQuery(querystring)

        sparql.setReturnFormat(TURTLE)
        sparql.setOnlyConneg(True)
        data = sparql.queryAndConvert()

        return Graph().parse(data=data, format="turtle")
    except SPARQLWrapperException as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise e


def _parse_user_input(catalog: dict) -> Graph:
    g = Catalog()

    g.identifier = URIRef(catalog["identifier"])
    g.title = catalog["title"]
    g.description = catalog["description"]
    g.publisher = catalog["publisher"]
    for api in catalog["apis"]:
        oas = yaml.safe_load(requests.get(api["url"]).text)
        oas_spec = OASDataService(api["url"], oas, api["identifier"])
        if "conformsTo" in api:
            oas_spec.conforms_to = api["conformsTo"]
        if "publisher" in api:
            oas_spec.publisher = api["publisher"]
        #
        # Add dataservices to catalog:
        for dataservice in oas_spec.dataservices:
            g.services.append(dataservice)

    return g._to_graph()


def create_catalog(catalog: dict) -> Graph:
    """Create a graph based on catalog and persist to store."""
    # Use datacatalogtordf and oastodcat to create a graph and persist:
    _g = Graph()
    try:
        _g = _parse_user_input(catalog)
    except TypeError:
        logging.exception("message")
        # Logs the error appropriately.
        raise ErrorInRequstBodyException("TypeError when processing request body")
    except KeyError:
        logging.exception("message")
        # Logs the error appropriately.
        raise ErrorInRequstBodyException("KeyError when processing request body")

    try:
        update_endpoint = f"{FUSEKI_HOST_URL}/{DATASET}/update"
        sparql = SPARQLWrapper(update_endpoint)
        sparql.setCredentials("admin", FUSEKI_PASSWORD)
        sparql.setMethod(POST)
        # Prepare query:
        prefixes = ""
        for ns in _g.namespaces():
            prefixes += f"PREFIX {ns[0]}: <{ns[1]}>\n"
        for s, p, o in _g:
            if isinstance(o, Literal):
                querystring = (
                    prefixes
                    + """
                    INSERT DATA {GRAPH <%s> {<%s> <%s> "%s"@%s}}
                    """
                    % (URIRef(catalog["identifier"]), s, p, o, o.language,)
                )
            else:
                querystring = (
                    prefixes
                    + """
                    INSERT DATA {GRAPH <%s> {<%s> <%s> <%s>}}
                    """
                    % (URIRef(catalog["identifier"]), s, p, o,)
                )

            sparql.setQuery(querystring)
            sparql.query()

        return _g
    except SPARQLWrapperException as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise e


def get_catalog_by_id(id: str) -> Graph:
    """Returns a specific catalog objects identified by id."""
    try:
        # Find a specific catalog
        context = URIRef(f"{DATASERVICE_PUBLISHER_URL}/catalogs/{id}")
        query_endpoint = f"{FUSEKI_HOST_URL}/{DATASET}/query"

        querystring = """
            CONSTRUCT { ?s ?p ?o }
            WHERE {
             GRAPH <%s> {?s ?p ?o}
            }
        """ % (
            context
        )
        sparql = SPARQLWrapper(query_endpoint)

        sparql.setQuery(querystring)

        sparql.setReturnFormat(TURTLE)
        sparql.setOnlyConneg(True)
        data = sparql.queryAndConvert()

        return Graph().parse(data=data, format="turtle")
    except Exception as e:
        # logging.exception("message")
        # Logs the error appropriately.
        raise e
