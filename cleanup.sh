#!/bin/bash

echo "Starte Bereinigung..."

# Lösche die SQLite-Datenbank
rm -rf network_analysis.db
echo "SQLite-Datenbank gelöscht."

# Lösche temporäre Uploads
rm -rf temp_uploads
echo "Temporäre Uploads gelöscht."

# Lösche Python-Cache-Ordner
rm -rf backend/__pycache__
rm -rf backend/analyzers/__pycache__
rm -rf backend/converters/__pycache__
rm -rf frontend/components/__pycache__
rm -rf frontend/__pycache__
echo "Python-Cache gelöscht."

echo "Bereinigung abgeschlossen!"

