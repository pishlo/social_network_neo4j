from neo4j import GraphDatabase
from typing import Optional, List

class Database:
    def __init__(self, uri="bolt://localhost:7687", username="soni", password="Soni1709"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def execute_write(self, query, parameters=None):
        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run(query, parameters or {}))

    def execute_read(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.execute_read(lambda tx: tx.run(query, parameters or {}))
            return [record for record in result]

    # === Task 4: User operations using Cypher ===

    def create_user(self, username: str, name: str) -> None:
        query = """
        CREATE (u:User {username: $username, name: $name})
        """
        self.execute_write(query, {"username": username, "name": name})

    def get_user(self, username: str) -> Optional[dict]:
        query = """
        MATCH (u:User {username: $username})
        RETURN u
        """
        result = self.execute_read(query, {"username": username})
        if not result:
            return None
        user = result[0]["u"]
        return {
            "id": user.element_id,  # Neo4j's internal string ID
            "username": user["username"],
            "name": user["name"]
        }

    def get_all_users(self) -> List[dict]:
        query = """
        MATCH (u:User)
        RETURN u
        ORDER BY u.username
        """
        result = self.execute_read(query)
        return [{
            "id": record["u"].element_id,
            "username": record["u"]["username"],
            "name": record["u"]["name"]
        } for record in result]