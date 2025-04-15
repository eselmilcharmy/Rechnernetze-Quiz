# Quiz – Web-App 

Browserbasierter Fragenkatalog – ideal zum Üben von Multiple-Choice-Fragen. Sie ist inspiriert vom Aufbau klassischer Fahrschul-Apps, aber vollständig anpassbar.
Entwickelt mit Python, Dash, Pandas und Bootstrap.

---

## 🌐 Funktionen

- 📋 Lokaler Fragenkatalog (aus Excel/CSV importiert)
- 🎯 Multiple-Choice-Antworten mit Auswertung
- 💡 Fortschrittsanzeige
- 📱 Responsive Design

---

## 🛠️ Installation & Setup

### 🔁 Repository klonen

```bash
git clone https://github.com/eselmilcharmy/Rechnernetze-Quiz.git
cd Rechnernetze-Quiz
```

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

Navigiere im Terminal zum Projektordner (der Ordner, der die Datei `index.py` enthält).

### Windows/macOS/Linux:

```bash
python index.py
```

Die Anwendung startet automatisch unter:

```
http://127.0.0.1:8050/
```

---

## 🤝 Mitwirken

Pull Requests sind willkommen! Öffne bei Fragen gerne ein Issue.

---

## 📄 Lizenz

MIT © 2025 Albinot Hajrizaj
