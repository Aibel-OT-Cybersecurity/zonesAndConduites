from neo4j import GraphDatabase
import json

# Connect to the Neo4j database
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "TesterGraph"))

# Delete all nodes and relationships
with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
    print("Deleted all nodes and relationships")
# Load the JSON file
with open("policy_standard_list_2024_08_28.json") as file:
#with open("withZone.json") as file:
    ruleset = json.load(file)

# Create nodes and relationships
with driver.session() as session:
    for rule in ruleset:
        # Skip rules with "DENY" action
        if rule["Action"] == "DENY":
            print(f"Skipping DENY rule: {rule}")
            continue

        # Determine the label and name for the source node
        if rule["Source"] == "all":
            from_label = "Zone"
            from_node = rule["From"]
        else:
            from_label = "NetworkDevice"
            from_node = rule["Source"]
        session.run(f"MERGE (s:{from_label} {{name: $name}})", name=from_node)
        print(f"Created {from_label} FROM node: {from_node}")

        # Determine the label and name for the destination node
        if rule["Destination"] == "all":
            to_label = "Zone"
            to_node = rule["To"]
        else:
            to_label = "NetworkDevice"
            to_node = rule["Destination"]
        session.run(f"MERGE (d:{to_label} {{name: $name}})", name=to_node)
        print(f"Created {to_label} TO node: {to_node}")

        # Create relationships
        session.run(f"""
            MATCH (s:{from_label} {{name: $sourceName}})
            MATCH (d:{to_label} {{name: $destinationName}})
            MERGE (s)-[:CONDUIT {{
                name: $conduitName, 
                service: $serviceName, 
                NAT: $nat, 
                schedule: $schedule
            }}]->(d)
        """, sourceName=from_node, destinationName=to_node, conduitName=rule["Name"], serviceName=rule["Service"], nat=rule.get("NAT", ""), schedule=rule.get("Schedule", ""))

        print(f"Created conduit from {from_node} to {to_node}")

        # Create CONTAINS relationships if applicable
        if from_label == "NetworkDevice":
            session.run(f"""
                MATCH (z:Zone {{name: $zoneName}})
                MATCH (n:NetworkDevice {{name: $deviceName}})
                MERGE (z)-[:CONTAINS]->(n)
            """, zoneName=rule["From"], deviceName=from_node)
            print(f"Created CONTAINS relationship from Zone {rule['From']} to NetworkDevice {from_node}")

        if to_label == "NetworkDevice":
            session.run(f"""
                MATCH (z:Zone {{name: $zoneName}})
                MATCH (n:NetworkDevice {{name: $deviceName}})
                MERGE (z)-[:CONTAINS]->(n)
            """, zoneName=rule["To"], deviceName=to_node)
            print(f"Created CONTAINS relationship from Zone {rule['To']} to NetworkDevice {to_node}")
