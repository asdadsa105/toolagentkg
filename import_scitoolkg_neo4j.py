"""Import SciToolAgent's persisted SimpleGraphStore into Neo4j for visualization.

This creates a *copy* of the graph in Neo4j; it does not modify SciToolAgent's
original graph_store.json or BGE-M3 index_store.json.

Examples (from SciToolAgent project root):
    pip install neo4j
    python import_scitoolkg_neo4j.py --dry-run
    python import_scitoolkg_neo4j.py
    python import_scitoolkg_neo4j.py --graph KG/storage_graph_bge_m3/graph_store.json

Environment variables:
    NEO4J_URI        default bolt://localhost:7687
    NEO4J_USER       default neo4j
    NEO4J_PASSWORD   prompt interactively if omitted
    NEO4J_DATABASE   default neo4j
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from getpass import getpass
from pathlib import Path

RELATION_TYPES = {
    "is a": "IS_A",
    "has the functionality that": "HAS_FUNCTIONALITY",
    "inputs": "INPUTS",
    "outputs": "OUTPUTS",
    "is sourced from": "SOURCED_FROM",
    "does not need": "DOES_NOT_NEED",
    "needs": "NEEDS",
    "is the input of": "IS_INPUT_OF",
    "is the output of": "IS_OUTPUT_OF",
}


def read_triples(graph_path: Path):
    with graph_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    graph = data["graph_dict"]
    triples = set()
    for source, relations in graph.items():
        for relation, target in relations:
            if relation not in RELATION_TYPES:
                raise ValueError(f"Unknown relation type {relation!r}; add it to RELATION_TYPES first")
            triples.add((source, relation, target))
    nodes = {s for s, _, _ in triples} | {t for _, _, t in triples}
    return triples, nodes


def main():
    parser = argparse.ArgumentParser(description="Import SciToolKG into Neo4j")
    parser.add_argument("--graph", default="KG/storage_graph_bge_m3/graph_store.json",
                        help="path to graph_store.json, relative to current working directory")
    parser.add_argument("--batch-size", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true", help="validate input without connecting to Neo4j")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be >= 1")
    graph_path = Path(args.graph)
    if not graph_path.is_file():
        parser.error(f"Cannot find {graph_path.resolve()}")

    triples, nodes = read_triples(graph_path)
    counts = Counter(rel for _, rel, _ in triples)
    print(f"Graph file: {graph_path.resolve()}")
    print(f"Unique nodes: {len(nodes)} | unique relationships: {len(triples)}")
    print("Relationship types:", dict(sorted(counts.items())))
    if args.dry_run:
        print("Dry run completed. Neo4j was not modified.")
        return

    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise SystemExit("Install the Neo4j Python driver: python -m pip install neo4j") from exc

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD") or getpass("Neo4j password: ")
    db_name = os.getenv("NEO4J_DATABASE", "neo4j")
    grouped = defaultdict(list)
    for src, relation, dst in sorted(triples):
        grouped[relation].append({"source": src, "target": dst})

    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        driver.verify_connectivity()
        print(f"Connected to {uri}, database {db_name}")
        with driver.session(database=db_name) as session:
            session.run(
                "CREATE CONSTRAINT scitool_entity_name IF NOT EXISTS "
                "FOR (n:Entity) REQUIRE n.name IS UNIQUE"
            ).consume()
            for relation, rows in grouped.items():
                rel_type = RELATION_TYPES[relation]  # only literal types from trusted allowlist
                query = (
                    "UNWIND $rows AS item\n"
                    "MERGE (src:Entity {name: item.source})\n"
                    "MERGE (dst:Entity {name: item.target})\n"
                    f"MERGE (src)-[r:{rel_type}]->(dst)\n"
                    "SET r.original_relation = $original_relation"
                )
                for i in range(0, len(rows), args.batch_size):
                    session.run(query, rows=rows[i:i + args.batch_size],
                                original_relation=relation).consume()
                print(f"Imported {relation}: {len(rows)} relationships")

            # Add convenient extra labels while retaining one common :Entity identity.
            labeling_queries = [
                "MATCH (t:Entity)-[:IS_A]->(c:Entity) SET t:Tool, c:Category",
                "MATCH (t:Tool)-[:HAS_FUNCTIONALITY]->(f:Entity) SET f:Functionality",
                "MATCH (t:Tool)-[:INPUTS|OUTPUTS]->(d:Entity) SET d:DataType",
                "MATCH (t:Tool)-[:SOURCED_FROM]->(s:Entity) SET s:Source",
            ]
            for query in labeling_queries:
                session.run(query).consume()

            counts = session.run(
                "MATCH (n:Entity) WITH count(n) AS nodes "
                "MATCH ()-[r]->() RETURN nodes, count(r) AS relationships"
            ).single()
            print(f"Neo4j now contains {counts['nodes']} Entity nodes, "
                  f"{counts['relationships']} relationships (may include pre-existing graph data).")
    print("Finished. Open Neo4j Query / Browser and run:")
    print("MATCH p=(t:Tool {name:'NameToSMILES'})--(n) RETURN p LIMIT 30;")


if __name__ == "__main__":
    main()
