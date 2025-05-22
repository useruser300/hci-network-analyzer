# HCI Network Analyzer – Lokale Testumgebung / Local Test Environment

Dieses Repository enthält den Quellcode eines im Rahmen einer Bachelorarbeit entwickelten Tools zur automatisierten Netzwerkanalyse. Die Anwendung kombiniert Methoden der strukturellen Netzwerkanalyse mit Prinzipien der Human-Computer Interaction (HCI) und bietet eine grafische Benutzeroberfläche (GUI) zur Analyse, Visualisierung und dem Export von Netzwerkdaten.

This repository contains the source code of a tool developed as part of a Bachelor's thesis on automated network analysis. The application combines methods from structural network analysis with principles from Human-Computer Interaction (HCI) and provides a graphical user interface (GUI) for importing, analyzing, visualizing, and exporting network data.

---

## Übersicht / Overview

- Unterstützte Formate / Supported formats: `.graphml`, `.xml`, `.cch`, `.txt`
- Netzwerkmetriken / Network metrics: Degree, Betweenness, Density, Connectivity, Periphery, etc.
- HCI-basiertes GUI-Design / HCI-based GUI design (Dark/Light mode, tooltips, feedback indicators)
- Exportformate / Export options: JSON, CSV, PDF
- SQLite-Datenbank / SQLite-based data storage
- Evaluation: Usability-Tests und heuristische Analyse (SUS-Score: 78,5) / Evaluation: Usability tests and heuristic analysis (SUS score: 78.5)

---

## Systemanforderungen / System Requirements

Getestet mit / Tested with:

- Miniconda (conda 25.1.1)
- Python 3.11.8
- PyQt5 5.15.10
- matplotlib 3.10.1, networkx 3.4.2, vispy 0.14.3
- macOS Sequoia 15.3.1, Ubuntu 22.04 LTS

---

## Lokale Ausführung / Local Installation

❗ Voraussetzung / Requirement: Eine funktionierende Installation von Miniconda / A working installation of Miniconda  
Download: https://docs.conda.io/en/latest/miniconda.html

### 1. Repository klonen / Clone the repository

```bash
git clone https://github.com/useruser300/hci-network-analyzer.git
cd hci-network-analyzer
```

### 2. Conda-Umgebung einrichten / Create the Conda environment

```bash
conda env create -f environment.yml
conda activate myenv
```

Die Umgebung heißt standardmäßig `myenv`. / The default environment name is `myenv`.

### 3. Anwendung starten / Launch the application

```bash
python start.py
```

Das Tool startet im GUI-Modus mit Zugriff auf die beiden Hauptmodule. / The application starts in GUI mode and provides access to the two main modules.

---

## Funktionen & Nutzung / Features and Usage

### Einzelgraph-Analyse / Single Graph Analysis

Im Tab „Einzelgraph-Analyse“ findest du:  
Accessible via the "Einzelgraph-Analyse" tab:

- Eine Filtersektion / A filtering section
- Eine Ergebnistabelle / A table of computed metrics
- Eine interaktive Visualisierung / An interactive network visualization (VisPy-based)

Funktionen / Functions:

- Schnellsuche nach Dateinamen / Quick search for filenames
- Erweiterte Filter / Advanced filtering (e.g., node/edge count, density, centrality)
- Auswahl von Metriken / Metric selection menu

Tabelle / Table View:

- Größenanpassung von Spalten/Zeilen / Resizable columns and rows
- Flexible Aufteilung (QSplitter) / Adjustable layout using QSplitter
- Doppelklick für Visualisierung / Double-click to open visualization

Visualisierung / Visualization:

- Zoom & Pan
- Hover-Tooltips (Knotennamen / node names)
- Drag & Drop von Knoten / Drag and drop of nodes

### Datensatzanalyse / Dataset Analysis

Im Tab „Datensatz-Analyse“ kannst du:  
Available via the "Datensatz-Analyse" tab:

- Eine Datenquelle wählen / Select a data source (e.g., "TopologyZoo", "SNDlib")
- Analyse laden / Load analysis results

Diagramme / Charts:

1. Metriken zwischen 0–1 (z. B. Dichte) / Normalized metrics (e.g., density, efficiency)
2. Reelle Werte (z. B. Knotenzahl) / Raw-value metrics (e.g., node count, diameter)

Zusätzliche Optionen / Additional controls:

- Metriken ein-/ausblenden / Show or hide selected metrics
- Auf Standardwerte zurücksetzen / Reset to default values
- Automatische Aktualisierung / Diagrams update automatically

---

## Beispieldaten / Example Data

Im Ordner `datasets-testen/` befinden sich Beispieldatensätze aus:  
The `datasets-testen/` folder contains datasets from:

- Topology Zoo (`.graphml`)
- SNDlib (`.xml`)
- Rocketfuel (`.cch`)
- CAIDA (`.txt`)

Diese können direkt in der GUI importiert werden.  
These can be directly imported into the application for testing and analysis.