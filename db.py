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
            return session.execute_read(
                lambda tx: [record for record in tx.run(query, parameters or {})]
            )


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
            "id": user.element_id,
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

    def create_post(self, username: str, content: str) -> None:
        query = """
        MATCH (u:User {username: $username})
        CREATE (p:Post {content: $content, timestamp: datetime()})
        CREATE (u)-[:POSTED]->(p)
        """
        self.execute_write(query, {"username": username, "content": content})

    def get_posts_by_user(self, username: str) -> List[dict]:
        query = """
        MATCH (u:User {username: $username})-[:POSTED]->(p:Post)
        RETURN p, u
        ORDER BY p.timestamp DESC
        """
        result = self.execute_read(query, {"username": username})
        return [{
            "content": record["p"]["content"],
            "timestamp": record["p"]["timestamp"],
            "username": record["u"]["username"],
            "name": record["u"]["name"]
        } for record in result]

    def follow_user(self, follower_username: str, followee_username: str) -> bool:
        query = """
        MATCH (follower:User {username: $follower})
        MATCH (followee:User {username: $followee})
        MERGE (follower)-[:FOLLOWS]->(followee)
        """
        self.execute_write(query, {"follower": follower_username, "followee": followee_username})
        return True

    def unfollow_user(self, follower_username: str, followee_username: str) -> bool:
        query = """
        MATCH (follower:User {username: $follower})-[r:FOLLOWS]->(followee:User {username: $followee})
        DELETE r
        """
        self.execute_write(query, {"follower": follower_username, "followee": followee_username})
        return True

    def get_followers(self, username: str) -> List[dict]:
        query = """
        MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
        RETURN follower
        """
        result = self.execute_read({"username": username}, query)
        return [{
            "id": record["follower"].element_id,
            "username": record["follower"]["username"],
            "name": record["follower"]["name"]
        } for record in result]

    def get_following(self, username: str) -> List[dict]:
        query = """
        MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
        RETURN following
        """
        result = self.execute_read(query, {"username": username})
        return [{
            "id": record["following"].element_id,
            "username": record["following"]["username"],
            "name": record["following"]["name"]
        } for record in result]
