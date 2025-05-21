# single_graph_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt
from frontend.components.analysis_section import AnalysisSection
from frontend.components.visualization_section import VisualizationSection

class SingleGraphTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Hauptlayout
        layout = QVBoxLayout(self)

        # QSplitter

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(10)  # Griff  
        layout.addWidget(splitter)

        # AnalysisSection
        self.analysis_section = AnalysisSection(self)
        splitter.addWidget(self.analysis_section)

        # VisualizationSection
        self.visualization_section = VisualizationSection(self)
        splitter.addWidget(self.visualization_section)
 