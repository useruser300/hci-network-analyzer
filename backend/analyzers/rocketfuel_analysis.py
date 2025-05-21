import os
import networkx as nx
import json
try:
    from backend.database_handler import save_analysis_results
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from backend.database_handler import save_analysis_results

def analyze_graph(graph_file, project_name="Rocketfuel", database_path="./network_analysis.db"):
    """
    Analysiert eine einzelne GraphML-Datei aus dem Rocketfuel-Datensatz und speichert die Ergebnisse
    in der SQLite-Datenbank. Die Ergebnisse werden auch als Dictionary zurückgegeben.
    
    Parameter:
      graph_file (str): Pfad zur GraphML-Datei, die analysiert werden soll.
      project_name (str): Name des Projekts (Standard: "Rocketfuel").
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

        # Prüfen, ob der Graph gerichtet ist
        is_directed = G.is_directed()
        print("Is the graph directed?", is_directed)

        # Konnektivität
        is_connected = nx.is_connected(G)
        print("The graph is connected:", is_connected)
        node_connectivity = nx.node_connectivity(G) 
        edge_connectivity = nx.edge_connectivity(G) 
        print("The node connectivity of the graph is:", node_connectivity)
        print("The edge connectivity of the graph is:", edge_connectivity)

        # Effizienz
        global_efficiency = nx.global_efficiency(G) 
        local_efficiency = nx.local_efficiency(G)
        print("Global efficiency:", global_efficiency)
        print("Local efficiency:", local_efficiency)

        # Zusätzliche Metriken bei verbundenen Graphen
        if is_connected:
            graph_center = nx.center(G)
            diameter = nx.diameter(G)
            graph_radius = nx.radius(G)
            graph_periphery = nx.periphery(G)
            print("Center of the graph:", graph_center)
            print("Diameter:", diameter)
            print("Radius of graph:", graph_radius)
            print("Periphery of the graph:", graph_periphery)
        else:
            graph_center = diameter = graph_radius = graph_periphery = "N/A"

        # Eigenschaften
        is_tree = nx.is_tree(G) if not G.is_directed() else False
        is_forest = nx.is_forest(G) if not G.is_directed() else False
        is_bipartite = nx.is_bipartite(G)
        is_planar, _ = nx.check_planarity(G)
        is_multigraph = isinstance(G, nx.MultiGraph)
        density = nx.density(G)

        print("Is the graph a tree?", is_tree)
        print("Is the graph a forest?", is_forest)
        print("Is the graph bipartit?", is_bipartite)
        print("Is the graph planar?", is_planar)
        print("G is a Multigraph:", is_multigraph)
        print("Density:", density)

        # Ergebnisse zusammenfassen
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
            "graph_center": str(graph_center),
            "diameter": diameter,
            "radius": graph_radius,
            "periphery": str(graph_periphery),
            "density": density,
            "is_tree": is_tree,
            "is_forest": is_forest,
            "is_bipartite": is_bipartite,
            "is_planar": is_planar,
            "is_multigraph": is_multigraph
        }

        # Ergebnisse in  Datenbank speichern
        save_analysis_results(database_path, results)

        return results

    except Exception as e:
        print(f"Fehler bei der Analyse von {graph_file}: {e}")
        return {"project_name": project_name, "file_name": os.path.basename(graph_file), "error": str(e)}
