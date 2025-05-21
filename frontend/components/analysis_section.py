# analysis_section.py

import os
import sqlite3
import datetime
import json
import csv

from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton,
    QLineEdit, QGroupBox, QFormLayout, QLabel, QComboBox, QSpinBox, QSlider,
    QCheckBox, QHBoxLayout, QToolButton, QMenu, QAction, QAbstractItemView, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from backend.export_handler import export_single_record_to_json
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QHeaderView


# Datenbankpfad

DATABASE_PATH = "./network_analysis.db"


# Worker-class für asynchrone DB-Abfragen

class DatabaseWorker(QThread):
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, query, params=None, parent=None):
        super().__init__(parent)
        self.query = query
        self.params = params if params is not None else []
        
    def run(self):
        try:
            print("DatabaseWorker startet...")
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            print("Executing query:", self.query)
            print("With parameters:", self.params)
            cursor.execute(self.query, self.params)
            results = cursor.fetchall()
            print("Query returned:", results)
            conn.close()
            self.results_ready.emit(results)
        except Exception as e:
            print("Fehler in DatabaseWorker:", e)
            self.error_occurred.emit(str(e))


# AnalysisSection-Klasse

class AnalysisSection(QWidget):
    """
    Zeigt eine Tabelle mit allen Metriken aus der DB, ermöglicht Filterung
    und bietet eine Dropdown-Checkbox-Liste für die Metrikauswahl.
    Bestimmte Spalten (u. a. File_name) sind nicht abwählbar, damit
    die Doppelklick-Funktion stets funktioniert.

    Außerdem gibt es einen Button, der das erweiterte Filterpanel ein-/ausblendet.
    """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        
        #  Alle Spalten
        
        self.all_columns = [
            "Project_name", "File_name", "is_directed",
            "number_of_nodes", "number_of_edges",
            "is_connected", "is_strongly_connected", "is_weakly_connected",
            "node_connectivity", "edge_connectivity",
            "global_efficiency", "local_efficiency",
            "graph_center", "degree_centrality", "betweenness_centrality",
            "closeness_centrality", "pagerank",
            "diameter", "radius", "periphery", "density",
            "is_tree", "is_forest", "is_bipartite", "is_planar", "is_multigraph"
        ]

        # Spalten, die NICHT abwählbar sind
        self.forced_columns = {
            "Project_name", "File_name", "number_of_nodes", "number_of_edges"
        }

        # Standardspalten: forced_columns plus weitere
        self.default_columns = self.forced_columns.union({
            "graph_center", "periphery"
        })
        self.metric_tooltips = {
            "project_name": "Name des analysierten Projekts oder Datensatzes",
            "file_name": "Name der analysierten Datei",
            "is_directed": "Gibt an, ob der Graph gerichtet ist (True = gerichtete Kanten)",
            "number_of_nodes": "Anzahl der Knoten im Graph",
            "number_of_edges": "Anzahl der Kanten im Graph",
            "is_connected": "True, wenn der ungerichtete Graph vollständig zusammenhängend ist",
            "is_strongly_connected": "True, wenn im gerichteten Graph jeder Knoten von jedem anderen aus erreichbar ist",
            "is_weakly_connected": "True, wenn der gerichtete Graph nach Ignorieren der Richtungen verbunden ist",
            "node_connectivity": "Minimale Anzahl an Knoten, deren Entfernung den Graph in isolierte Teile trennt",
            "edge_connectivity": "Minimale Anzahl an Kanten, deren Entfernung den Graph trennt",
            "global_efficiency": "Maß für den mittleren Informationsfluss zwischen allen Knoten",
            "local_efficiency": "Wie effizient Nachbarn bei Knotenausfall miteinander kommunizieren",
            "graph_center": "Knoten mit der geringsten maximalen Entfernung zu allen anderen",
            "degree_centrality": "Anzahl der direkten Verbindungen eines Knotens",
            "betweenness_centrality": "Wie oft ein Knoten auf kürzesten Pfaden liegt (Vermittlerrolle)",
            "closeness_centrality": "Durchschnittliche Entfernung eines Knotens zu allen anderen",
            "pagerank": "Wichtigkeit eines Knotens basierend auf eingehenden Verbindungen",
            "diameter": "Größte kürzeste Entfernung zwischen zwei beliebigen Knoten",
            "radius": "Kleinster maximaler Abstand eines Knotens im Graph",
            "periphery": "Knoten mit größter Entfernung zu anderen (höchste Exzentrizität)",
            "density": "Verhältnis tatsächlicher Kanten zur maximal möglichen Anzahl",
            "is_tree": "True, wenn der Graph ein zusammenhängender, zyklenfreier Baum ist",
            "is_forest": "True, wenn der Graph aus mehreren getrennten Bäumen besteht",
            "is_bipartite": "True, wenn Knoten in zwei Gruppen ohne interne Verbindungen teilbar sind",
            "is_planar": "True, wenn der Graph ohne überlappende Kanten darstellbar ist",
            "is_multigraph": "True, wenn mehrere Kanten zwischen denselben Knoten existieren",
        }

        # Aktuell gewählte Spalten
        self.selected_columns = set(self.default_columns)

        
        # GUI-Aufbau
        
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Schnellsuche
        fast_search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("fastSearchInput")
        self.search_input.setPlaceholderText("🔍 Schnellsuche: Projekt-/Dateiname...")
        self.search_input.textChanged.connect(self.load_analysis_results)
        fast_search_layout.addWidget(self.search_input)

        self.fast_search_button = QPushButton("🔍")
        self.fast_search_button.setObjectName("fastSearchButton")
        self.fast_search_button.clicked.connect(self.load_analysis_results)
        fast_search_layout.addWidget(self.fast_search_button)

        main_layout.addLayout(fast_search_layout)

        # Metrik-Auswahl Dropdown + Reset
        metric_layout = QHBoxLayout()

        self.metric_button = QToolButton()
        self.metric_button.setText("Metriken wählen")
        self.metric_button.setObjectName("metricButton")

        self.metric_button.setPopupMode(QToolButton.InstantPopup)
        self.metric_menu = QMenu(self)
        self.metric_button.setMenu(self.metric_menu)
        metric_layout.addWidget(self.metric_button)

        self.reset_button = QPushButton("Zurücksetzen auf Standard-Metriken")
        self.reset_button.setObjectName("resetMetricsButton")
        self.reset_button.clicked.connect(self.on_reset_metrics)
        metric_layout.addWidget(self.reset_button)

        main_layout.addLayout(metric_layout)

        # Dropdown-Checkboxen 
        self.build_metric_menu()

        #  Button zum Ein-/Ausblenden fur erweiterte Filterpanel
        self.toggle_advanced_button = QPushButton("Erweiterte Filter einblenden")
        self.toggle_advanced_button.setObjectName("toggleAdvancedButton")
        self.toggle_advanced_button.clicked.connect(self.toggle_advanced_filters)
        main_layout.addWidget(self.toggle_advanced_button)

        # Erweiterte Filtergruppe
        self.advanced_filters_visible = False
        self.advanced_filter_group = QGroupBox("Erweiterte Filter")
        self.advanced_filter_group.setVisible(self.advanced_filters_visible)
        adv_layout = QFormLayout(self.advanced_filter_group)

        # Knotenfilter
        node_size_layout = QHBoxLayout()
        self.node_min_spin = QSpinBox()
        self.node_min_spin.setMinimum(0)
        self.node_min_spin.setMaximum(100000)
        self.node_min_spin.setPrefix("Min: ")
        self.node_max_spin = QSpinBox()
        self.node_max_spin.setMinimum(0)
        self.node_max_spin.setMaximum(100000)
        self.node_max_spin.setPrefix("Max: ")
        node_size_layout.addWidget(self.node_min_spin)
        node_size_layout.addWidget(self.node_max_spin)
        adv_layout.addRow(QLabel("Knotenzahl:"), node_size_layout)

        # Kantenfilter
        edge_size_layout = QHBoxLayout()
        self.edge_min_spin = QSpinBox()
        self.edge_min_spin.setMinimum(0)
        self.edge_min_spin.setMaximum(1000000)
        self.edge_min_spin.setPrefix("Min: ")
        self.edge_max_spin = QSpinBox()
        self.edge_max_spin.setMinimum(0)
        self.edge_max_spin.setMaximum(1000000)
        self.edge_max_spin.setPrefix("Max: ")
        edge_size_layout.addWidget(self.edge_min_spin)
        edge_size_layout.addWidget(self.edge_max_spin)
        adv_layout.addRow(QLabel("Kantenanzahl:"), edge_size_layout)

        # Gerichtete Graphen
        self.directed_checkbox = QCheckBox("Nur gerichtete Netzwerke")
        adv_layout.addRow(QLabel("Richtung:"), self.directed_checkbox)

        # Verbindungstyp
        self.connection_type_combo = QComboBox()
        self.connection_type_combo.addItems(["Alle", "Stark", "Schwach", "Kein"])
        adv_layout.addRow(QLabel("Verbindungstyp:"), self.connection_type_combo)

        # Dichte
        density_layout = QHBoxLayout()
        self.density_slider = QSlider(Qt.Horizontal)
        self.density_slider.setMinimum(0)
        self.density_slider.setMaximum(100)
        self.density_slider.setValue(0)
        self.density_slider.setTickInterval(10)
        self.density_slider.setTickPosition(QSlider.TicksBelow)
        self.density_value_label = QLabel("0.00")
        self.density_slider.valueChanged.connect(
            lambda val: self.density_value_label.setText(f"{val/100:.2f}")
        )
        density_layout.addWidget(self.density_slider)
        density_layout.addWidget(self.density_value_label)
        adv_layout.addRow(QLabel("Dichte (≥):"), density_layout)

        # PageRank
        pr_layout = QHBoxLayout()
        self.pagerank_slider = QSlider(Qt.Horizontal)
        self.pagerank_slider.setMinimum(0)
        self.pagerank_slider.setMaximum(100)
        self.pagerank_slider.setValue(0)
        self.pagerank_slider.setTickInterval(10)
        self.pagerank_slider.setTickPosition(QSlider.TicksBelow)
        self.pagerank_value_label = QLabel("0.00")
        self.pagerank_slider.valueChanged.connect(
            lambda val: self.pagerank_value_label.setText(f"{val/100:.2f}")
        )
        pr_layout.addWidget(self.pagerank_slider)
        pr_layout.addWidget(self.pagerank_value_label)
        adv_layout.addRow(QLabel("PageRank (≥):"), pr_layout)

        # Netzwerkstruktur
        ns_layout = QHBoxLayout()
        self.tree_checkbox = QCheckBox("Bäume")
        self.forest_checkbox = QCheckBox("Wälder")
        self.bipartite_checkbox = QCheckBox("Bipartit")
        self.planar_checkbox = QCheckBox("Planar")
        self.multigraph_checkbox = QCheckBox("Multigraph")
        ns_layout.addWidget(self.tree_checkbox)
        ns_layout.addWidget(self.forest_checkbox)
        ns_layout.addWidget(self.bipartite_checkbox)
        ns_layout.addWidget(self.planar_checkbox)
        ns_layout.addWidget(self.multigraph_checkbox)
        adv_layout.addRow(QLabel("Struktur:"), ns_layout)

        # Sortieren nach
        self.sort_by_combo = QComboBox()
        self.sort_by_combo.addItems(["Größe", "Kanten", "Dichte", "Zentralität"])
        self.sort_by_combo.currentIndexChanged.connect(self.load_analysis_results)
        adv_layout.addRow(QLabel("Sortieren nach:"), self.sort_by_combo)

        # Filter-Buttons
        filter_buttons_layout = QHBoxLayout()
        self.advanced_search_button = QPushButton("🔍 Suche starten")
        self.advanced_search_button.clicked.connect(self.load_analysis_results)
        self.reset_filters_button = QPushButton("🔄 Zurücksetzen")
        self.reset_filters_button.clicked.connect(self.reset_advanced_filters)
        filter_buttons_layout.addWidget(self.advanced_search_button)
        filter_buttons_layout.addWidget(self.reset_filters_button)
        adv_layout.addRow(filter_buttons_layout)

        main_layout.addWidget(self.advanced_filter_group)

        # Statusanzeige
        self.status_label = QLabel("Bereit")
        main_layout.addWidget(self.status_label)

        # Tabelle
        self.data_table = QTableWidget()
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Nicht editierbar
        self.data_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # Spalten ziehbar machen
        header.setDefaultSectionSize(130)                      # Standardbreite 
        header.setFixedHeight(25)                             #  Header-Höhe 

        self.data_table.setStyleSheet("""
            QHeaderView::section {
                font-size: 14pt;
                font-weight: bold;
            }
        """)

        # Kontextmenü für die Tabelle setzen
        self.data_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.data_table.customContextMenuRequested.connect(self.open_context_menu)
        main_layout.addWidget(self.data_table)

        # Worker
        self.worker = None

        # Start
        self.load_analysis_results()

    
    # Button zum Ein-/Ausblenden der erweiterten Filter
    
    def toggle_advanced_filters(self):
        self.advanced_filters_visible = not self.advanced_filters_visible
        self.advanced_filter_group.setVisible(self.advanced_filters_visible)
        if self.advanced_filters_visible:
            self.toggle_advanced_button.setText("Erweiterte Filter ausblenden")
        else:
            self.toggle_advanced_button.setText("Erweiterte Filter einblenden")

    
    # Menü für Metrik-Auswahl
    
    def build_metric_menu(self):
        """
        Erzeugt ein QMenu mit checkbaren Aktionen für jede Spalte (self.all_columns).
        Zeigt Tooltips manuell an, weil Qt keine Hover-Tooltips bei QAction zeigt.
        """
        self.metric_menu.clear()

        for col_name in self.all_columns:
            action = QAction(col_name, self.metric_menu)
            action.setCheckable(True)
            action.setChecked(col_name in self.selected_columns or col_name in self.forced_columns)

            tooltip = self.metric_tooltips.get(col_name.lower())

            if tooltip:
                # Tooltip beim Mouse-Hover über das Menüelement
                def show_tip(tooltip_text=tooltip):
                    QToolTip.showText(QCursor.pos(), tooltip_text)

                action.hovered.connect(show_tip)

            if col_name in self.forced_columns:
                action.setEnabled(False)
            else:
                action.toggled.connect(lambda checked, c=col_name: self.on_metric_toggled(c, checked))

            self.metric_menu.addAction(action)



    def on_metric_toggled(self, column_name, checked):
        if column_name in self.forced_columns:
            return  # unmöglich, da disabled
        if checked:
            self.selected_columns.add(column_name)
        else:
            self.selected_columns.discard(column_name)
        self.load_analysis_results()

    def on_reset_metrics(self):
        """
        Stellt die Standardspalten wieder her (inkl. forced_columns).
        """
        self.selected_columns = set(self.default_columns)
        self.build_metric_menu()
        self.load_analysis_results()

    
    # Filter-Logik
    
    def load_analysis_results(self):
        """
        Baut die SQL-Abfrage dynamisch (Filter) und wählt IMMER alle Spalten.
        Zeigt in der Tabelle nur self.selected_columns (inkl. forced_columns).
        """
        self.status_label.setText("Lade Ergebnisse...")
        params = []

        # SELECT-Liste = alle Spalten
        select_clause = ", ".join(self.all_columns)
        query = f"SELECT {select_clause} FROM analysis_results"

        # Bedingungen
        conditions = []
        search_text = self.search_input.text().strip()
        if search_text:
            conditions.append("(Project_name LIKE ? OR File_name LIKE ?)")
            like_param = f"%{search_text}%"
            params.extend([like_param, like_param])

        # Knotenfilter
        node_min = self.node_min_spin.value()
        node_max = self.node_max_spin.value()
        if node_min > 0:
            conditions.append("number_of_nodes >= ?")
            params.append(node_min)
        if node_max > 0:
            conditions.append("number_of_nodes <= ?")
            params.append(node_max)

        # Kantenfilter
        edge_min = self.edge_min_spin.value()
        edge_max = self.edge_max_spin.value()
        if edge_min > 0:
            conditions.append("number_of_edges >= ?")
            params.append(edge_min)
        if edge_max > 0:
            conditions.append("number_of_edges <= ?")
            params.append(edge_max)

        # Gerichtete Graphen
        if self.directed_checkbox.isChecked():
            conditions.append("is_directed = ?")
            params.append(1)

        # Verbindungstyp
        conn_type = self.connection_type_combo.currentText()
        if conn_type != "Alle":
            if conn_type == "Stark":
                conditions.append("is_strongly_connected = ?")
                params.append(1)
            elif conn_type == "Schwach":
                conditions.append("is_weakly_connected = ?")
                params.append(1)
            elif conn_type == "Kein":
                conditions.append("is_connected = ?")
                params.append(0)

        # Dichte
        if self.density_slider.value() > 0:
            density_value = self.density_slider.value() / 100.0
            conditions.append("density >= ?")
            params.append(density_value)

        # PageRank
        if self.pagerank_slider.value() > 0:
            pr_value = self.pagerank_slider.value() / 100.0
            conditions.append("pagerank >= ?")
            params.append(pr_value)

        # Netzwerkstruktur
        if self.tree_checkbox.isChecked():
            conditions.append("is_tree = ?")
            params.append(1)
        if self.forest_checkbox.isChecked():
            conditions.append("is_forest = ?")
            params.append(1)
        if self.bipartite_checkbox.isChecked():
            conditions.append("is_bipartite = ?")
            params.append(1)
        if self.planar_checkbox.isChecked():
            conditions.append("is_planar = ?")
            params.append(1)
        if self.multigraph_checkbox.isChecked():
            conditions.append("is_multigraph = ?")
            params.append(1)

        # Zusammensetzen
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Sortierung
        sort_by = self.sort_by_combo.currentText()
        if sort_by == "Größe":
            query += " ORDER BY number_of_nodes DESC"
        elif sort_by == "Kanten":
            query += " ORDER BY number_of_edges DESC"
        elif sort_by == "Dichte":
            query += " ORDER BY density DESC"
        elif sort_by == "Zentralität":
            query += " ORDER BY pagerank DESC"

        print("Final query:", query)
        print("Params:", params)

        self.worker = DatabaseWorker(query, params)
        self.worker.results_ready.connect(self.update_table)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def update_table(self, results):
        """
        results: Liste von Tupeln, je Zeile hat len(self.all_columns) Elemente.
        Wir zeigen nur self.selected_columns + forced_columns in der Reihenfolge self.all_columns.
        """
        print("update_table wird aufgerufen mit Ergebnissen:", results)

        # forced_columns sind sowieso in selected_columns, da wir die Actions disabled haben gemacht 
        displayed_cols = [c for c in self.all_columns if c in self.selected_columns]

        self.data_table.clearContents()
        self.data_table.setRowCount(len(results))
        self.data_table.setColumnCount(len(displayed_cols))
        # Leere Labels setzen (werden durch Items ersetzt)
        self.data_table.setHorizontalHeaderLabels([""] * len(displayed_cols))

        # Für jede Spalte ein Header-Item mit Tooltip setzen
        for col_idx, col_name in enumerate(displayed_cols):
            header_item = QTableWidgetItem(col_name)
            tooltip = self.metric_tooltips.get(col_name.lower())
            if tooltip:
                header_item.setToolTip(tooltip)
            self.data_table.setHorizontalHeaderItem(col_idx, header_item)

        for row_idx, row_data in enumerate(results):
            for col_idx, col_name in enumerate(displayed_cols):
                full_index = self.all_columns.index(col_name)
                value = row_data[full_index]
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(row_idx, col_idx, item)
        

        # Speichere das komplette Ergebnis (alle Spalten) für den Einzelexport
        self.full_results = results

        self.status_label.setText(f"Ergebnisse geladen: {len(results)} Einträge gefunden.")

    
    # Erweiterte Filterpanel ein-/ausblenden
    
    def toggle_advanced_filters(self):
        self.advanced_filters_visible = not self.advanced_filters_visible
        self.advanced_filter_group.setVisible(self.advanced_filters_visible)
        if self.advanced_filters_visible:
            self.toggle_advanced_button.setText("Erweiterte Filter ausblenden")
        else:
            self.toggle_advanced_button.setText("Erweiterte Filter einblenden")

    
    # Reset der erweiterten Filter
    
    def reset_advanced_filters(self):
        self.node_min_spin.setValue(0)
        self.node_max_spin.setValue(0)
        self.edge_min_spin.setValue(0)
        self.edge_max_spin.setValue(0)
        self.directed_checkbox.setChecked(False)
        self.connection_type_combo.setCurrentIndex(0)
        self.density_slider.setValue(0)
        self.pagerank_slider.setValue(0)
        self.tree_checkbox.setChecked(False)
        self.forest_checkbox.setChecked(False)
        self.bipartite_checkbox.setChecked(False)
        self.planar_checkbox.setChecked(False)
        self.multigraph_checkbox.setChecked(False)
        self.sort_by_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.load_analysis_results()

    
    # Fehlerbehandlung
    
    def handle_error(self, error_message):
        print(f"⚠ Fehler: {error_message}")
        self.status_label.setText(f"Fehler: {error_message}")

    
    # Doppelklick
    
    def on_cell_double_clicked(self, row, column):
        """
        Wird aufgerufen, wenn man in der Tabelle doppelklickt.
        Da 'File_name' erzwungen ist, sollte es immer in self.selected_columns sein.
        """
        #  Ermittlung der sichtbaren Spalten und des File_name-Index
        displayed_cols = [c for c in self.all_columns if c in self.selected_columns]
        try:
            file_col_index = displayed_cols.index("File_name")
        except ValueError:
            self.status_label.setText("Spalte 'File_name' ist nicht sichtbar! (sollte unmöglich sein)")
            return

        # Dateiname aus der Tabelle auslesen
        file_item = self.data_table.item(row, file_col_index)
        if not file_item:
            self.status_label.setText("Kein Dateiname in der ausgewählten Zeile gefunden.")
            return

        filename = file_item.text()
        base_dir = "temp_uploads"
        full_path = os.path.join(base_dir, filename)

        # Existenz und Format-Checks
        if not os.path.exists(full_path):
            self.status_label.setText(f"Die Datei {filename} wurde nicht gefunden.")
            return
        if not filename.lower().endswith('.graphml'):
            self.status_label.setText(f"Die Datei {filename} ist kein GraphML-Dokument.")
            return

        # Statusmeldung
        self.status_label.setText(f"Visualisierung gestartet: {filename}")
        #  graph_center als JSON-String parsen
        #   Index der Spalte in self.all_columns finden
        center_idx = self.all_columns.index("graph_center")
        #     Roh-Wert aus dem geladenen Ergebnis
        raw = self.full_results[row][center_idx]
        #     JSON nach Python-Liste
        try:
            centers = json.loads(raw)
        except Exception:
            centers = []
        #  periphery als JSON-String parsen
        peri_idx = self.all_columns.index("periphery")
        raw_peri = self.full_results[row][peri_idx]
        try:
            periphery = json.loads(raw_peri)
        except Exception:
            periphery = []
        # Visualisierung aufrufen mit beiden Highlight-Parametern
        if hasattr(self.parent, "visualization_section"):
            self.parent.visualization_section.load_graph_from_path(
                full_path,
                highlight_nodes=centers,
                highlight_periphery=periphery
            )

    


    def open_context_menu(self, pos):
        index = self.data_table.indexAt(pos)
        context_menu = QMenu(self.data_table)

        # Einzel-Export
        if index.isValid():
            row = index.row()
            export_json_action = QAction("Als JSON exportieren", self.data_table)
            export_json_action.triggered.connect(lambda: self.export_single_record(row))
            context_menu.addAction(export_json_action)

        # Gesamtexport als CSV (immer verfügbar)
        export_csv_action = QAction("Tabelle als CSV exportieren", self.data_table)
        export_csv_action.triggered.connect(self.export_to_csv)
        context_menu.addAction(export_csv_action)

        context_menu.exec_(self.data_table.viewport().mapToGlobal(pos))


    def export_single_record(self, row):
        """
        Extrahiert den vollständigen Datensatz (alle Spalten) aus der gewählten Zeile
        und exportiert ihn als JSON. Der 'id'-Schlüssel wird entfernt.
        """
        # Überprüfe, ob das vollständige Ergebnis verfügbar ist
        try:
            full_row = self.full_results[row]
        except (AttributeError, IndexError):
            QMessageBox.warning(self, "Warnung", "Kein vollständiger Datensatz verfügbar.")
            return

        # Erstelle ein Dictionary, das alle Spalten aus self.all_columns enthält
        record = {}
        for idx, col_name in enumerate(self.all_columns):
            record[col_name] = full_row[idx]

        # Entferne 'id'-Schlüssel, falls vorhanden
        record.pop("id", None)

        # Bestimme Standard Dateinamen basierend auf 'File_name' oder 'Project_name'
        base_name = record.get("File_name") or record.get("Project_name") or "Datensatz"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{base_name}_{timestamp}.json"

        # Dateiauswahl-Dialog, um den Speicherort und Namen festzulegen
        file_name, _ = QFileDialog.getSaveFileName(self, "Export einzelnes JSON", default_filename, "JSON-Dateien (*.json)")
        if file_name:
            try:
                export_single_record_to_json(record, file_name)
                QMessageBox.information(self, "Erfolg", f"Graph {base_name} erfolgreich als JSON exportiert!")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Export: {str(e)}")

    def export_to_csv(self):
        """
        Exportiert die aktuell angezeigten Ergebnisse (nur sichtbare Spalten) als CSV-Datei.
        """
        if not hasattr(self, "full_results") or not self.full_results:
            QMessageBox.warning(self, "Kein Inhalt", "Keine Daten zum Exportieren vorhanden.")
            return

        # Nur sichtbare Spalten exportieren
        displayed_cols = [c for c in self.all_columns if c in self.selected_columns]
        col_indices = [self.all_columns.index(c) for c in displayed_cols]

        # Datei auswählen
        file_path, _ = QFileDialog.getSaveFileName(self, "CSV exportieren", "export.csv", "CSV-Dateien (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(displayed_cols)  # Header
                for row in self.full_results:
                    writer.writerow([row[i] for i in col_indices])
            QMessageBox.information(self, "Erfolg", f"CSV-Datei erfolgreich gespeichert: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Exportieren: {str(e)}")

