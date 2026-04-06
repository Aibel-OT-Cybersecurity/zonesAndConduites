from neo4j import GraphDatabase
# Remember to:pip install neo4j
import csv

# Connect to Neo4j database.
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "TesterGraph"))
with driver.session() as session:
    # Delete all nodes and edges.
    session.run("MATCH (n) DETACH DELETE n")

# Open the CSV file
with open('ZaC-ABB-WithSL-T.csv', 'r') as file:
    reader = csv.reader(file)
    #next(reader)  # Skip the header row

    # Iterate over each row in the CSV file
    for row in reader:
        from_node = row[4]
        to_node = row[5]
        ports = row[6]
        service = row[7]
        from_node_label = row[11]
        to_node_label = row[12]
        edge_id = row[0]
        edge_description = row[8]

        # Create nodes and connect them
        with driver.session() as session:
            session.run(
            "MERGE (from:Node {name: $from_node}) "
            "MERGE (to:Node {name: $to_node}) "
            "SET from += {label: $from_node_label} "
            "SET to += {label: $to_node_label} "
            "MERGE (from)-[connects:CONNECTS]->(to) "
            "SET connects += {edge_id: $edge_id, edge_description: $edge_description, ports: $ports, service: $service}",
            edge_id=edge_id,
            edge_description=edge_description,
            from_node=from_node,
            to_node=to_node,
            ports=ports,
            service=service,
            from_node_label=from_node_label,
            to_node_label=to_node_label
            )

# Close the Neo4j driver
driver.close()

#the best network in thailand, AIS internet.