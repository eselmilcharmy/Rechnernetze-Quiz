# from asyncio.windows_events import NULL
import os
import random
import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go

# -------------------------------------------------------------
# Fallback-Funktion: CSV oder XLSX einlesen
# -------------------------------------------------------------
def load_quiz_data():
    """
    Versucht, quiz_data.csv einzulesen.
    Falls das fehlschlägt oder nicht existiert,
    wird quiz_data.xlsx gelesen.
    Danach werden die wichtigen Spalten geprüft.
    """
    data_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Data"
    )

    CSV_FILE = os.path.join(data_folder, "quiz_data.csv")
    XLSX_FILE = os.path.join(data_folder, "quiz_data.xlsx")

    required_columns = {"type","frage","solution","a","b","c","d","e","f","info"}

    df = None

    # 1) CSV versuchen
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            print(f"CSV '{CSV_FILE}' erfolgreich geladen.")
        except Exception as e:
            print(f"Fehler beim Einlesen der CSV '{CSV_FILE}': {e}")
            df = None

    # 2) Fallback: Excel
    if df is None:
        if os.path.exists(XLSX_FILE):
            try:
                df = pd.read_excel(XLSX_FILE)
                print(f"Excel '{XLSX_FILE}' erfolgreich geladen.")
            except Exception as e:
                raise FileNotFoundError(
                    f"Fehler beim Einlesen von '{XLSX_FILE}'.\n"
                    f"Ursprünglicher Fehler: {e}"
                )
        else:
            raise FileNotFoundError(
                f"Weder CSV '{CSV_FILE}' noch XLSX '{XLSX_FILE}' gefunden."
            )

    # 3) Spaltencheck
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Die Daten-Datei muss mindestens diese Spalten enthalten: {required_columns}"
        )

    df = df[((df["info"].isna()) | (df["info"] == "falsch")) & ((df["type"] == "MC") | (df["type"] == "FT"))]

    return df

# -------------------------------------------------------------
# Daten einlesen
# -------------------------------------------------------------
df = load_quiz_data()

# -------------------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------------------
def shuffle_questions(dataframe):
    indices = list(dataframe.index)
    random.shuffle(indices)
    return indices

def init_quiz(dataframe):
    question_order = shuffle_questions(dataframe)
    return question_order, 0, 0, False

def restart_quiz(dataframe):
    new_order = shuffle_questions(dataframe)
    return new_order, 0, 0, False

def get_question_data(df, idx):
    row = df.loc[idx]
    qtype = str(row["type"]).strip().upper()  # "MC" oder "FT"
    frage = str(row["frage"])
    solution_letters = str(row["solution"]).split(";")  # z.B. "b;e"
    mc_dict = {
        "a": str(row["a"]),
        "b": str(row["b"]),
        "c": str(row["c"]),
        "d": str(row["d"]),
        "e": str(row["e"]),
        "f": str(row["f"]),
    }
    return qtype, frage, solution_letters, mc_dict

def build_mc_options(mc_dict, disabled=False):
    options = []
    
    for letter in ["a", "b", "c", "d", "e", "f"]:
        txt = mc_dict.get(letter)
        
        if txt is not None and str(txt).strip() and str(txt).lower() != "nan":
            opt = {
                "label": txt,
                "value": letter,
                "disabled": disabled
            }
            options.append(opt)
    
    return options

def highlight_correct_answers(mc_dict, correct_letters):
    new_options = []
    correct_set = set(correct_letters)
    for letter in ["a","b","c","d","e","f"]:
        text = mc_dict.get(letter)
        style = {}
        disabled = True
        if letter in correct_set:
            style = {"backgroundColor": "#d4edda"}  # helgrün
        if text is not None and str(text).strip() and str(text).lower() != "nan": 
            new_options.append({
                "label": html.Span(text, style=style),
                "value": letter,
                "disabled": disabled
        })
    return new_options

def _split_and_clean(text):
    """
    Zerlegt text in tokens, ignoriert Groß/Klein, trennt an ; , -
    """
    if not text:
        return set()
    tmp = text.replace(";", ",").replace("-", ",")
    tokens = tmp.split(",")
    cleaned = [t.strip().lower() for t in tokens if t.strip()]
    return set(cleaned)

def check_question(qtype, solution_letters, mc_dict, user_checklist, user_text, revealed):
    if revealed:
        # Schon aufgedeckt
        return ("", True, False, [])

    # Multiple Choice
    if qtype == "MC":
        correct_set = set(solution_letters)
        user_set = set(user_checklist or [])
        is_correct = (user_set == correct_set)
        if is_correct:
            feedback = "Richtig (MC)!"
        else:
            feedback = f"Falsch! Richtige Lösung(en): {','.join(solution_letters)}"
        new_options = highlight_correct_answers(mc_dict, solution_letters)
        return (feedback, True, is_correct, new_options)

    # Freitext
    elif qtype == "FT":
        user_tokens = _split_and_clean(user_text)
        is_correct = False
        feedback = "Falsch! (Freitext)"

        for letter in solution_letters:
            correct_text_clean = _split_and_clean(mc_dict[letter])
            if user_tokens == correct_text_clean and len(user_tokens) > 0:
                is_correct = True
                break

        if is_correct:
            feedback = "Richtig (FT)!"
        else:
            correct_texts = [mc_dict[l] for l in solution_letters]
            if len(correct_texts) == 1:
                feedback = f"Falsch! Richtige Antwort: {correct_texts[0]}"
            else:
                feedback = "Falsch! Richtige Antworten: " + ", ".join(correct_texts)

        return (feedback, True, is_correct, [])

    # Fallback
    return ("Unbekannter Typ!", True, False, [])

