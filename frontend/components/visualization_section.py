import os
import sys
import networkx as nx
import numpy as np

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage

from vispy import scene
from vispy.scene import visuals, cameras
from vispy.scene import transforms
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QFileDialog

# Funktionen zum Einlesen der GraphML-Datei
def load_graph(graphml_path):
    try:
        G = nx.read_graphml(graphml_path)
        print(f"Graph geladen: {G.number_of_nodes()} Knoten, {G.number_of_edges()} Kanten")
        return G
    except Exception as e:
        print("Fehler beim Laden der GraphML-Datei:", e)
        return None

#  Funktion zur Layout-Berechnung 
def compute_layout(G, k=0.1, iterations=50):
    try:
        pos = nx.spring_layout(G, k=k, iterations=iterations)
        return pos
    except Exception as e:
        print("Fehler bei der Layout-Berechnung:", e)
        return None

#  QThread für asynchrone Layout-Berechnung 
class LayoutWorker(QThread):
    layout_ready = pyqtSignal(dict)

    def __init__(self, G, k=0.1, iterations=200):
        super().__init__()
        self.G = G
        self.k = k
        self.iterations = iterations
        self._stop_requested = False

    def run(self):
        pos = compute_layout(self.G, k=self.k, iterations=self.iterations)
        if pos is not None and not self._stop_requested:
            self.layout_ready.emit(pos)

    def stop(self):
        self._stop_requested = True

#  VisPy-Canvas mit permanenten Labels und Drag & Drop (optimiert) 
class NetworkCanvas(scene.SceneCanvas):
    def __init__(self, G, pos, highlight_nodes=None, highlight_periphery=None, parent=None):
        super().__init__(keys='interactive', show=True, parent=parent, bgcolor='white')
        self.unfreeze()

        # interne Daten
        self._G = G
        self._pos = pos.copy()
        self._node_list = list(G.nodes())
        self.highlight_nodes = set(highlight_nodes or [])
        self.highlight_periphery = set(highlight_periphery or [])
        self.picked_node = None

        # View & Camera (Zoom & Pan)
        self.view = self.central_widget.add_view()
        self.camera = cameras.PanZoomCamera(aspect=1)
        self.view.camera = self.camera
        self.view.camera.set_range()

        # Graph, Marker, Kanten, Labels initial zeichnen
        self._draw_graph()
        # Legende einrichten
        # Node im Canvas-Raum (unabhängig von Pan/Zoom)
        self.legend_node = scene.Node(parent=self.scene)
        # Marker + Texte 
        self._draw_legend()
        # Fenstresize abfangen, um Legend-Position anzupassen
        self.events.resize.connect(self._update_legend_position)
        # Einmal initial positionieren
        self._update_legend_position()

        # Maus-Events für Drag & Drop
        self.events.mouse_press.connect(self.on_mouse_press)
        self.events.mouse_move.connect(self.on_mouse_move)
        self.events.mouse_release.connect(self.on_mouse_release)

        self.freeze()

    def _draw_graph(self):
        nodes     = self._node_list
        positions = np.array([self._pos[n] for n in nodes])

        # Marker-Farben
        center_color    = (0.20, 0.60, 0.86, 1.0)  # Blau
        periphery_color = (0.95, 0.61, 0.07, 1.0)  # Orange
        default_color   = (0.56, 0.27, 0.68, 1.0)  # Purpur
        colors = [
            center_color    if n in self.highlight_nodes
            else periphery_color if n in self.highlight_periphery
            else default_color
            for n in nodes
        ]

        # Marker-Visual
        self.node_visual = visuals.Markers()
        self.node_visual.set_data(positions, face_color=colors, size=10)
        self.view.add(self.node_visual)

        # Kanten-Visual
        edge_lines = []
        for u, v in self._G.edges():
            edge_lines.extend([self._pos[u], self._pos[v], [np.nan, np.nan]])
        self.edge_visual = visuals.Line(np.array(edge_lines), color='gray', width=2)
        self.view.add(self.edge_visual)

        # Ein einziges Text-Visual für alle Labels
        labels    = [str(n) for n in nodes]
        label_pos = positions + np.array([0.0, 0.04])
        self.label_visual = visuals.Text(
            text=labels,
            pos=label_pos,
            color='black',
            font_size=10,
            anchor_x='center',
            anchor_y='bottom',
            parent=self.view.scene
        )

    def update_graph(self, G, pos):
        # Neue Daten übernehmen
        self._G = G
        self._pos = pos.copy()
        self._node_list = list(G.nodes())

        nodes     = self._node_list
        positions = np.array([self._pos[n] for n in nodes])

        # Marker-Farben aktualisieren
        center_color    = (0.20, 0.60, 0.86, 1.0)  # Blau
        periphery_color = (0.95, 0.61, 0.07, 1.0)  # Orange
        default_color   = (0.56, 0.27, 0.68, 1.0)  # Purpur

        colors = [
            center_color    if n in self.highlight_nodes
            else periphery_color if n in self.highlight_periphery
            else default_color
            for n in nodes
        ]
        self.node_visual.set_data(positions, face_color=colors, size=10)

        # Kanten aktualisieren
        edge_lines = []
        for u, v in self._G.edges():
            edge_lines.extend([self._pos[u], self._pos[v], [np.nan, np.nan]])
        self.edge_visual.set_data(np.array(edge_lines))

        # Labels aktualisieren 
        labels    = [str(n) for n in nodes]
        label_pos = positions + np.array([0.0, 0.04])
        self.label_visual.text = labels
        self.label_visual.pos  = label_pos

        self.update()

    def on_mouse_press(self, event):
        if event.button == 1:
            mapped   = self.view.camera.transform.imap(event.pos)
            data_pos = np.array(mapped[:2])
            coords   = np.array([self._pos[n] for n in self._node_list])
            dists    = np.linalg.norm(coords - data_pos, axis=1)
            idx      = int(np.argmin(dists))
            if dists[idx] < 0.05:
                self.picked_node       = idx
                self.camera.interactive = False

    def on_mouse_move(self, event):
        if self.picked_node is not None and event.is_dragging:
            mapped   = self.view.camera.transform.imap(event.pos)
            new_pos  = np.array(mapped[:2])
            node_id  = self._node_list[self.picked_node]
            self._pos[node_id] = new_pos
            self.update_graph(self._G, self._pos)

    def on_mouse_release(self, event):
        if self.picked_node is not None:
            self.picked_node       = None
            self.camera.interactive = True

    def _draw_legend(self):
        # Center (Blau)
        blue = visuals.Markers(parent=self.legend_node)
        blue.set_data(np.array([[0,   0]]),
                    face_color=(0.20, 0.60, 0.86, 1.0),
                    size=10)
        visuals.Text(
            text='Center',
            pos=[(15,   0)],
            color='black',
            font_size=14,
            anchor_x='left',
            anchor_y='center',
            parent=self.legend_node
        )

        # Periphery (Orange)
        orange = visuals.Markers(parent=self.legend_node)
        orange.set_data(np.array([[0, -25]]),
                        face_color=(0.95, 0.61, 0.07, 1.0),
                        size=10)
        visuals.Text(
            text='Periphery',
            pos=[(15, -25)],
            color='black',
            font_size=14,
            anchor_x='left',
            anchor_y='center',
            parent=self.legend_node
        )

        # Default (Purpur)
        purple = visuals.Markers(parent=self.legend_node)
        purple.set_data(np.array([[0, -50]]),
                        face_color=(0.56, 0.27, 0.68, 1.0),
                        size=10)
        visuals.Text(
            text='Default',
            pos=[(15, -50)],
            color='black',
            font_size=14,
            anchor_x='left',
            anchor_y='center',
            parent=self.legend_node
        )


    def _update_legend_position(self, event=None):
        # immer 20px vom linken, 20px vom oberen Rand
        w, h = self.size
        self.legend_node.transform = transforms.STTransform(
            translate=(20, h - 20)
        )

    

    

