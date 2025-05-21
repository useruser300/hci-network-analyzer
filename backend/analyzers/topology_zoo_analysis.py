import os
import networkx as nx
import json
try:
    from backend.database_handler import save_analysis_results
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from backend.database_handler import save_analysis_results

def analyze_graph(graph_file, project_name="Topology Zoo", database_path="./network_analysis.db"):
    """
    Analysiert eine einzelne GraphML-Datei und speichert die Ergebnisse in der SQLite-Datenbank.
    Zusätzlich wird ein Ergebnis-Dictionary erzeugt, das später auch für den JSON-Export genutzt werden kann.
    
    Parameter:
      graph_file (str): Pfad zur GraphML-Datei, die analysiert werden soll.
      project_name (str): Name des Projekts oder der Datenquelle (Default: "Topology Zoo").
      database_path (str): Pfad zur SQLite-Datenbank.
    
    Rückgabe:
      dict: Ein Dictionary mit den berechneten Netzwerkmetriken.
    """
    try:
        # Lese den Graph aus der GraphML-Datei
        G = nx.read_graphml(graph_file)
        print(f"Analysiere Datei: {graph_file}")
        
        # Knoten und Kanten
        number_of_nodes = G.number_of_nodes()
        number_of_edges = G.number_of_edges()
        print("Number of nodes:", number_of_nodes)
        print("Number of edges:", number_of_edges)


        # Prüfen, ob der Graph gerichtet ist
        is_directed = G.is_directed()
        print("Is the graph directed?", is_directed)
        
        # Konnektivität (nur für ungerichtete Graphen)
        is_connected = nx.is_connected(G) 
        print("The graph is connected:", is_connected)
        node_connectivity = nx.node_connectivity(G) 
        edge_connectivity = nx.edge_connectivity(G) 
        
        # Effizienz
        global_efficiency = nx.global_efficiency(G) 
        local_efficiency = nx.local_efficiency(G)
        
        # Zentralitätsmetriken
        graph_center = nx.center(G) 
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        closeness_centrality = nx.closeness_centrality(G)
        
        # PageRank
        pagerank = nx.pagerank(G)
        
        # Graphstruktur
        diameter = nx.diameter(G) 
        graph_radius = nx.radius(G) 
        graph_periphery = nx.periphery(G) 
        
        # Baum- und Waldstruktur (nur für ungerichtete Graphen)
        is_tree = nx.is_tree(G) 
        is_forest = nx.is_forest(G) 
        
        # Weitere Eigenschaften
        is_bipartite = nx.is_bipartite(G)
        is_planar, embedding = nx.check_planarity(G)
        is_multigraph = isinstance(G, nx.MultiGraph)
        density = nx.density(G)
        
        # Ergebnisse zusammenstellen
        results = {
            "project_name": project_name,
            "file_name": os.path.basename(graph_file),
            "is_directed": is_directed,
            "number_of_nodes": number_of_nodes,
            "number_of_edges": number_of_edges,
            "is_connected": is_connected,
            "node_connectivity": node_connectivity,
            "edge_connectivity": edge_connectivity,
            "global_efficiency": global_efficiency,
            "local_efficiency": local_efficiency,
            "graph_center": json.dumps(graph_center),
            "degree_centrality": json.dumps(degree_centrality),
            "betweenness_centrality": json.dumps(betweenness_centrality),
            "closeness_centrality": json.dumps(closeness_centrality),
            "pagerank": json.dumps(pagerank),
            "diameter": diameter,
            "radius": graph_radius,
            "periphery": json.dumps(graph_periphery),
            "density": density,
            "is_tree": is_tree,
            "is_forest": is_forest,
            "is_bipartite": is_bipartite,
            "is_planar": is_planar,
            "is_multigraph": is_multigraph
        }
        
        # Speichere Ergebnisse in SQLite-Datenbank
        save_analysis_results(database_path, results)
        
        return results

    except Exception as e:
        print(f"Fehler bei der Analyse von {graph_file}: {e}")
        return {"project_name": project_name, "file_name": os.path.basename(graph_file), "error": str(e)}
