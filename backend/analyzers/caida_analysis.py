import os
import networkx as nx
import json
try:
    from backend.database_handler import save_analysis_results
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from backend.database_handler import save_analysis_results

def analyze_graph(graph_file, project_name="CAIDA", database_path="./network_analysis.db"):
    """
    Analysiert eine einzelne GraphML-Datei aus dem CAIDA-Datensatz und speichert die Ergebnisse
    in der SQLite-Datenbank. Die Ergebnisse werden auch als Dictionary zurückgegeben.
    
    Parameter:
      graph_file (str): Pfad zur GraphML-Datei, die analysiert werden soll.
      project_name (str): Name des Projekts oder der Datenquelle (Standard: "CAIDA").
      database_path (str): Pfad zur SQLite-Datenbank.
      
    Rückgabe:
      dict: Ein Dictionary mit den berechneten Netzwerkmetriken.
    """
    try:
        # Graph einlesen
        G = nx.read_graphml(graph_file)

        

        # Basis-Metriken
        number_of_nodes = G.number_of_nodes()
        number_of_edges = G.number_of_edges()
        print("Number of nodes:", number_of_nodes)
        print("Number of edges:", number_of_edges)


        # Prüfe, ob der Graph gerichtet ist
        is_directed = G.is_directed()
        print("Is the graph directed?", is_directed)

        # Konnektivitäts-Metriken
        is_strongly_connected = nx.is_strongly_connected(G)
        is_weakly_connected = nx.is_weakly_connected(G)
        print("The graph is strongly connected:", is_strongly_connected)
        print("The graph is weakly connected:", is_weakly_connected)

        node_connectivity = nx.node_connectivity(G) 
        edge_connectivity = nx.edge_connectivity(G) 
        print("Node connectivity:", node_connectivity)
        print("Edge connectivity:", edge_connectivity)

        # Multigraph-Check und Planarität
        is_multigraph = isinstance(G, nx.MultiDiGraph)
        is_planar, _ = nx.check_planarity(G)
        print("G is a MultiDiGraph:", is_multigraph)
        print("Is the graph planar:", is_planar)

        # Strukturmetriken für stark verbundene Graphen
        if is_strongly_connected:
            is_tree = nx.is_tree(G)
            is_forest = nx.is_forest(G)
            diameter = nx.diameter(G)
            graph_radius = nx.radius(G)
            is_bipartite = nx.is_bipartite(G)
            print("Is the graph a tree?", is_tree)
            print("Is the graph a forest?", is_forest)
            print("Diameter:", diameter)
            print("Radius:", graph_radius)
            print("Is the graph bipartite?", is_bipartite)
        else:
            is_tree = is_forest = diameter = graph_radius = is_bipartite = "N/A"

        # Dichte
        density = nx.density(G)
        print("Density:", density)

        # Ergebnisse zusammenfassen
        results = {
            "project_name": project_name,
            "file_name": os.path.basename(graph_file),
            "is_directed": is_directed,
            "number_of_nodes": number_of_nodes,
            "number_of_edges": number_of_edges,
            "is_strongly_connected": is_strongly_connected,
            "is_weakly_connected": is_weakly_connected,
            "node_connectivity": node_connectivity,
            "edge_connectivity": edge_connectivity,
            "is_multigraph": is_multigraph,
            "is_planar": is_planar,
            "is_tree": is_tree,
            "is_forest": is_forest,
            "diameter": diameter,
            "radius": graph_radius,
            "is_bipartite": is_bipartite,
            "density": density,
        }

        # Speichere  Ergebnisse in der SQLite-Datenbank
        save_analysis_results(database_path, results)

        return results

    except Exception as e:
        print(f"Fehler bei der Analyse von {graph_file}: {e}")
        return {"project_name": project_name, "file_name": os.path.basename(graph_file), "error": str(e)}
