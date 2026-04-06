from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "SuperSnurt12#")
NEO4J_DB   = "zac"

def fetch_graph():
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    nodes = {}
    edges = []

    with driver.session(database=NEO4J_DB) as session:
        # Fetch all nodes
        result = session.run("MATCH (n:Node) RETURN n.name AS name, n.label AS label")
        for record in result:
            name  = record["name"]
            label = record["label"] or "unknown"
            nodes[name] = {"id": name, "label": label}

        # Fetch all edges
        result = session.run(
            "MATCH (a:Node)-[r:CONNECTS]->(b:Node) "
            "RETURN a.name AS from, b.name AS to, "
            "r.edge_id AS edge_id, r.edge_description AS description, "
            "r.ports AS ports, r.service AS service"
        )
        for record in result:
            edges.append({
                "source": record["from"],
                "target": record["to"],
                "edge_id": record["edge_id"] or "",
                "description": record["description"] or "",
                "ports": record["ports"] or "",
                "service": record["service"] or "",
            })

    driver.close()

    cy_nodes = [{"data": v} for v in nodes.values()]
    cy_edges = [
        {
            "data": {
                "id": f"{e['source']}__{e['target']}__{e['edge_id']}",
                "source": e["source"],
                "target": e["target"],
                "edge_id": e["edge_id"],
                "description": e["description"],
                "ports": e["ports"],
                "service": e["service"],
            }
        }
        for e in edges
    ]
    return {"nodes": cy_nodes, "edges": cy_edges}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access log noise

    def do_GET(self):
        if self.path == "/graph":
            data = fetch_graph()
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path in ("/", "/index.html"):
            with open("cytoscape_viz.html", "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    port = 8765
    print(f"Serving at http://localhost:{port}  (press Ctrl+C to stop)")
    HTTPServer(("", port), Handler).serve_forever()
