import sqlite3
import json

# Definiere das feste Schema (entsprechend der DB-Spalten)
ALL_COLUMNS = [
    "Project_name", "File_name", "is_directed",
    "number_of_nodes", "number_of_edges",
    "is_connected", "is_strongly_connected", "is_weakly_connected",
    "node_connectivity", "edge_connectivity",
    "global_efficiency", "local_efficiency",
    "graph_center", "degree_centrality", "betweenness_centrality",
    "closeness_centrality", "pagerank",
    "diameter", "radius", "periphery", "density",
    "is_tree", "is_forest", "is_bipartite", "is_planar", "is_multigraph"
]

DATABASE_PATH = "./network_analysis.db"

def fetch_dataset(query, params):
    """
    Führt die gegebene SQL-Abfrage aus und gibt eine Liste von Dictionaries zurück,
    die dem festen Schema ALL_COLUMNS entsprechen. Fehlende Werte werden als None gesetzt.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    # Holet Spaltennamen aus der Abfrage (können anders ALL_COLUMNS sein)
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    
    data = []
    for row in rows:
        # Erstelle ein Dictionary aus dem Abfrageergebnis
        record = dict(zip(columns, row))
        # Stelle sicher, dass alle Felder im Schema vorhanden sind
        for key in ALL_COLUMNS:
            if key not in record:
                record[key] = None
        data.append(record)
    return data

def export_dataset_to_json(query, params, filename):
    """
    Exportiert den kompletten Datensatz, der mit der Abfrage geliefert wird, in eine JSON-Datei.
    """
    data = fetch_dataset(query, params)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def export_single_record_to_json(record, filename):
    """
    Exportiert einen einzelnen Datensatz (als Dictionary) in eine JSON-Datei.
    Stellt sicher, dass alle Felder des festen Schemas vorhanden sind.
    """
    for key in ALL_COLUMNS:
        if key not in record:
            record[key] = None
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=4)
