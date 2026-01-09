import sqlite3

def conectar():
    return sqlite3.connect("agenda.db", check_same_thread=False)

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horario TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def salvar_horario(horario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agendamentos (horario) VALUES (?)",
        (horario,)
    )
    conn.commit()
    conn.close()

def horarios_ocupados():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT horario FROM agendamentos")
    dados = cursor.fetchall()
    conn.close()
    return [h[0] for h in dados]
