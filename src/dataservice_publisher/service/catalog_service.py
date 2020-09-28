"""Repository module for service layer."""
import logging
from os import environ as env
from typing import Any

from datacatalogtordf import Catalog
from dotenv import load_dotenv
from oastodcat import OASDataService
from rdflib.graph import Graph, Literal, URIRef
import requests
from SPARQLWrapper import POST, SPARQLWrapper, TURTLE
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
import yaml


load_dotenv()
HOST = env.get("HOST", "dataservice-publisher")
PORT = int(env.get("PORT", "8080"))
DATASET = env.get("DATASET_1", "ds")
FUSEKI_PASSWORD = env.get("FUSEKI_PASSWORD")
FUSEKI_HOST = env.get("FUSEKI_HOST", "fuseki")
FUSEKI_PORT = int(env.get("FUSEKI_PORT", "3030"))


def fetch_catalogs() -> Graph:
    """Returns a list of Catalog objects."""
    try:
        # Find all catalogs from all named graph
        # Find a specific catalog
        query_endpoint = f"http://{FUSEKI_HOST}:{FUSEKI_PORT}/{DATASET}/query"

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


def create_catalog(catalog: dict) -> Any:
    """Create a graph based on catalog and persist to store."""
    # Use datacatalogtordf and oastodcat to create a graph and persist:
    try:
        _catalog = Catalog()
        # create a hash based on publisher and id
        _catalog.identifier = URIRef(catalog["identifier"])
        _catalog.title = catalog["title"]
        _catalog.description = catalog["description"]
        _catalog.publisher = catalog["publisher"]
        for api in catalog["apis"]:
            oas = yaml.safe_load(requests.get(api["url"]).text)
            _dataservice = OASDataService(oas)
            _dataservice.identifier = api["identifier"]
            _dataservice.endpointDescription = api["url"]
            #
            # Add dataservice to catalog:
            _catalog.services.append(_dataservice)

        g = _catalog._to_graph()

        update_endpoint = f"http://{FUSEKI_HOST}:{FUSEKI_PORT}/{DATASET}/update"
        sparql = SPARQLWrapper(update_endpoint)
        sparql.setCredentials("admin", FUSEKI_PASSWORD)
        sparql.setMethod(POST)
        # Prepare query:
        prefixes = ""
        for ns in g.namespaces():
            prefixes += f"PREFIX {ns[0]}: <{ns[1]}>\n"
        for s, p, o in g:
            if isinstance(o, Literal):
                querystring = (
                    prefixes
                    + """
                    INSERT DATA {GRAPH <%s> {<%s> <%s> "%s"@%s}}
                    """
                    % (_catalog.identifier, s, p, o, o.language,)
                )
            else:
                querystring = (
                    prefixes
                    + """
                    INSERT DATA {GRAPH <%s> {<%s> <%s> <%s>}}
                    """
                    % (_catalog.identifier, s, p, o,)
                )

            sparql.setQuery(querystring)
            sparql.query()

        return _catalog.identifier
    except SPARQLWrapperException as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise e


def get_catalog_by_id(id: str) -> Graph:
    """Returns a specific catalog objects identified by id."""
    try:
        # Find a specific catalog
        context = URIRef(f"http://{HOST}:{PORT}/catalogs/{id}")
        query_endpoint = f"http://{FUSEKI_HOST}:{FUSEKI_PORT}/{DATASET}/query"

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