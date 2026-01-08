from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES
# =========================

HORARIO_ATENDIMENTO = {
    "semana_inicio": 9,
    "semana_fim": 18,
    "sabado_inicio": 9,
    "sabado_fim": 13
}

# =========================
# FUNÇÕES
# =========================

def dentro_do_horario():
    agora = datetime.now()
    hora = agora.hour
    dia = agora.weekday()

    if dia <= 4:
        return HORARIO_ATENDIMENTO["semana_inicio"] <= hora < HORARIO_ATENDIMENTO["semana_fim"]
    elif dia == 5:
        return HORARIO_ATENDIMENTO["sabado_inicio"] <= hora < HORARIO_ATENDIMENTO["sabado_fim"]
    else:
        return False

def menu_principal():
    return (
        "Olá! 👋\n"
        "Bem-vindo à *PANDA RACING DEVELOPMENT* 🐼🏁\n\n"
        "Escolha uma opção:\n\n"
        "1️⃣ Agendar serviço\n"
        "2️⃣ Informações gerais\n"
        "3️⃣ Falar com atendente"
    )

# =========================
# ROTAS
# =========================

@app.route("/", methods=["GET"])
def home():
    return "PANDA RACING DEVELOPMENT - Bot ativo"

@app.route("/simular", methods=["POST"])
def simular():
    data = request.get_json(silent=True) or {}
    texto = data.get("text", "").strip().lower()

    if texto in ["oi", "olá", "ola", "menu", "inicio", "início"]:
        resposta = menu_principal()

    elif texto == "1":
        resposta = (
            "📅 *Agendamento de serviço*\n\n"
            "Realizamos:\n"
            "🔧 Remap\n"
            "🔧 Revisões\n"
            "🔧 Manutenções em geral\n\n"
            "Envie:\n"
            "👉 Serviço desejado\n"
            "👉 Data e horário pretendidos"
        )

    elif texto == "2":
        resposta = (
            "ℹ️ *Informações*\n\n"
            "⚠️ Valores e mais detalhes sobre os serviços "
            "são informados somente presencialmente na oficina."
        )

    elif texto == "3":
        if dentro_do_horario():
            resposta = (
                "👨‍🔧 Atendimento humano disponível!\n"
                "Um atendente irá te responder em breve."
            )
        else:
            resposta = (
                "⏰ Atendimento humano:\n\n"
                "🗓️ Segunda a sexta: 9h às 18h\n"
                "🗓️ Sábado: 9h às 13h\n\n"
                "Deixe sua mensagem que retornaremos no próximo horário útil."
            )

    else:
        resposta = (
            "❓ Não entendi.\n\n"
            "Digite *menu* para ver as opções."
        )

    return jsonify({"resposta": resposta})

# =========================
# START
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
