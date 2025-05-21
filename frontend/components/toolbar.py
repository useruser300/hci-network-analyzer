import os
import json
import datetime
from PyQt5.QtWidgets import QToolBar, QAction, QFileDialog, QMessageBox, QMenu, QToolButton
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QSize

from backend.export_handler import fetch_dataset


class Toolbar(QToolBar):
    def __init__(self, parent):
        super().__init__("Hauptmenü")
        self.parent = parent

        self.setStyleSheet("""
            /* Abstand zwischen den Buttons */
            QToolBar { spacing: 8px; }

            /* Größe, Padding und Schrift */
            QToolButton {
                min-width: 25px;
                min-height: 25px;
                font-size: 12pt;
                padding: 4px;
            }
        """)

        
        # Bericht generieren  sollte mit pdf nicht vergessen alles (JSON speichern) ersetz das jetzt 
        self.report_action = QAction("📊 Bericht generieren", self)
        self.report_action.triggered.connect(self.generate_report)
        self.addAction(self.report_action)

        # Bericht als JSON speichern
        self.export_json_action = QAction("📊 JSON speichern", self)
        self.export_json_action.triggered.connect(self.export_as_json)
        self.addAction(self.export_json_action)

        # Bilder speichern 
        self.export_images_action = QAction("🖼 Bilder speichern", self)
        self.export_images_action.triggered.connect(self.export_images)
        self.addAction(self.export_images_action)

        # Theme-Auswahl 
        self.theme_action = QAction("🎨 Theme", self)
        theme_menu = QMenu()
        dark_action = QAction("Dark", self)
        light_action = QAction("Light", self)
        dark_action.triggered.connect(self.apply_dark_mode)
        light_action.triggered.connect(self.apply_light_mode)
        theme_menu.addAction(dark_action)
        theme_menu.addAction(light_action)
        self.theme_action.setMenu(theme_menu)
        self.addAction(self.theme_action)

        #  Popup-Modus 
        theme_button = self.widgetForAction(self.theme_action)
        if isinstance(theme_button, QToolButton):
            theme_button.setPopupMode(QToolButton.InstantPopup)

        # Hilfe anzeigen
        self.help_action = QAction("❓ Hilfe", self)
        self.help_action.triggered.connect(self.show_help)
        self.addAction(self.help_action)
        #soll gemacht 
    def generate_report(self):
        """Erstellt den Bericht und speichert ihn standardmäßig als JSON."""
        self.export_as_json()
        QMessageBox.information(self, "Erfolg", "Bericht wurde erfolgreich generiert!")

    def export_as_json(self):
        # Wähle Ordner zum Speichern der JSON-Dateien
        folder = QFileDialog.getExistingDirectory(self, "Wählen Sie einen Ordner zum Speichern der JSON-Dateien")
        if not folder:
            return

        try:
            # SQL-Abfrage: Alle Datensätze aus der Tabelle holen
            query = "SELECT * FROM analysis_results"
            params = []
            data = fetch_dataset(query, params)

            # Entferne den Schlüssel "id" 
            for record in data:
                record.pop("id", None)

            # Gruppierund die Datensätze nach 'Project_name'
            datasets = {}
            for record in data:
                project = record.get("Project_name") or "unknown"
                if project not in datasets:
                    datasets[project] = []
                datasets[project].append(record)

            # Erzeuget einen Zeitstempel in den Dateinamen eingefügt 
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Für jeden Datensatz-Typ wird eine separate JSON-Datei erstellt,
            # wobei der Zeitstempel im Dateinamen enthalten ist.
            for project, records in datasets.items():
                filename = os.path.join(folder, f"{project}_{timestamp}.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(records, f, indent=4)

            QMessageBox.information(self, "Erfolg", "Alle Datensätze wurden erfolgreich exportiert!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Export: {str(e)}")






    def export_images(self):
        directory = QFileDialog.getExistingDirectory(self, "Verzeichnis zum Speichern auswählen")
        if not directory:
            return

        saved_images = 0
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Exportiere Bilder aus dem DatasetAnalysisTab (auch Zeitstempel)
        if hasattr(self.parent, "dataset_tab"):
            dataset_tab = self.parent.dataset_tab
            if hasattr(dataset_tab, "get_generated_images"):
                images = dataset_tab.get_generated_images()
                if images:
                    for idx, img in enumerate(images):
                        if isinstance(img, QImage):
                            file_path = os.path.join(directory, f"dataset_image_{idx+1}_{timestamp}.png")
                            img.save(file_path, "PNG")
                            saved_images += 1

        # Exportiere das Visualisierungsbild aus dem SingleGraphTab
        if hasattr(self.parent, "single_graph_tab"):
            sg_tab = self.parent.single_graph_tab
            if hasattr(sg_tab, "visualization_section"):
                viz_section = sg_tab.visualization_section
                if hasattr(viz_section, "get_generated_image"):
                    viz_image = viz_section.get_generated_image()
                    if isinstance(viz_image, QImage):
                        # Verwende den geladenen Dateinamen, wenn vorhanden, sonst den Zeitstempel
                        base_name = getattr(viz_section, "loaded_file", None)
                        if base_name:
                            file_name = f"{base_name}.png"
                        else:
                            file_name = f"visualization_{timestamp}.png"
                        file_path = os.path.join(directory, file_name)
                        viz_image.save(file_path, "PNG")
                        saved_images += 1

        if saved_images > 0:
            QMessageBox.information(self, "Erfolg", f"{saved_images} Bild(er) erfolgreich gespeichert!")
        else:
            QMessageBox.warning(self, "Fehler", "Keine Bilder zum Speichern gefunden!")


    def apply_dark_mode(self):
        self.parent.apply_theme("dark")

    def apply_light_mode(self):
        self.parent.apply_theme("light")

    def show_help(self):
        help_text = (
            "🛠️ Bedienungsschritte – So nutzt du das Tool\n\n"
            "🔹 Schritt 1: Start & Übersicht\n"
            "- Linker Bereich: Datei-Upload\n"
            "- Rechter Bereich: Einzelgraph- und Datensatz-Analyse\n"
            "- Oben: Toolbar mit Export- & Hilfefunktionen\n\n"
            "🔹 Schritt 2: Netzwerkdateien hochladen\n"
            "- Klicke auf 'Datei hochladen' und wähle .graphml, .xml, .txt, .cch\n\n"
            "🔹 Schritt 3: Analyse starten\n"
            "- Klicke auf 'Analyse starten' → Ergebnisse erscheinen in den Tabs\n\n"
            "🔹 Schritt 4: Einzelgraph-Analyse\n"
            "- Filter, Metrikauswahl, Schnellsuche\n"
            "- Spalten & Zeilen lassen sich manuell in der Größe anpassen\n"
            "- Doppelklick zeigt die Visualisierung\n\n"
            "🔹 Schritt 5: Visualisierung\n"
            "- Statische Anzeige (Matplotlib), QSplitter für Größenanpassung\n\n"
            "🔹 Schritt 6: Datensatz-Analyse\n"
            "- Wähle Quelle, lade Analyse, sieh Diagramme und Bilder\n"
        )
        QMessageBox.information(self, "Hilfe", help_text)
