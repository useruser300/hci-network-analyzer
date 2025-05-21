import os
from backend.file_converter import convert_file
from backend.data_processing import analyze_file  # angepasste Funktion, die eine einzelne Datei verarbeitet
from backend.database_handler import initialize_database

# Pfad zur SQLite-Datenbank
database_path = "./network_analysis.db"

def process_files(file_paths):
    """
    Verarbeitet eine Liste von Dateien:
      1. Konvertiert die Datei ins GraphML-Format (falls erforderlich) und erhält die Datenquelle.
      2. Analysiert die konvertierte Datei, wobei der richtige Analyzer basierend auf der Datenquelle gewählt wird.
      3. Die Analyseergebnisse werden in der SQLite-Datenbank gespeichert.
      
    Parameter:
      file_paths (list): Liste der Pfade zu den hochgeladenen Dateien (aus temp_uploads/).
      
    Rückgabe:
      list: Eine Liste mit den Ergebnis-Dictionaries aller verarbeiteten Dateien.
    """
    results = []
    for file_path in file_paths:
        try:
            # Schritt 1: Konvertierung
            converted_file, data_source = convert_file(file_path)
            print(f"Datei konvertiert: {file_path} -> {converted_file} (Datenquelle: {data_source})")
        except Exception as e:
            print(f"Fehler bei der Konvertierung von {file_path}: {e}")
            continue

        try:
            # Schritt 2: Analyse
            analysis_results = analyze_file(converted_file, data_source, database_path)
            results.append(analysis_results)
            print(f"Analyse abgeschlossen für {converted_file}.")
        except Exception as e:
            print(f"Fehler bei der Analyse von {converted_file}: {e}")
            continue

    return results

if __name__ == "__main__":
    # Testblock: Initialisiere die Datenbank und verarbeite alle Dateien in temp_uploads/
    initialize_database(database_path)
    print("Datenbank initialisiert.")

    temp_dir = "temp_uploads"
    if os.path.exists(temp_dir):
        # Sammle alle Dateien im temp_uploads-Verzeichnis
        file_paths = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
        results = process_files(file_paths)
        print("Verarbeitung abgeschlossen.")
        print("Ergebnisse:", results)
    else:
        print("Verzeichnis temp_uploads/ nicht gefunden.")
