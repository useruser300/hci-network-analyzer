# dataset_analysis_tab.py

import os
import json
import sqlite3
import numpy as np


from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QMessageBox, QFileDialog, QTabWidget, QToolButton, QMenu, QAction
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


#  Globale Datenbankpfad

DATABASE_PATH = "./network_analysis.db"


#  Asynchroner DatabaseWorker

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


# DatasetAnalysisTab-Klasse (ohne Interpretationsbereich)

from PyQt5.QtGui import QPixmap
class DatasetAnalysisTab(QWidget):
    """
    Zeigt zwei Diagramme (in Tabs) mit dynamischer Metrikauswahl.
    - Wenn "Alle" gewählt ist, werden mehrere Datensätze (GROUP BY) geholt,
      Diagramm 1 = [0..1] Metriken, Diagramm 2 = reelle Metriken, 
      gruppiert nach Datensatz, farbcodiert, Legende.
    - Wenn ein einzelner Datensatz gewählt ist, 
      wird wie bisher ein Balkendiagramm (einzelner Balken pro Metrik) gezeigt.

    Das Interpretations-Label und -Textfeld wurden entfernt.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        
        # Hauptlayout
        
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        
        # Steuerbereich 

        control_layout = QHBoxLayout()
        self.layout.addLayout(control_layout)

        # ComboBox für Datenquelle
        self.dataset_combo = QComboBox()
        self.dataset_combo.setObjectName("metricButton")
        self.dataset_combo.addItem("Alle")
        self.dataset_combo.addItem("Rocketfuel")
        self.dataset_combo.addItem("TopologyZoo")
        self.dataset_combo.addItem("SNDlibrary")
        self.dataset_combo.addItem("CAIDA")
        control_layout.addWidget(self.dataset_combo)

        #  Analyse laden Button
        self.load_button = QPushButton("Analyse laden")
        self.load_button.setObjectName("fastSearchButton")
        self.load_button.clicked.connect(self.load_analysis)
        control_layout.addWidget(self.load_button)

        # ToolButton + Menu für Metrik-Auswahl (Diagramm 1 / 2)
        self.metric_button = QToolButton()
        self.metric_button.setObjectName("metricButton")
        self.metric_button.setText("Metriken wählen")
        self.metric_button.setPopupMode(QToolButton.InstantPopup)
        self.metric_menu = QMenu(self)
        self.metric_button.setMenu(self.metric_menu)
        control_layout.addWidget(self.metric_button)

        # Standardwerte zurücksetzen
        self.reset_button = QPushButton("Standardwerte zurücksetzen")
        self.reset_button.setObjectName("resetMetricsButton")
        self.reset_button.clicked.connect(self.on_reset_metrics)
        control_layout.addWidget(self.reset_button)

 
        # QTabWidget für Diagramme

        self.diag_tabwidget = QTabWidget()
        self.layout.addWidget(self.diag_tabwidget)

        # Tab 1: Diagramm 1 ([0..1])
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout(self.tab1)
        self.fig1 = Figure(figsize=(5,3))
        self.canvas1 = FigureCanvas(self.fig1)
        self.tab1_layout.addWidget(self.canvas1)
      # Kontextmenü für Canvas1  
        self.canvas1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas1.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self.canvas1, pos)
        )
        self.diag_tabwidget.addTab(self.tab1, "Diagramm [0..1]")

        # Tab 2: Diagramm 2 (Reelle Zahlen)
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout(self.tab2)
        self.fig2 = Figure(figsize=(5,3))
        self.canvas2 = FigureCanvas(self.fig2)
        self.tab2_layout.addWidget(self.canvas2)
        #  Kontextmenü für Canvas2
        self.canvas2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.canvas2.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self.canvas2, pos)
        )
        self.diag_tabwidget.addTab(self.tab2, "Diagramm (Reelle Zahlen)")

        self.diag_tabwidget.currentChanged.connect(self.on_diagram_tab_changed)

    
        # Export-Button JSON

        export_layout = QHBoxLayout()
        self.export_button = QPushButton("Export (JSON)")
        self.export_button.setObjectName("resetMetricsButton")
        self.export_button.clicked.connect(self.export_as_json)
        export_layout.addWidget(self.export_button)
        self.layout.addLayout(export_layout)


        # Metrik-Definitionen

        # Diagramm 1 ([0..1]) hat 13 Metriken
        self.metrics_diagram1 = [
            "is_connected_avg", "density_avg", "is_tree_avg", "is_forest_avg",
            "is_bipartite_avg", "is_planar_avg", "is_multigraph_avg",
            "global_efficiency", "local_efficiency",
            "degree_centrality", "betweenness_centrality",
            "closeness_centrality", "pagerank"
        ]
        # Diagramm 2 (Reelle Zahlen) hat 6 Metriken
        self.metrics_diagram2 = [
            "node_connectivity", "edge_connectivity",
            "diameter", "radius", "number_of_nodes", "number_of_edges"
        ]

        # Standard-Auswahl
        self.default_selected_diagram1 = {
            "is_connected_avg", "density_avg", "pagerank"
        }
        self.default_selected_diagram2 = {
            "node_connectivity", "diameter", "number_of_nodes"
        }

        # Aktuell gewählte Metriken
        self.selected_metrics_diagram1 = set(self.default_selected_diagram1)
        self.selected_metrics_diagram2 = set(self.default_selected_diagram2)

        # Datenpuffer
        self.last_results = []  # Kann mehrere Zeilen enthalten, wenn Alle gewählt
        self.single_row_mode = True  # True = nur 1 Datensatz, False = mehrere

        # Beim Start
        self.on_diagram_tab_changed(0)

    #   DB-Abfrage (Single und Alle)
    def load_analysis(self):
        selected_source = self.dataset_combo.currentText()
        if selected_source == "Alle":
            self.load_all_datasets_grouped()
        else:
            self.load_single_dataset(selected_source)

    def load_all_datasets_grouped(self):
        query = """
        SELECT
          Project_name,
          AVG(CAST(is_connected AS FLOAT)) as is_connected_avg,
          AVG(density) as density_avg,
          AVG(CAST(is_tree AS FLOAT)) as is_tree_avg,
          AVG(CAST(is_forest AS FLOAT)) as is_forest_avg,
          AVG(CAST(is_bipartite AS FLOAT)) as is_bipartite_avg,
          AVG(CAST(is_planar AS FLOAT)) as is_planar_avg,
          AVG(CAST(is_multigraph AS FLOAT)) as is_multigraph_avg,
          AVG(global_efficiency) as global_efficiency,
          AVG(local_efficiency) as local_efficiency,
          AVG(degree_centrality) as degree_centrality,
          AVG(betweenness_centrality) as betweenness_centrality,
          AVG(closeness_centrality) as closeness_centrality,
          AVG(pagerank) as pagerank,

          AVG(node_connectivity) as node_connectivity,
          AVG(edge_connectivity) as edge_connectivity,
          AVG(diameter) as diameter,
          AVG(radius) as radius,
          AVG(number_of_nodes) as number_of_nodes,
          AVG(number_of_edges) as number_of_edges,

          COUNT(*) as graph_count,
          SUM(CAST(is_tree AS INT)) as tree_count,
          SUM(CAST(is_forest AS INT)) as forest_count,
          SUM(CAST(is_bipartite AS INT)) as bipartite_count,
          SUM(CAST(is_multigraph AS INT)) as multigraph_count,
          SUM(CAST(is_planar AS INT)) as planar_count
        FROM analysis_results
        GROUP BY Project_name
        """
        self.worker = DatabaseWorker(query)
        self.worker.results_ready.connect(self.on_results_ready_all)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_results_ready_all(self, rows):
        if not rows:
            QMessageBox.information(self, "Info", "Keine Datensätze gefunden (Alle).")
            return
        self.last_results = rows
        self.single_row_mode = False
        self.update_charts_all()
        # Interpretation Methoden entfernt wenn ich wieder habe mochte hier 

    def load_single_dataset(self, source):
        query = f"""
        SELECT
            /* Anzahl / Counts */
            COUNT(*) as total_graphs,
            SUM(CAST(is_bipartite AS INT)) as bipartite_count,
            SUM(CAST(is_multigraph AS INT)) as multigraph_count,
            SUM(CAST(is_tree AS INT)) as tree_count,
            SUM(CAST(is_forest AS INT)) as forest_count,
            SUM(CAST(is_planar AS INT)) as planar_count,

            /* [0..1] AVG-Werte */
            AVG(CAST(is_connected AS FLOAT)) as is_connected_avg,
            AVG(density) as density_avg,
            AVG(CAST(is_tree AS FLOAT)) as is_tree_avg,
            AVG(CAST(is_forest AS FLOAT)) as is_forest_avg,
            AVG(CAST(is_bipartite AS FLOAT)) as is_bipartite_avg,
            AVG(CAST(is_planar AS FLOAT)) as is_planar_avg,
            AVG(CAST(is_multigraph AS FLOAT)) as is_multigraph_avg,
            AVG(global_efficiency) as global_efficiency,
            AVG(local_efficiency) as local_efficiency,
            AVG(degree_centrality) as degree_centrality,
            AVG(betweenness_centrality) as betweenness_centrality,
            AVG(closeness_centrality) as closeness_centrality,
            AVG(pagerank) as pagerank,

            /* Reelle Zahlen */
            AVG(node_connectivity) as node_connectivity,
            AVG(edge_connectivity) as edge_connectivity,
            AVG(diameter) as diameter,
            AVG(radius) as radius,
            AVG(number_of_nodes) as number_of_nodes,
            AVG(number_of_edges) as number_of_edges
        FROM analysis_results
        WHERE Project_name = ?
        """
        self.worker = DatabaseWorker(query, [source])
        self.worker.results_ready.connect(self.on_results_ready_single)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_results_ready_single(self, rows):
        if not rows or not rows[0]:
            QMessageBox.information(self, "Info", "Keine Daten gefunden.")
            return

        row = rows[0]
        safe = lambda x: x if x is not None else 0
        self.single_row_mode = True
        self.last_results = [{
            "total_graphs":       safe(row[0]),
            "bipartite_count":    safe(row[1]),
            "multigraph_count":   safe(row[2]),
            "tree_count":         safe(row[3]),
            "forest_count":       safe(row[4]),
            "planar_count":       safe(row[5]),

            "is_connected_avg":   safe(row[6]),
            "density_avg":        safe(row[7]),
            "is_tree_avg":        safe(row[8]),
            "is_forest_avg":      safe(row[9]),
            "is_bipartite_avg":   safe(row[10]),
            "is_planar_avg":      safe(row[11]),
            "is_multigraph_avg":  safe(row[12]),
            "global_efficiency":  safe(row[13]),
            "local_efficiency":   safe(row[14]),
            "degree_centrality":  safe(row[15]),
            "betweenness_centrality": safe(row[16]),
            "closeness_centrality":   safe(row[17]),
            "pagerank":           safe(row[18]),

            "node_connectivity":  safe(row[19]),
            "edge_connectivity":  safe(row[20]),
            "diameter":           safe(row[21]),
            "radius":             safe(row[22]),
            "number_of_nodes":    safe(row[23]),
            "number_of_edges":    safe(row[24]),
        }]
        self.update_charts_single()
        # Interpretation Methoden entfernt auch hier 

    def on_error(self, error_message):
        print("Fehler in DatasetAnalysisTab:", error_message)
        QMessageBox.critical(self, "Fehler", f"Database Error: {error_message}")

    # Diagramm-Update (Modus Alle und  Single)
    def update_charts_single(self):
        if not self.last_results:
            return
        single_dict = self.last_results[0]

        current_tab = self.diag_tabwidget.currentIndex()
        if current_tab == 0:
            # Diagramm 1 ([0..1]) => grünes Balkendiagramm
            self.fig1.clear()
            ax1 = self.fig1.add_subplot(111)

            selected = self.selected_metrics_diagram1
            data_dict = {m: single_dict[m] for m in selected if m in single_dict}

            names = list(data_dict.keys())
            values = list(data_dict.values())

            ax1.bar(names, values, color='green')
            ax1.set_title("Diagramm [0..1] (Ein Datensatz)")
            ax1.set_ylabel("Wert")
            ax1.set_xticks(range(len(names)))
            ax1.set_xticklabels(names, rotation=45, ha="right")

            self.fig1.tight_layout()
            self.canvas1.draw()
        else:
            # Diagramm 2 (Reelle Zahlen) => blaues Balkendiagramm
            self.fig2.clear()
            ax2 = self.fig2.add_subplot(111)

            selected = self.selected_metrics_diagram2
            data_dict = {m: single_dict[m] for m in selected if m in single_dict}

            names = list(data_dict.keys())
            values = list(data_dict.values())

            ax2.bar(names, values, color='blue')
            ax2.set_title("Diagramm (Reelle Zahlen) (Ein Datensatz)")
            ax2.set_ylabel("Wert")
            ax2.set_xticks(range(len(names)))
            ax2.set_xticklabels(names, rotation=45, ha="right")

            self.fig2.tight_layout()
            self.canvas2.draw()

    def update_charts_all(self):
        if not self.last_results:
            return

        current_tab = self.diag_tabwidget.currentIndex()
        if current_tab == 0:
            # Diagramm 1 ([0..1])
            self.fig1.clear()
            ax1 = self.fig1.add_subplot(111)

            metric_map = {
                "is_connected_avg":       1,
                "density_avg":            2,
                "is_tree_avg":            3,
                "is_forest_avg":          4,
                "is_bipartite_avg":       5,
                "is_planar_avg":          6,
                "is_multigraph_avg":      7,
                "global_efficiency":      8,
                "local_efficiency":       9,
                "degree_centrality":      10,
                "betweenness_centrality": 11,
                "closeness_centrality":   12,
                "pagerank":               13,
            }
            project_names = [row[0] for row in self.last_results]
            x = np.arange(len(project_names))

            selected = sorted(m for m in self.selected_metrics_diagram1 if m in metric_map)
            bar_width = 0.08
            color_map = self.get_color_map(selected)

            for i, metric in enumerate(selected):
                offset = i * bar_width
                col_idx = metric_map[metric]
                values = [row[col_idx] if row[col_idx] else 0 for row in self.last_results]
                ax1.bar(x + offset, values, bar_width, label=metric, color=color_map[metric])

            ax1.set_xticks(x + bar_width*(len(selected)-1)/2 if selected else 0)
            ax1.set_xticklabels(project_names, rotation=45, ha="right")
            ax1.set_xlabel("Datensätze")
            ax1.set_ylabel("Wert (0..1)")
            ax1.set_title("Gruppierte Diagramme (Alle) [0..1]")

            if selected:
                ax1.legend(title="Metriken")

            self.fig1.tight_layout()
            self.canvas1.draw()
        else:
            # Diagramm 2 (Reelle Zahlen)
            self.fig2.clear()
            ax2 = self.fig2.add_subplot(111)

            metric_map = {
                "node_connectivity": 14,
                "edge_connectivity": 15,
                "diameter":          16,
                "radius":            17,
                "number_of_nodes":   18,
                "number_of_edges":   19,
            }
            project_names = [row[0] for row in self.last_results]
            x = np.arange(len(project_names))

            selected = sorted(m for m in self.selected_metrics_diagram2 if m in metric_map)
            bar_width = 0.12
            color_map = self.get_color_map(selected)

            for i, metric in enumerate(selected):
                offset = i * bar_width
                col_idx = metric_map[metric]
                values = [row[col_idx] if row[col_idx] else 0 for row in self.last_results]
                ax2.bar(x + offset, values, bar_width, label=metric, color=color_map[metric])

            ax2.set_xticks(x + bar_width*(len(selected)-1)/2 if selected else 0)
            ax2.set_xticklabels(project_names, rotation=45, ha="right")
            ax2.set_xlabel("Datensätze")
            ax2.set_ylabel("Wert")
            ax2.set_title("Gruppierte Diagramme (Alle) (Reelle Zahlen)")

            if selected:
                ax2.legend(title="Metriken")

            self.fig2.tight_layout()
            self.canvas2.draw()

    # Dynamische Metrik-Liste
    def on_diagram_tab_changed(self, index):
        self.rebuild_metric_menu(index)
        if self.dataset_combo.currentText() == "Alle":
            self.update_charts_all()
        else:
            self.update_charts_single()

    def rebuild_metric_menu(self, diagram_index):
        self.metric_menu.clear()

        if diagram_index == 0:
            metrics = self.metrics_diagram1
            selected_set = self.selected_metrics_diagram1
        else:
            metrics = self.metrics_diagram2
            selected_set = self.selected_metrics_diagram2

        for metric in metrics:
            action = QAction(metric, self.metric_menu)
            action.setCheckable(True)
            action.setChecked(metric in selected_set)
            action.toggled.connect(lambda checked, m=metric: self.on_metric_toggled(m, checked))
            self.metric_menu.addAction(action)

    def on_metric_toggled(self, metric, checked):
        current_tab = self.diag_tabwidget.currentIndex()
        if current_tab == 0:
            if checked:
                self.selected_metrics_diagram1.add(metric)
            else:
                self.selected_metrics_diagram1.discard(metric)
        else:
            if checked:
                self.selected_metrics_diagram2.add(metric)
            else:
                self.selected_metrics_diagram2.discard(metric)

        if self.dataset_combo.currentText() == "Alle":
            self.update_charts_all()
            # Interpretation-Aufruf entfernt hier auc
        else:
            self.update_charts_single()
            # Interpretation-Aufruf entfernt ****

    def on_reset_metrics(self):
        self.selected_metrics_diagram1 = set(self.default_selected_diagram1)
        self.selected_metrics_diagram2 = set(self.default_selected_diagram2)
        self.rebuild_metric_menu(self.diag_tabwidget.currentIndex())

        if self.dataset_combo.currentText() == "Alle":
            self.update_charts_all()
            # Interpretation-Aufruf entfernt hier 
        else:
            self.update_charts_single()
            # Interpretation-Aufruf entfernt hier 

    # Farbcodierung
    def get_color_map(self, metrics):
        colors = [
            "red", "orange", "gold", "green", "cyan", "blue", "purple", 
            "magenta", "pink", "lime", "chocolate", "gray", "olive",
        ]
        color_map = {}
        for i, m in enumerate(metrics):
            color_map[m] = colors[i % len(colors)]
        return color_map

    #  Export
    def export_as_json(self):
        if not self.last_results:
            QMessageBox.warning(self, "Warnung", "Keine Daten zum Exportieren. Bitte zuerst Analyse laden.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "JSON speichern", "", "JSON-Dateien (*.json)")
        if file_name:
            if self.single_row_mode:
                data = {
                    "mode": "Einzel",
                    "dataset": self.dataset_combo.currentText(),
                    "results": self.last_results[0],
                    "selected_metrics_diagram1": list(self.selected_metrics_diagram1),
                    "selected_metrics_diagram2": list(self.selected_metrics_diagram2)
                }
            else:
                output = []
                for row in self.last_results:
                    d = {}
                    d["Project_name"] = row[0]
                    d["is_connected_avg"] = row[1]
                    d["density_avg"]      = row[2]
                    d["is_tree_avg"]      = row[3]
                    d["is_forest_avg"]    = row[4]
                    d["is_bipartite_avg"] = row[5]
                    d["is_planar_avg"]    = row[6]
                    d["is_multigraph_avg"] = row[7]
                    d["global_efficiency"] = row[8]
                    d["local_efficiency"]  = row[9]
                    d["degree_centrality"] = row[10]
                    d["betweenness_centrality"] = row[11]
                    d["closeness_centrality"]   = row[12]
                    d["pagerank"]               = row[13]
                    d["node_connectivity"] = row[14]
                    d["edge_connectivity"] = row[15]
                    d["diameter"]          = row[16]
                    d["radius"]            = row[17]
                    d["number_of_nodes"]   = row[18]
                    d["number_of_edges"]   = row[19]
                    d["graph_count"]       = row[20]
                    d["tree_count"]        = row[21]
                    d["forest_count"]      = row[22]
                    d["bipartite_count"]   = row[23]
                    d["multigraph_count"]  = row[24]
                    d["planar_count"]      = row[25]
                    output.append(d)

                data = {
                    "mode": "Alle",
                    "results": output,
                    "selected_metrics_diagram1": list(self.selected_metrics_diagram1),
                    "selected_metrics_diagram2": list(self.selected_metrics_diagram2)
                }

            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Erfolg", "Daten erfolgreich als JSON exportiert.")

    def get_generated_images(self):
        """
        Gibt eine Liste von QImage-Objekten zurück, die die aktuell dargestellten Diagramme enthalten.
        """
        images = []
        try:
            # Export Diagramm 1
            if hasattr(self, 'canvas1') and self.canvas1:
                pixmap1 = self.canvas1.grab()
                images.append(pixmap1.toImage())
            # Export Diagramm 2
            if hasattr(self, 'canvas2') and self.canvas2:
                pixmap2 = self.canvas2.grab()
                images.append(pixmap2.toImage())
        except Exception as e:
            print("Fehler beim Exportieren der Bilder:", e)
        return images
    

       # Kontextmenü-Handler für Diagramm-Canvases 
    def _show_context_menu(self, canvas, pos):
        menu = QMenu(self)
        save_act = menu.addAction("Diagramm speichern…")
        action = menu.exec_(canvas.mapToGlobal(pos))
        if action == save_act:
            # bestimme, welches Bild gespeichert werden soll
            images = self.get_generated_images()
            img = images[0] if canvas is self.canvas1 else images[1]
            if img:
                fname, _ = QFileDialog.getSaveFileName(
                    self,
                    "Diagramm speichern",
                    "",
                    "PNG-Dateien (*.png);;JPEG-Dateien (*.jpg *.jpeg)"
                )
                if fname:
                    img.save(fname)
