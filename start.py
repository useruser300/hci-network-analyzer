import os
import sys
from PyQt5.QtWidgets import QApplication
from backend.database_handler import initialize_database
from frontend.gui_main import NetworkAnalysisGUI

def ensure_temp_uploads():
    """
    Überprüft, ob der Ordner 'temp_uploads/' existier und erstellt ihn, falls nicht.
    """
    temp_dir = "temp_uploads"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        print(f"'{temp_dir}' wurde erstellt.")
    else:
        print(f"'{temp_dir}' existiert bereits.")

if __name__ == "__main__":
    # Sicherstellen, dass der temp_uploads/ Ordner existiert
    ensure_temp_uploads()

    # Initialisiere die SQLite-Datenbank, bevor die GUI gestartet wird
    database_path = "./network_analysis.db"
    initialize_database(database_path)
    print("Datenbank erfolgreich initialisiert.")

    # Starte die GUI-Anwendung
    app = QApplication(sys.argv)
    gui = NetworkAnalysisGUI()  # Die GUI initialisiert alle Komponenten 
    sys.exit(app.exec_())
