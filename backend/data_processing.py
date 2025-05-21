import os

def analyze_file(file_path, data_source, database_path):
    """
    Analysiert eine einzelne konvertierte GraphML-Datei und speichert die Ergebnisse in der Datenbank.
    
    Parameter:
      file_path (str): Pfad zur konvertierten GraphML-Datei.
      data_source (str): Kennzeichnung der Datenquelle 
                         (z.B. "TopologyZoo", "SNDlib", "Rocketfuel", "CAIDA_AS").
      database_path (str): Pfad zur SQLite-Datenbank.
    
    Die Funktion wählt basierend auf data_source den passenden Analyzer aus und gibt
    das Ergebnis-Dictionary zurück.
    """
    # Optionl: Ein Output-Pfad für die JSON-Ergebnisse
    output_file = os.path.splitext(file_path)[0] + "_analysis.json"
    
    if data_source == "TopologyZoo":
        from backend.analyzers import topology_zoo_analysis
        return topology_zoo_analysis.analyze_graph(file_path, project_name="TopologyZoo", database_path=database_path)
    elif data_source == "SNDlib":
        from backend.analyzers import sndlib_analysis
        return sndlib_analysis.analyze_graph(file_path, project_name="SNDlibrary", database_path=database_path)
    elif data_source == "Rocketfuel":
        from backend.analyzers import rocketfuel_analysis
        return rocketfuel_analysis.analyze_graph(file_path, project_name="Rocketfuel", database_path=database_path)
    elif data_source == "CAIDA_AS":
        from backend.analyzers import caida_analysis
        return caida_analysis.analyze_graph(file_path, project_name="CAIDA", database_path=database_path)
    else:
        raise ValueError(f"Unbekannte Datenquelle: {data_source}")
