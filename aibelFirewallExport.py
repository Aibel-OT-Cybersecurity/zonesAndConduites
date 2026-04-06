from neo4j import GraphDatabase
# Remember to: pip install neo4j
import csv
import sys

# Connect to Neo4j database.
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "TesterGraph"))

output_file = "ZaC-export.csv"
if len(sys.argv) > 1:
    output_file = sys.argv[1]

# Query all CONNECTS relationships with their source and target nodes
query = (
    "MATCH (from:Node)-[r:CONNECTS]->(to:Node) "
    "RETURN r.edge_id AS edge_id, "
    "       r.conduit_name AS conduit_name, "
    "       from.zone AS from_zone, "
    "       to.zone AS to_zone, "
    "       from.name AS from_node, "
    "       to.name AS to_node, "
    "       r.ports AS ports, "
    "       r.service AS service, "
    "       r.edge_description AS edge_description, "
    "       r.notes AS notes, "
    "       r.notes2 AS notes2, "
    "       from.label AS from_label, "
    "       to.label AS to_label"
)

rows = []
with driver.session() as session:
    result = session.run(query)
    for record in result:
        # Match the original CSV column layout:
        # 0:edge_id, 1:conduit_name, 2:from_zone, 3:to_zone,
        # 4:from_node, 5:to_node, 6:ports, 7:service,
        # 8:edge_description, 9:notes, 10:notes2,
        # 11:from_label, 12:to_label
        row = [
            record["edge_id"] or "",          # 0
            record["conduit_name"] or "",      # 1
            record["from_zone"] or "",         # 2
            record["to_zone"] or "",           # 3
            record["from_node"] or "",         # 4
            record["to_node"] or "",           # 5
            record["ports"] or "",             # 6
            record["service"] or "",           # 7
            record["edge_description"] or "",  # 8
            record["notes"] or "",             # 9
            record["notes2"] or "",            # 10
            record["from_label"] or "",        # 11
            record["to_label"] or "",          # 12
        ]
        rows.append(row)

driver.close()

# Sort by edge_id for consistent output
rows.sort(key=lambda r: r[0])

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(rows)

print(f"Exported {len(rows)} conduits to {output_file}")
