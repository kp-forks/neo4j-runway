import os
from typing import Any, Dict, List, Optional, Union

from neo4j import GraphDatabase

from ...exceptions import APOCNotInstalledError
from ..base import BaseGraph


class Neo4jGraph(BaseGraph):
    """
    Handler for Neo4j graph interactions.

    Attributes
    ----------
    apoc_version : Union[str, None]
        The APOC version present in the database.
    database : Union[str, None]
        The database name to run queries against in the Neo4j instance.
    database_edition : str
        The edition of the Neo4j instance.
    database_version : str
        The Neo4j version of the Neo4j instance.
    driver : Driver
        The driver used to communicate with Neo4j. Constructed from credentials provided to the constructor.
    gds_version : Union[str, None]
        The GDS version present in the database.
    schema : Union[Dict[str, Any], None]
        The database schema gathered from APOC.meta.schema
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        uri: Optional[str] = None,
        database: Optional[str] = None,
        driver_config: Dict[str, Any] = dict(),
    ) -> None:
        """
        Constructor for the Neo4jGraph.

        Parameters
        ----------
        username : Optional[str], optional
            Neo4j username. If not provided, will check NEO4J_USERNAME env variable. By default None
        password : Optional[str], optional
            Neo4j password. If not provided, will check NEO4J_PASSWORD env variable. By default None
        uri : Optional[str], optional
            Neo4j uri. If not provided, will check NEO4J_URI env variable. By default None
        database : Optional[str], optional
            Neo4j database to connect to. If not provided, will check NEO4J_DATABASE env variable. By default None
        driver_config : Dict[str, Any], optional
            Any additional configuration to provide the driver, by default dict()
        """
        if uri is None:
            uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.driver = GraphDatabase.driver(
            uri=uri,
            auth=(
                username or os.environ.get("NEO4J_USERNAME", "neo4j"),
                password or os.environ.get("NEO4J_PASSWORD", "password"),
            ),
            **driver_config,
        )
        self.database = database or os.environ.get("NEO4J_DATABASE", "neo4j")

        self.driver.verify_connectivity()

        self.apoc_version = self._get_apoc_version()
        self.gds_version = self._get_gds_version()
        self.database_version, self.database_edition = self._get_database_version()
        self._schema: Optional[Dict[str, Any]] = None

        super().__init__(driver=self.driver, version=self.database_version)

    @property
    def schema(self) -> Union[Dict[str, Any], None]:
        """
        The database schema provided by apoc.meta.schema

        Returns
        -------
        Dict[str, Any]
            The schema.
        """
        if self._schema is None:
            self.refresh_schema()
        return self._schema

    @schema.setter
    def schema(self, new_schema: Dict[str, Any]) -> None:
        self._schema = new_schema

    def verify(self) -> Dict[str, Any]:
        """
        Verify connection and authentication.

        Returns
        -------
        Dict[str, Any]
            Whether connection is successful and any messages.
        """

        try:
            self.driver.verify_connectivity()
            self.driver.verify_authentication()
        except Exception as e:
            return {
                "valid": False,
                "message": f"""
                            Are your credentials correct?
                            Connection Error: {e}
                            """,
            }
        return {"valid": True, "message": "Connection and Auth Verified!"}

    def _get_database_version(self) -> List[str]:
        """
        Retrieve the Neo4j version and edition of the database.

        Returns
        -------
        List[str]
            The Neo4j version and edition.
        """
        try:
            with self.driver.session(database=self.database) as session:
                response = session.run(
                    """CALL dbms.components()
    YIELD versions, edition
    RETURN versions[0] as version, edition"""
                ).single()
            if response is not None:
                version, edition = response.values()
                return [version, edition]
        except Exception:
            print("Unable to retrieve database version and edition.")

        return ["", ""]

    def _get_apoc_version(self) -> Union[str, None]:
        """
        Retrieve the APOC version running in the database.

        Returns
        -------
        str
            The APOC version or None if APOC not present on database.
        """
        try:
            with self.driver.session(database=self.database) as session:
                response = session.run("RETURN apoc.version()").single()
                if response is not None:
                    return str(response.value())
                else:
                    return None
        except Exception:
            # warnings.warn(
            #     "APOC is not found in the database. Some features such as schema retrieval depend on APOC."
            # )
            return None

    def _get_gds_version(self) -> Union[str, None]:
        """
        Retrieve the GDS version running in the database.

        Returns
        -------
        str
            The GDS version or None if GDS not present on database.
        """
        try:
            with self.driver.session(database=self.database) as session:
                response = session.run("RETURN gds.version()").single()
                if response is not None:
                    return str(response.value())
                else:
                    return None
        except Exception:
            # warnings.warn("GDS is not found in the database.")
            return None

    def refresh_schema(self) -> Dict[str, Any]:
        """
        Refresh the graph schema via APOC from the database.

        Raises
        ------
        APOCNotInstalledError
            If APOC is not installed on the Neo4j instance.

        Returns
        -------
        Dict[str, Any]
            The schema in APOC format, if APOC is present on database
        """
        try:
            with self.driver.session(database=self.database) as session:
                response: Dict[str, Any] = session.run(
                    """CALL apoc.meta.schema()
YIELD value
RETURN value as dataModel"""
                ).value()[0]

            self.schema = response
            return response
        except Exception:
            raise APOCNotInstalledError(
                "APOC must be installed to perform `refresh_schema` operation."
            )
