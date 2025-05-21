# styles.py

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_dark_fusion_palette(app):
    """
    Aktiviert den Fusion-Style und setzt eine dunkle QPalette.
    """
    app.setStyle("Fusion")
    dark_palette = QPalette()

    # Fenster- und Widget-Hintergrund
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))

    # Textfarbe
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)

    # Buttons
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)

    # Auswahlelemente (z. B. markierter Text, Hover)
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    # Tooltip
    dark_palette.setColor(QPalette.ToolTipBase, QColor(30, 30, 30))  # dunkler Hintergrund
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)            # heller Text


    # Link-Farbe (z. B. in Labels)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))

    app.setPalette(dark_palette)
    app.setStyleSheet("""
                      
        
        * {
        font-weight: bold;
         }
        QSplitter::handle {
            background-color: rgba(255, 255, 255, 30);  /* leicht sichtbar, dunkelkompatibel */
        }
        QSplitter::handle:hover {
            background-color: rgba(255, 255, 255, 60);  /* stärker beim Hover */
        }
        QToolButton#metricButton {
            background-color: rgb(70, 130, 180);  /* Eigene Farbe für den metricButton */
            color: white;
            border: 1px solid rgb(120, 120, 120);
            border-radius: 4px;
            padding: 4px;
            font-size: 12pt;
            font-weight: bold;
        }
        QToolButton#metricButton:hover {
            background-color: rgb(100, 149, 237);
        }
        
        QComboBox#metricButton {
            background-color: rgb(70, 130, 180);  /* Eigene Farbe für den metricButton */
            color: white;
            border: 1px solid rgb(120, 120, 120);
            border-radius: 4px;
            padding: 4px;
            font-size: 12pt;
            font-weight: bold;
        }
        QComboBox#metricButton:hover {
            background-color: rgb(100, 149, 237);
        }
        QPushButton#toggleButton,
        QPushButton#uploadButton,
        QPushButton#analyzeButton,
        QPushButton#fastSearchButton,
        QPushButton#resetMetricsButton,
        QPushButton#toggleAdvancedButton{
            background-color: rgb(80, 80, 80);   /* dezentes Mittelgrau */
            color: white;
            border: 1px solid rgb(120, 120, 120);
            border-radius: 4px;
            padding: 4px;
            font-size: 14pt;
            font-weight: bold;
        }
        QPushButton#toggleButton:hover,
        QPushButton#uploadButton:hover,
        QPushButton#analyzeButton:hover,
        QPushButton#fastSearchButton:hover,
        QPushButton#resetMetricsButton:hover,
        QPushButton#toggleAdvancedButton:hover {
            background-color: rgb(100, 100, 100);  /* etwas heller beim Hover */
        }
                

    
    """)


def apply_light_fusion_palette(app):
    """
    Aktiviert den Fusion-Style mit einer hellen QPalette.
    """
    app.setStyle("Fusion")
    light_palette = QPalette()

    # Fenster- und Widget-Hintergrund
    light_palette.setColor(QPalette.Window, Qt.white)
    light_palette.setColor(QPalette.Base, Qt.white)
    light_palette.setColor(QPalette.AlternateBase, QColor(235, 235, 235))

    # Textfarbe
    light_palette.setColor(QPalette.WindowText, Qt.black)
    light_palette.setColor(QPalette.Text, Qt.black)

    # Buttons
    light_palette.setColor(QPalette.Button, Qt.white)
    light_palette.setColor(QPalette.ButtonText, Qt.black)

    # Auswahlelemente
    light_palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
    light_palette.setColor(QPalette.HighlightedText, Qt.white)

    # Tooltip
    light_palette.setColor(QPalette.ToolTipBase, Qt.white)
    light_palette.setColor(QPalette.ToolTipText, Qt.black)

    # Link-Farbe
    light_palette.setColor(QPalette.Link, QColor(0, 122, 204))

    app.setPalette(light_palette)
    app.setStyleSheet("""
                      
    * {
        font-weight: bold;
         }
    QSplitter::handle {
        background-color: rgba(0, 0, 0, 20);  /* leicht grau für hellen Hintergrund */
    }
    QSplitter::handle:hover {
        background-color: rgba(0, 0, 0, 40);
    }
    QToolButton#metricButton {
            border: 1px solid rgb(120, 120, 120);
            border-radius: 4px;
            padding: 4px;
            font-size: 12pt;
            font-weight: bold;
        }

        
    QComboBox#metricButton {
            border: 1px solid rgb(120, 120, 120);
            border-radius: 4px;
            padding: 4px;
            font-size: 12pt;
            font-weight: bold;
        }

    QPushButton#toggleButton,
    QPushButton#uploadButton,
    QPushButton#analyzeButton,
    QPushButton#fastSearchButton,
    QPushButton#resetMetricsButton,
    QPushButton#toggleAdvancedButton{
            border: 1px solid rgb(120, 120, 120);
            border-radius: 4px;
            padding: 4px;
            font-size: 14pt;
            font-weight: bold;
        }
""")



