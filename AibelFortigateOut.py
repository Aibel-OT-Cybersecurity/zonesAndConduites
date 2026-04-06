import json
from neo4j import GraphDatabase

# Neo4j connection details
uri = "bolt://localhost:7687"
username = "neo4j"
password = "TesterGraph"

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

with driver.session() as session:

    query = """
        MATCH (from:NetworkDevice)-[r:CONDUIT]->(to:NetworkDevice)
        OPTIONAL MATCH (from)<-[:CONTAINS]-(fz:Zone)
        OPTIONAL MATCH (to)<-[:CONTAINS]-(tz:Zone)
        WITH DISTINCT from, r, to, fz, tz
        OPTIONAL MATCH (fromz:Zone)-[rz:CONDUIT]->(toz:Zone)
        OPTIONAL MATCH (fromnd:NetworkDevice)-[rnd:CONDUIT]->(toz:Zone)
        OPTIONAL MATCH (fromz:Zone)-[rz:CONDUIT]->(tond:NetworkDevice)
        RETURN DISTINCT  from, r, to, fz, tz, rz, toz, fromnd, rnd, tond
    """
    result = session.run(query)

    rules = []
    for record in result:
        
        from_node = record['fromz']
        to_node = record['toz']
        conduit = record['r']
        source = record['from']
        destination = record['to']

        rule = {
            "Name": conduit.get('name', 'Unnamed Rule'),
            "From": from_node.get('name', 'Unknown From'),
            "To": to_node.get('name', 'Unknown To'),
            "Source": source.get('name', '0.0.0.0'),
            "Destination": destination.get('name', '0.0.0.0'),
            "Schedule": conduit.get('schedule', 'Always'),
            "Service": conduit.get('service', 'ALL'),
            "Action": "ACCEPT",  # Default value
            "NAT": conduit.get('nat', 'None'),
            "Security Profiles": "no-inspection",  # Default value
            "Log": "UTM",  # Default value
            "Bytes": "0 B",  # Default value, you might want to calculate this
            "Type": "Standard"  # Default value
        }

        rules.append(rule)

file_path = '/home/bent/Desktop/git/Documentation/zonesAndConduites/firewall.json'

with open(file_path, 'w') as json_file:
    json.dump(rules, json_file, indent=4)

driver.close()
