import os
from backend.converters import (
    convert_xml_to_graphml,
    convert_cch_to_graphml,
    convert_to_graphml,
)

def convert_file(file_path):
    """
    Konvertiert die übergebene Datei in das GraphML-Format, falls erforderlich.
    Die Funktion bestimmt anhand der Dateiendung den passenden Konverter
    und gibt ein Tupel zurück: (konvertierter Dateipfad, data_source).

    Unterstützte Formate:
      - .graphml: Bereits im gewünschten Format. (Datenquelle: "TopologyZoo")
      - .xml: Konvertierung mittels convert_xml_to_graphml() (Datenquelle: "SNDlib")
      - .cch: Konvertierung mittels convert_cch_to_graphml() (Datenquelle: "Rocketfuel")
      - .txt: Konvertierung mittels convert_to_graphml() (Datenquelle: "CAIDA_AS")
    """
    ext = os.path.splitext(file_path)[1].lower()  # Ermittelt die Dateiendung in Kleinbuchstaben

    if ext == ".graphml":
        # Keine Konvertierung erforderlich; da es sich um TopologyZoo-Daten handelt.
        return file_path, "TopologyZoo"
    elif ext == ".xml":
        converted_file = convert_xml_to_graphml(file_path)
        return converted_file, "SNDlib"
    elif ext == ".cch":
        converted_file = convert_cch_to_graphml(file_path)
        return converted_file, "Rocketfuel"
    elif ext == ".txt":
        converted_file = convert_to_graphml(file_path)
        return converted_file, "CAIDA_AS"
    else:
        raise ValueError(f"Nicht unterstütztes Dateiformat: {ext}")
