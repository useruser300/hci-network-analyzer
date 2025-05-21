import os
import networkx as nx

def convert_to_graphml(input_file):
    """
    Konvertiert eine CAIDA .txt-Datei in das GraphML-Format.
    Liest die Datei zeilenweise ein, überspringt Kommentare,
    extrahiert 'from_node', 'to_node' und 'relationship' und erstellt einen gerichteten Graphen.
    Speichert den Graphen als .graphml-Datei im gleichen Verzeichnis.
    """
    # Erstelle einen gerichteten Graphen
    G = nx.DiGraph()

    # Lese die Datei Zeile für Zeile
    with open(input_file, 'r') as file:
        for line in file:
            # Überspringe Kommentare
            if line.startswith('#'):
                continue
            # Versuche, die Zeile zu parsen (erwartet drei Integer-Werte)
            try:
                from_node, to_node, relationship = map(int, line.split())
            except Exception as e:
                print(f"Fehler beim Parsen der Zeile: {line.strip()} - {e}")
                continue
            # Füge die Kante zum Graphen hinzu
            G.add_edge(from_node, to_node, relationship=relationship)

    # Erstelle den Namen für die GraphML-Datei
    output_file = os.path.splitext(input_file)[0] + '.graphml'
    # Speichere den Graphen als GraphML-Datei
    nx.write_graphml(G, output_file)
    print(f"Die Konvertierung von {input_file} ist abgeschlossen. GraphML-Datei: {output_file}")
    return output_file
if __name__ == "__main__":
    print("Dieses Skript stellt die Funktion convert_to_graphml() bereit und sollte von der zentralen Pipeline aufgerufen werden.")
