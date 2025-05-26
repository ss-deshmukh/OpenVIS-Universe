from neo4j import GraphDatabase

class SchemaExplorer:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def explore_schema(self):
        """Explore the database schema to understand node labels and relationships"""
        with self.driver.session() as session:
            print("=== DATABASE SCHEMA EXPLORATION ===\n")
            
            # Get all node labels
            print("1. NODE LABELS:")
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            for label in labels:
                print(f"   - {label}")
            
            print(f"\nTotal labels: {len(labels)}\n")
            
            # Get all relationship types
            print("2. RELATIONSHIP TYPES:")
            result = session.run("CALL db.relationshipTypes()")
            rel_types = [record["relationshipType"] for record in result]
            for rel_type in rel_types:
                print(f"   - {rel_type}")
            
            print(f"\nTotal relationship types: {len(rel_types)}\n")
            
            # Sample nodes from each label
            print("3. SAMPLE NODES (first 3 from each label):")
            for label in labels[:5]:  # Limit to first 5 labels to avoid too much output
                print(f"\n   {label} nodes:")
                query = f"MATCH (n:{label}) RETURN n LIMIT 3"
                result = session.run(query)
                for i, record in enumerate(result):
                    node = record["n"]
                    properties = dict(node)
                    print(f"     Node {i+1}: {properties}")
            
            # Sample relationships
            print("\n4. SAMPLE RELATIONSHIPS (first 5):")
            query = "MATCH (a)-[r]->(b) RETURN type(r) as rel_type, labels(a) as start_labels, labels(b) as end_labels, r LIMIT 5"
            result = session.run(query)
            for i, record in enumerate(result):
                print(f"     Relationship {i+1}:")
                print(f"       Type: {record['rel_type']}")
                print(f"       From: {record['start_labels']} -> To: {record['end_labels']}")
                print(f"       Properties: {dict(record['r'])}")
                print()
            
            # Count nodes by label
            print("5. NODE COUNTS BY LABEL:")
            for label in labels:
                query = f"MATCH (n:{label}) RETURN count(n) as count"
                result = session.run(query)
                count = result.single()["count"]
                print(f"   {label}: {count} nodes")
            
            # Count relationships by type
            print("\n6. RELATIONSHIP COUNTS BY TYPE:")
            for rel_type in rel_types:
                query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
                result = session.run(query)
                count = result.single()["count"]
                print(f"   {rel_type}: {count} relationships")

def main():
    # Connection details
    URI = "neo4j+s://56bf968b.databases.neo4j.io"
    USER = "neo4j"
    PASSWORD = "BJX7_gT3khz6BiBezhTrbi-dRl0l-_dfI3fUyuKiX5g"
    
    explorer = SchemaExplorer(URI, USER, PASSWORD)
    
    try:
        explorer.explore_schema()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        explorer.close()

if __name__ == "__main__":
    main() 