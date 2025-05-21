import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu

)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from backend import pipeline

def guess_data_source_by_extension(filename):
    ext = os.path.splitext(filename)[1].lower()
    mapping = {
        ".graphml": "TopologyZoo",
        ".xml": "SNDlib",
        ".cch": "Rocketfuel",
        ".txt": "CAIDA_AS",
    }
    return mapping.get(ext, "Unbekannt")

class AnalysisThread(QThread):
    finished = pyqtSignal()

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        pipeline.process_files(self.file_paths)
        self.finished.emit()

class UploadPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.uploaded_files = []
        self.expanded_width = 320
        self.collapsed_width = 40
        self.expanded = True

        # Drag-&-Drop aktivieren soll noch datein validiern machen 
        self.setAcceptDrops(True)

        # Hauptlayout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Toggle-Button
        self.toggle_button = QPushButton("<<")
        self.toggle_button.setObjectName("toggleButton")
        self.toggle_button.setFixedWidth(40)
        self.toggle_button.clicked.connect(self.toggle_panel)
        self.main_layout.addWidget(self.toggle_button, 0, Qt.AlignTop)

        # Content-Widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)

        # Button-Bereich
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("📂 Datei hochladen")
        self.upload_button.setObjectName("uploadButton")
        self.upload_button.clicked.connect(self.upload_files)
        button_layout.addWidget(self.upload_button)
        self.analyze_button = QPushButton("🔍 Analyse starten")
        self.analyze_button.setObjectName("analyzeButton")
        self.analyze_button.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.analyze_button)
        self.content_layout.addLayout(button_layout)

        # Status-Label
        self.status_label = QLabel("Status: Keine Datei hochgeladen.")
        self.content_layout.addWidget(self.status_label)

        # Tabelle der hochgeladenen Dateien
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["Dateiname", "Quelle", "Status"])
        header = self.files_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setDefaultSectionSize(102)
        header.setFixedHeight(25)
        self.files_table.setStyleSheet("""
            QHeaderView::section {
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        self.content_layout.addWidget(self.files_table)
        self.files_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.main_layout.addWidget(self.content_widget, 1)

    def toggle_panel(self):
        if self.parent and hasattr(self.parent, "handle_toggle_sidebar"):
            self.parent.handle_toggle_sidebar()
            self.expanded = not self.expanded
            self.toggle_button.setText("<<" if self.expanded else ">>")

    def upload_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Dateien auswählen", "",
            "Unterstützte Dateien (*.graphml *.xml *.cch *.txt);;Alle Dateien (*)"
        )
        if files:
            destination_folder = "temp_uploads"
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            for file_path in files:
                base_name = os.path.basename(file_path)
                destination_path = os.path.join(destination_folder, base_name)
                try:
                    shutil.copy(file_path, destination_path)
                    self.uploaded_files.append(destination_path)
                    guessed_source = guess_data_source_by_extension(base_name)
                    self.add_file_to_table(base_name, guessed_source, "Bereit")
                except Exception as e:
                    self.status_label.setText(f"⚠ Fehler beim Kopieren von {base_name}: {e}")
                    return
            self.status_label.setText(f"✅ {len(files)} Datei(en) erfolgreich gespeichert.")

    def add_file_to_table(self, filename, source, status):
        row = self.files_table.rowCount()
        self.files_table.insertRow(row)
        self.files_table.setItem(row, 0, QTableWidgetItem(filename))
        self.files_table.setItem(row, 1, QTableWidgetItem(source))
        self.files_table.setItem(row, 2, QTableWidgetItem(status))

    def start_analysis(self):
        if not self.uploaded_files:
            self.status_label.setText("⚠ Keine Datei hochgeladen!")
            return
        for row in range(self.files_table.rowCount()):
            self.files_table.setItem(row, 2, QTableWidgetItem("🔄 in Analyse..."))
        self.analysis_thread = AnalysisThread(self.uploaded_files)
        self.analysis_thread.finished.connect(self.analysis_finished)
        self.analysis_thread.start()
        self.status_label.setText("🔍 Analyse gestartet...")

    def analysis_finished(self):
        self.status_label.setText("✅ Analyse abgeschlossen!")
        for row in range(self.files_table.rowCount()):
            self.files_table.setItem(row, 2, QTableWidgetItem("✔️ analysiert"))
        if hasattr(self.parent, "single_graph_tab") and hasattr(self.parent.single_graph_tab, "analysis_section"):
            self.parent.single_graph_tab.analysis_section.load_analysis_results()
        self.uploaded_files.clear()

    # Gemeinsame Drag-&-Drop-Logik auslagern
    def handle_dropped_files(self, file_paths):
        destination_folder = "temp_uploads"
        os.makedirs(destination_folder, exist_ok=True)
        for src in file_paths:
            name = os.path.basename(src)
            dst = os.path.join(destination_folder, name)
            try:
                shutil.copy(src, dst)
                self.uploaded_files.append(dst)
                quelle = guess_data_source_by_extension(name)
                self.add_file_to_table(name, quelle, "Bereit")
            except Exception as e:
                self.status_label.setText(f"⚠ Fehler: {e}")
                return
        self.status_label.setText(f"✅ {len(file_paths)} Datei(en) bereit zur Analyse.")

    # Drag-Event erlauben
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # Drop-Event verarbeiten
    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        self.handle_dropped_files(paths)




        # Kontextmenü zum Löschen
    def show_context_menu(self, pos):
        row = self.files_table.rowAt(pos.y())
        if row < 0:
            return
        menu = QMenu()
        delete_action = menu.addAction("Datei löschen")
        action = menu.exec_(self.files_table.viewport().mapToGlobal(pos))
        if action == delete_action:
            self.delete_file(row)

    def delete_file(self, row):
        # Pfad aus Liste entfernen
        filename = self.files_table.item(row, 0).text()
        # finde index in uploaded_files anhand des Basisnamens
        for p in self.uploaded_files:
            if os.path.basename(p) == filename:
                try:
                    os.remove(p)
                except OSError:
                    pass
                self.uploaded_files.remove(p)
                break
        # Zeile aus Tabelle löschen
        self.files_table.removeRow(row)
        self.status_label.setText(f"🗑️ '{filename}' gelöscht.")