import sqlite3

def connect_database(database_path):
    """
    Erstellt eine Verbindung zur SQLite-Datenbank und gibt die Verbindung zurück.
    """
    connection = sqlite3.connect(database_path)
    return connection

def initialize_database(database_path):
    """
    Initialisiert die Datenbankstruktur und erstellt erforderliche Tabellen.
    """
    connection = connect_database(database_path)
    cursor = connection.cursor()

    # Tabelle "analysis_results" erstellen oder aktualisieren
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Project_name TEXT,
            File_name TEXT,
            is_directed BOOLEAN,
            number_of_nodes INTEGER,
            number_of_edges INTEGER,
            is_connected BOOLEAN,
            is_strongly_connected BOOLEAN,
            is_weakly_connected BOOLEAN,
            node_connectivity TEXT,
            edge_connectivity TEXT,
            global_efficiency TEXT,
            local_efficiency TEXT,
            graph_center TEXT,
            degree_centrality TEXT,
            betweenness_centrality TEXT,
            closeness_centrality TEXT,
            pagerank TEXT,
            diameter TEXT,
            radius TEXT,
            periphery TEXT,
            density REAL,
            is_tree BOOLEAN,
            is_forest BOOLEAN,
            is_bipartite BOOLEAN,
            is_planar BOOLEAN,
            is_multigraph BOOLEAN
        )
    """)

    # Änderungen speichern und Verbindung schließen
    connection.commit()
    connection.close()

def save_analysis_results(database_path, results):
    """
    Speichert die Analyseergebnisse in der SQLite-Datenbank.
    """
    connection = connect_database(database_path)
    cursor = connection.cursor()

    # Daten einfügen
    cursor.execute("""
        INSERT INTO analysis_results (
            Project_name, File_name, is_directed, number_of_nodes, number_of_edges, is_connected,
            is_strongly_connected, is_weakly_connected, node_connectivity, edge_connectivity,
            global_efficiency, local_efficiency, graph_center, degree_centrality,
            betweenness_centrality, closeness_centrality, pagerank, diameter, radius,
            periphery, density, is_tree, is_forest, is_bipartite, is_planar, is_multigraph
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        results.get("project_name"),
        results.get("file_name"),
        results.get("is_directed"),
        results.get("number_of_nodes"),
        results.get("number_of_edges"),
        results.get("is_connected"),
        results.get("is_strongly_connected"),
        results.get("is_weakly_connected"),
        results.get("node_connectivity"),
        results.get("edge_connectivity"),
        results.get("global_efficiency"),
        results.get("local_efficiency"),
        results.get("graph_center"),
        results.get("degree_centrality"),
        results.get("betweenness_centrality"),
        results.get("closeness_centrality"),
        results.get("pagerank"),
        results.get("diameter"),
        results.get("radius"),
        results.get("periphery"),
        results.get("density"),
        results.get("is_tree"),
        results.get("is_forest"),
        results.get("is_bipartite"),
        results.get("is_planar"),
        results.get("is_multigraph")
    ))

    # Änderungen speichern und Verbindung schließen
    connection.commit()
    connection.close()

def query_results(database_path, query):
    """
    Führt eine benutzerdefinierte Abfrage in der Datenbank aus und gibt die Ergebnisse zurück.
    """
    connection = connect_database(database_path)
    cursor = connection.cursor()

    cursor.execute(query)
    results = cursor.fetchall()

    connection.close()
    return results

def clear_analysis_results(database_path):
    """
    Löscht alle Einträge in der Tabelle "analysis_results".
    """
    connection = connect_database(database_path)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM analysis_results")

    connection.commit()
    connection.close()

# Initialisierung der Datenbank
if __name__ == "__main__":
    database_path = "./network_analysis.db"
    initialize_database(database_path)
    print("Datenbank initialisiert.")
