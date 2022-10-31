"""Repository module for service layer."""
import logging
from os import environ as env

from aiohttp import ClientSession
from datacatalogtordf import Catalog
from dotenv import load_dotenv
from oastodcat import OASDataService
from rdflib.graph import Graph, Literal, URIRef
from SPARQLWrapper import POST, SPARQLWrapper, TURTLE
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
import yaml

from dataservice_publisher.exceptions.exceptions import RequestBodyError

load_dotenv()
DATASERVICE_PUBLISHER_URL = env.get("DATASERVICE_PUBLISHER_URL")
DATASET = env.get("FUSEKI_DATASET_1", "ds")
FUSEKI_PASSWORD = env.get("FUSEKI_PASSWORD")
FUSEKI_HOST = env.get("FUSEKI_HOST", "http://fuseki")
FUSEKI_PORT = int(env.get("FUSEKI_PORT", 8080))


async def fetch_catalogs() -> Graph:
    """Returns a list of Catalog objects."""
    logging.debug("Fetch catalogs")
    try:
        # Find all catalogs from all named graph
        # Find a specific catalog
        query_endpoint = f"{FUSEKI_HOST}:{FUSEKI_PORT}/fuseki/{DATASET}"

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

        return Graph().parse(data=data, format="turtle")  # type: ignore
    except SPARQLWrapperException as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise e


async def _parse_user_input(catalog: dict) -> Graph:
    g = Catalog()
    g.identifier = URIRef(catalog["identifier"])
    g.title = catalog["title"]
    g.description = catalog["description"]
    g.publisher = catalog["publisher"]
    # TODO: consider doing the request in parallel
    for api in catalog["apis"]:
        logging.debug(f"""getting ${api["url"]}""")
        async with ClientSession() as session:
            async with session.get(api["url"]) as response:
                logging.debug(f"""${api["url"]}: ${response.status}""")
                if response.status == 200:
                    api_spec = await response.text()
                    oas = yaml.safe_load(api_spec)

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


async def create_catalog(catalog: dict) -> Graph:
    """Create a graph based on catalog and persist to store."""
    # Use datacatalogtordf and oastodcat to create a graph and persist:
    _g = Graph()
    logging.info("creating and persisting graph from catalog")
    try:
        _g = await _parse_user_input(catalog)
    except TypeError as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise RequestBodyError("TypeError when processing request body") from e
    except KeyError as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise RequestBodyError("KeyError when processing request body") from e

    try:
        update_endpoint = f"{FUSEKI_HOST}:{FUSEKI_PORT}/fuseki/{DATASET}/update"
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
                    % (
                        URIRef(catalog["identifier"]),
                        s,
                        p,
                        o,
                        o.language,
                    )
                )
            else:
                querystring = (
                    prefixes
                    + """
                    INSERT DATA {GRAPH <%s> {<%s> <%s> <%s>}}
                    """
                    % (
                        URIRef(catalog["identifier"]),
                        s,
                        p,
                        o,
                    )
                )

            sparql.setQuery(querystring)
            sparql.query()

        return _g
    except SPARQLWrapperException as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise e


async def get_catalog_by_id(id: str) -> Graph:
    """Returns a specific catalog objects identified by id."""
    logging.debug(f"Get catalog by id: {id}")
    try:
        # Find a specific catalog
        context = URIRef(f"{DATASERVICE_PUBLISHER_URL}/catalogs/{id}")
        query_endpoint = f"{FUSEKI_HOST}:{FUSEKI_PORT}/fuseki/{DATASET}"

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
        # logging.debug(f"querystring: {querystring}")

        sparql.setReturnFormat(TURTLE)
        sparql.setOnlyConneg(True)
        data = sparql.queryAndConvert()
        # logging.debug(f"data: {data!r}")

        return Graph().parse(data=data, format="turtle")  # type: ignore
    except SPARQLWrapperException as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise e


async def delete_catalog(id: str) -> bool:
    """Delete the graph given by id and return true if successful."""
    try:
        context = URIRef(f"{DATASERVICE_PUBLISHER_URL}/catalogs/{id}")
        update_endpoint = f"{FUSEKI_HOST}:{FUSEKI_PORT}/fuseki/{DATASET}/update"
        sparql = SPARQLWrapper(update_endpoint)
        sparql.setCredentials("admin", FUSEKI_PASSWORD)
        sparql.setMethod(POST)
        # Prepare query:
        querystring = """
            DROP GRAPH <%s>
        """ % (
            URIRef(context),
        )

        sparql.setQuery(querystring)
        result = sparql.query()
        if result.response.status == 200:
            return True
    except SPARQLWrapperException as e:
        logging.exception("message")
        # Logs the error appropriately.
        raise e
    return False
