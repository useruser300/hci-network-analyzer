import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTabWidget, QStatusBar, QSplitter
)
from PyQt5.QtCore import Qt, QSettings

from frontend.components.styles import apply_dark_fusion_palette, apply_light_fusion_palette
from frontend.components.toolbar import Toolbar
from frontend.components.upload_panel import UploadPanel
from frontend.components.single_graph_tab import SingleGraphTab
from frontend.components.dataset_analysis_tab import DatasetAnalysisTab


class NetworkAnalysisGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Netzwerkanalyse-Tool (neue HCI-GUI)")
        self.setGeometry(100, 100, 1200, 800)

        # Zentrales Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # QSplitter für den horizontalen Bereich
        self.splitter = QSplitter(Qt.Horizontal, main_widget)
        self.splitter.setHandleWidth(10)   


        # Linker Bereich: Container für die Sidebar (enthält das UploadPanel mitt Toggle-Button)
        self.left_container = QWidget()
        self.left_container.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_container.setLayout(left_layout)

        # Füge das UploadPanel 
        self.upload_panel = UploadPanel(self)
        left_layout.addWidget(self.upload_panel)
        # Mindestbreite des linken Containers
        self.left_container.setMinimumWidth(self.upload_panel.collapsed_width)
        # maximale Breite 
        self.left_container.setMaximumWidth(self.upload_panel.expanded_width)

        self.splitter.addWidget(self.left_container)
        # Verhindert, dass der linke Bereich komplett kollabiert
        self.splitter.setCollapsible(0, False)

        # Rechter Bereich: Tab-Widget
        self.tabs = QTabWidget()
        self.splitter.addWidget(self.tabs)

        # Stretch-Faktor
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # Splitter in das Hauptlayout 
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.splitter)

        # Tabs initialisieren
        self.single_graph_tab = SingleGraphTab(self)
        self.tabs.addTab(self.single_graph_tab, "Einzelgraph-Analyse")
        self.dataset_tab = DatasetAnalysisTab(self)
        self.tabs.addTab(self.dataset_tab, "Datensatz-Analyse")

        # Toolbar hinzufügen
        self._init_toolbar()

        # Statusbar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Theme laden (Dark oder Light)
        self.load_theme()

        self.show()

        # Standardwerte für die Sidebar-Breite
        self._sidebar_expanded_width = 320  
        self._sidebar_collapsed_width = 40    

        # Verbinde Signal splitterMoved, um Inhalt bei manueller Anpassung zu kontrollieren
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

    def _init_toolbar(self):
        self.toolbar = Toolbar(self)
        self.addToolBar(self.toolbar)

    def apply_theme(self, mode):
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if mode == "dark":
            apply_dark_fusion_palette(app)
        else:
            apply_light_fusion_palette(app)
        settings = QSettings("MyCompany", "MyApp")
        settings.setValue("theme", mode)

    def load_theme(self):
        settings = QSettings("MyCompany", "MyApp")
        mode = settings.value("theme", "light")
        self.apply_theme(mode)

    def handle_toggle_sidebar(self):
        """
        Wird vom UploadPanel (Toggle-Button) aufgerufen.
        Schaltet die Breite des linken Bereichs im Splitter zwischen minimal (40px)
        und Standardbreite (z. B. 250px) um und blendet den Inhalt entsprechend ein oder aus.
        """
        sizes = self.splitter.sizes()  
        left_width = sizes[0]
        right_width = sizes[1]

        if left_width > self._sidebar_collapsed_width + 10:  
            new_sizes = [self._sidebar_collapsed_width, left_width + right_width - self._sidebar_collapsed_width]
            self.splitter.setSizes(new_sizes)
            # Inhalt ausblenden
            self.upload_panel.content_widget.hide()
        else:  # ausklappen
            new_sizes = [self._sidebar_expanded_width, left_width + right_width - self._sidebar_expanded_width]
            self.splitter.setSizes(new_sizes)
            # Inhalt einblenden
            self.upload_panel.content_widget.show()

    def on_splitter_moved(self, pos, index):
        """
        Überwacht die Bewegung des Splitters.
        Wenn der linke Bereich (Sidebar) nahe der Minimalbreite ist,
        wird der Inhalt ausgeblendet, andernfalls eingeblendet.
        """
        sizes = self.splitter.sizes()
        left_width = sizes[0]
        if left_width <= self._sidebar_collapsed_width + 10:
            self.upload_panel.content_widget.hide()
            self.upload_panel.toggle_button.setText(">>")
        else:
            self.upload_panel.content_widget.show()
            self.upload_panel.toggle_button.setText("<<")


def main():
    app = QApplication(sys.argv)
    gui = NetworkAnalysisGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