def next_question(current_idx, score, is_correct):
    if is_correct:
        score += 1
    current_idx += 1
    revealed = False
    return current_idx, score, revealed

def update_ui(question_order, current_idx, revealed, df, current_mc_options):
    if not question_order:
        return "Keine Fragen vorhanden.", 0, [], "???"

    total = len(question_order)
    if current_idx >= total:
        return "Quiz beendet!", 100, [], "???"

    idx = question_order[current_idx]
    qtype, frage, solution_letters, mc_dict = get_question_data(df, idx)
    progress_value = int((current_idx / total) * 100)

    if qtype == "MC":
        if not revealed:
            mc_opts = build_mc_options(mc_dict, disabled=False)
        else:
            mc_opts = current_mc_options
        return frage, progress_value, mc_opts, qtype
    else:
        return frage, progress_value, [], qtype

def update_statistics(question_order, current_idx, score):
    total = len(question_order) if question_order else 0
    if current_idx >= total and total > 0:
        return f"Endergebnis: {score} von {total} korrekt!"
    else:
        return f"Aktueller Punktestand: {score} / {total}."

# -------------------------------------------------------------
# Dash-App
# -------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Titel + Layout
header = dbc.Row(
    dbc.Col(html.H2("Rechnernetze-Quiz", 
                    className="text-center my-4"), width=12)
)

progress_bar = dbc.Progress(id="progress-bar", value=0, striped=True, animated=True, className="mb-4")
question_text = html.Div(id="question-text", className="mb-3", style={"fontSize":"1.25rem","fontWeight":"bold"})

checkboxes = dbc.Checklist(id="answer-checklist", options=[], value=[], inline=False)
answer_input = dbc.Input(id="answer-input", type="text", placeholder="(Freitext eingeben...)")

feedback_text = html.Div(id="feedback-text", className="mt-3", style={"fontSize":"1rem","fontStyle":"italic"})

btn_check = dbc.Button("Auflösen", id="btn-check", color="primary", className="me-2 mb-2")
btn_next = dbc.Button("Nächste Frage", id="btn-next", color="secondary", className="me-2 mb-2")
btn_restart = dbc.Button("Quiz erneut starten", id="btn-restart", color="danger", className="mb-2")
btn_repeat_mistakes = dbc.Button("Falsche Fragen erneut lernen", id="btn-repeat-mistakes",
                                 color="warning", className="mb-2", style={"display":"none"})

buttons = dbc.Row([
    dbc.Col(btn_check, width="auto"),
    dbc.Col(btn_next, width="auto"),
    dbc.Col(btn_restart, width="auto"),
    dbc.Col(btn_repeat_mistakes, width="auto"),
], justify="center")

statistics_text = html.Div(id="statistics-text", className="mt-4",
                           style={"fontSize":"1.1rem","fontWeight":"bold","textAlign":"center"})

# Copyright
footer = html.Div(
    "© 2025 Albinot Hajrizaj",
    style={"fontSize": "0.9rem", "textAlign": "center", "marginTop": "30px"}
)

app.layout = dbc.Container([
    header,
    progress_bar,
    question_text,
    checkboxes,
    answer_input,
    feedback_text,
    buttons,
    statistics_text,

    # Hier fügen wir den Footer ein
    footer,

    # Stores
    dcc.Store(id="store-question-order"),
    dcc.Store(id="store-current-index", data=0),
    dcc.Store(id="store-score", data=0),
    dcc.Store(id="store-revealed", data=False),
    dcc.Store(id="store-current-mc-options", data=[]),
    dcc.Store(id="store-last-correct", data=False),

    # Falsche Fragen
    dcc.Store(id="store-incorrect-questions", data=[]),

], fluid=True)

