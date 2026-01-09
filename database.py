import sqlite3

DB_NAME = "agenda.db"

def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            servico TEXT,
            data TEXT,
            horario TEXT
        )
    """)
    conn.commit()
    conn.close()

def horario_ocupado(data, horario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM agendamentos WHERE data=? AND horario=?",
        (data, horario)
    )
    existe = cursor.fetchone()
    conn.close()
    return existe is not None

def salvar_agendamento(cliente, servico, data, horario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agendamentos (cliente, servico, data, horario) VALUES (?, ?, ?, ?)",
        (cliente, servico, data, horario)
    )
    conn.commit()
    conn.close()

def horarios_ocupados(data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT horario FROM agendamentos WHERE data=?",
        (data,)
    )
    horarios = [row[0] for row in cursor.fetchall()]
    conn.close()
    return horarios