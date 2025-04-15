# Interaktives Quiz (Dash)

Dies ist eine interaktive Quiz-Webanwendung, entwickelt mit Python, Dash, Bootstrap und Plotly. Sie lädt Fragen aus einer CSV- oder XLSX-Datei und bietet Multiple-Choice- sowie Freitext-Fragen mit Auswertungsfunktion.

---

## 📦 Voraussetzungen

- Python 3.8 oder höher
- Pip (Python-Paketmanager)

### 🧰 Benötigte Python-Bibliotheken:

Installiere die erforderlichen Pakete mit folgendem Befehl:

```bash
pip install dash dash-bootstrap-components pandas plotly openpyxl
```

---

## 🗂️ Datenstruktur

Die Fragen müssen sich in einer Datei namens `quiz_data.csv` **oder** `quiz_data.xlsx` im Ordner `Data` befinden. Die Datei muss folgende Spalten enthalten:

- `type` – `MC` (Multiple Choice) oder `FT` (Freitext)
- `frage` – Die Fragestellung
- `solution` – Die richtige(n) Antwort(en), z. B. `a` oder `b;e`
- `a`, `b`, `c`, `d`, `e`, `f` – Antwortoptionen (auch bei Freitext)
- `info` – `falsch` oder leer, um die Frage einzubeziehen

---

## 🖥️ Ausführen der App

Navigiere im Terminal zum Projektordner (der Ordner, der die Datei `app.py` enthält).

### Windows/macOS/Linux:

```bash
python app.py
```

Die Anwendung startet automatisch unter:

```
http://127.0.0.1:8050/
```

---

## 🔄 Funktionen

- Zufällige Frageauswahl
- MC- oder Freitextmodus
- Sofortige Auswertung der Antworten
- Punktestand-Tracking
- „Falsche Fragen erneut lernen“-Funktion
- Fortschrittsbalken

---

## 📁 Projektstruktur (Beispiel)

```
quiz-app/
├── app.py
├── Data/
│   └── quiz_data.csv
```

---

## 👤 Autor

[Albinot Hajrizaj](mailto:albinot.hajrizaj@example.com)  
© 2025

---

## 📃 Lizenz

MIT License