# -------------------------------------------------------------
# Callback
# -------------------------------------------------------------
@app.callback(
    # Alle Outputs
    Output("store-question-order", "data"),
    Output("store-current-index", "data"),
    Output("store-score", "data"),
    Output("store-revealed", "data"),
    Output("store-current-mc-options", "data"),
    Output("store-last-correct", "data"),

    Output("question-text", "children"),
    Output("progress-bar", "value"),
    Output("answer-checklist", "options"),
    Output("answer-checklist", "value"),
    Output("answer-input", "value"),
    Output("feedback-text", "children"),
    Output("statistics-text", "children"),

    Output("answer-checklist", "style"),
    Output("answer-input", "style"),
    Output("btn-check", "style"),
    Output("btn-next", "style"),
    Output("btn-repeat-mistakes", "style"),

    Output("store-incorrect-questions", "data"),  # Falsche Fragen

    Input("btn-restart", "n_clicks"),
    Input("btn-next", "n_clicks"),
    Input("btn-check", "n_clicks"),
    Input("btn-repeat-mistakes", "n_clicks"),

    State("store-question-order", "data"),
    State("store-current-index", "data"),
    State("store-score", "data"),
    State("store-revealed", "data"),
    State("store-current-mc-options", "data"),
    State("store-last-correct", "data"),

    State("answer-checklist", "value"),
    State("answer-input", "value"),

    State("store-incorrect-questions", "data"),

    prevent_initial_call=False
)
def master_callback(n_restart,
                    n_next,
                    n_check,
                    n_repeat,
                    question_order,
                    current_idx,
                    score,
                    revealed,
                    current_mc_options,
                    last_correct,
                    user_checklist,
                    user_text,
                    incorrect_list):

    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""
    feedback = ""

    # 1) Initialisierung
    if question_order is None:
        question_order, current_idx, score, revealed = init_quiz(df)
        current_mc_options = []
        last_correct = False
        incorrect_list = []

    # 2) Quiz erneut starten
    if triggered_id == "btn-restart" and n_restart:
        question_order, current_idx, score, revealed = restart_quiz(df)
        current_mc_options = []
        last_correct = False
        user_checklist = []
        user_text = ""
        feedback = ""
        incorrect_list = []

    # 2.1) Falsche Fragen erneut lernen
    if triggered_id == "btn-repeat-mistakes" and n_repeat:
        if incorrect_list:
            random.shuffle(incorrect_list)
            question_order = incorrect_list
            current_idx = 0
            score = 0
            revealed = False
            current_mc_options = []
            last_correct = False
            user_checklist = []
            user_text = ""
            feedback = ""
            # Leere die Liste, damit man nicht endlos
            incorrect_list = []

    # 3) Auflösen
    if triggered_id == "btn-check" and n_check:
        if question_order and current_idx < len(question_order):
            qtype, frage, solution_letters, mc_dict = get_question_data(df, question_order[current_idx])
            fb, new_revealed, is_correct, new_opts = check_question(
                qtype, solution_letters, mc_dict, user_checklist, user_text, revealed
            )
            feedback = fb
            revealed = new_revealed
            last_correct = is_correct

            if qtype == "MC":
                current_mc_options = new_opts
        else:
            feedback = "Keine Frage mehr verfügbar."
            revealed = True
            last_correct = False

    # 4) Nächste Frage
    if triggered_id == "btn-next" and n_next:
        if revealed and question_order and current_idx < len(question_order):
            old_idx = question_order[current_idx]
            if not last_correct:
                # Frage war falsch -> merken
                if old_idx not in incorrect_list:
                    incorrect_list.append(old_idx)

            current_idx, score, revealed = next_question(current_idx, score, last_correct)
        else:
            current_idx += 1
            revealed = False

        user_checklist = []
        user_text = ""
        feedback = ""
        current_mc_options = []
        last_correct = False

    # 5) UI aktualisieren
    frage, progress_value, mc_opts, qtype = update_ui(question_order, current_idx, revealed, df, current_mc_options)
    if mc_opts:
        current_mc_options = mc_opts

    stats_text = update_statistics(question_order, current_idx, score)

    # 6) Dynamische Styles
    checklist_style = {"display": "block"}
    input_style = {"display": "block"}
    btn_check_style = {"display": "inline-block"}    # Standard: Auflösen sichtbar
    btn_next_style = {"display": "inline-block"}
    repeat_btn_style = {"display": "none"}

    # a) Quiz-Ende?
    if question_order and current_idx >= len(question_order):
        # Quiz beendet
        checklist_style = {"display": "none"}
        input_style = {"display": "none"}
        btn_check_style = {"display": "none"}
        btn_next_style = {"display": "none"}

        if incorrect_list:
            repeat_btn_style = {"display": "inline-block"}
    else:
        # Quiz läuft
        # Nächste Frage erst, wenn revealed == True
        if not revealed:
            # Frage nicht aufgedeckt:
            # -> "Nächste Frage" verstecken
            btn_next_style = {"display": "none"}
            # -> "Auflösen" anzeigen
        else:
            # Frage aufgedeckt
            # -> "Auflösen" verstecken
            btn_check_style = {"display": "none"}
            # -> "Nächste Frage" anzeigen

        # MC oder FT?
        if qtype == "MC":
            input_style = {"display": "none"}
        elif qtype == "FT":
            checklist_style = {"display": "none"}

    return (
        question_order,
        current_idx,
        score,
        revealed,
        current_mc_options,
        last_correct,

        frage,
        progress_value,
        current_mc_options,
        user_checklist,
        user_text,
        feedback,
        stats_text,

        checklist_style,
        input_style,
        btn_check_style,
        btn_next_style,
        repeat_btn_style,

        incorrect_list
    )

# -------------------------------------------------------------
# Start
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