# PyQt-Widget zur Einbettung und Reaktivität 
class VisualizationSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.canvas = None
        self.worker = None
        self._highlight_nodes = set()
        self._highlight_periphery = set()

    def load_graph_from_path(self, graphml_path, highlight_nodes=None, highlight_periphery=None):
        G = load_graph(graphml_path)
        if G is None:
            return
        pos0 = compute_layout(G, k=0.1, iterations=50)
        if pos0 is None:
            return

        self._highlight_nodes = set(highlight_nodes or [])
        self._highlight_periphery = set(highlight_periphery or [])

        if self.canvas is None:
            self.canvas = NetworkCanvas(
                G, pos0,
                highlight_nodes=self._highlight_nodes,
                highlight_periphery=self._highlight_periphery,
                parent=self
            )
            self.layout().addWidget(self.canvas.native)
            #  Kontextmenü aktivieren
            self.canvas.native.setContextMenuPolicy(Qt.CustomContextMenu)
            #  Signal verbinden
            self.canvas.native.customContextMenuRequested.connect(self._show_context_menu)

        else:
            self.canvas.highlight_nodes = self._highlight_nodes
            self.canvas.highlight_periphery = self._highlight_periphery
            self.canvas.update_graph(G, pos0)

        # Asynchrones Feintuning
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.worker = LayoutWorker(G, k=0.1, iterations=200)
        self.worker.layout_ready.connect(lambda new_pos: self.canvas.update_graph(G, new_pos))
        self.worker.start()

        print("Graph & Layout initial geladen; Feintuning läuft.")

    def get_generated_image(self):
        """
        Erfasst das aktuell dargestellte Bild des VisPy-Canvas und gibt es als QImage zurück.
        """
        if self.canvas:
            # Das Canvas rendert in ein NumPy-Array im Format (Höhe, Breite, 4) (RGBA)
            image_array = self.canvas.render()
            if image_array.ndim == 3 and image_array.shape[2] == 4:
                height, width, channels = image_array.shape
                bytes_per_line = width * 4  # 4 Bytes pro Pixel (RGBA)
                # Konvertiere den memoryview in bytes
                data_bytes = image_array.tobytes()
                image = QImage(data_bytes, width, height, bytes_per_line, QImage.Format_RGBA8888)
                # Gib eine Kopie zurück, um Probleme mit dem internen Speicher zu vermeiden
                return image.copy()
            else:
                print("Unerwartetes Bildformat:", image_array.shape)
                return None
        else:
            print("Kein Canvas vorhanden!")
            return None
        
    def _show_context_menu(self, pos):
        menu = QMenu(self)
        save_act = menu.addAction("Bild speichern…")
        # Menü 
        action = menu.exec_(self.canvas.native.mapToGlobal(pos))
        if action == save_act:
            img = self.get_generated_image()
            if img is not None:
                # Speichern-Dialog
                fname, _ = QFileDialog.getSaveFileName(
                    self,
                    "Graph als Bild speichern",
                    "",
                    "PNG-Bild (*.png);;JPEG-Bild (*.jpg *.jpeg)"
                )
                if fname:
                    img.save(fname)

