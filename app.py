from flask import Flask, request, jsonify
from datetime import datetime
from database import criar_tabela, salvar_agendamento, horarios_ocupados

app = Flask(__name__)

# =========================
# INICIALIZA BANCO
# =========================
criar_tabela()

# =========================
# CONFIGURAÇÕES
# =========================

HORARIOS_DISPONIVEIS = ["09:00", "11:00", "13:00", "15:00", "17:00"]

HORARIO_ATENDIMENTO = {
    "semana_inicio": 9,
    "semana_fim": 18,
    "sabado_inicio": 9,
    "sabado_fim": 13
}

sessoes = {}

# =========================
# FUNÇÕES AUXILIARES
# =========================

def dentro_do_horario():
    agora = datetime.now()
    hora = agora.hour
    dia = agora.weekday()

    if dia <= 4:
        return HORARIO_ATENDIMENTO["semana_inicio"] <= hora < HORARIO_ATENDIMENTO["semana_fim"]
    if dia == 5:
        return HORARIO_ATENDIMENTO["sabado_inicio"] <= hora < HORARIO_ATENDIMENTO["sabado_fim"]
    return False

def menu_principal():
    return (
        "Olá! 👋\n"
        "Bem-vindo à *PANDA RACING DEVELOPMENT* 🐼🏁\n\n"
        "1️⃣ Agendar serviço\n"
        "2️⃣ Informações gerais\n"
        "3️⃣ Falar com atendente"
    )

def horarios_livres(data):
    ocupados = horarios_ocupados(data)
    return [h for h in HORARIOS_DISPONIVEIS if h not in ocupados]

# =========================
# ROTAS
# =========================

@app.route("/", methods=["GET"])
def home():
    return "PANDA RACING DEVELOPMENT - Bot ativo"

@app.route("/simular", methods=["POST"])
def simular():
    payload = request.get_json(silent=True) or {}
    texto = payload.get("text", "").strip()

    cliente_id = "cliente_teste"

    if cliente_id not in sessoes:
        sessoes[cliente_id] = {"estado": "menu"}

    estado = sessoes[cliente_id]["estado"]

    # ===== MENU =====
    if estado == "menu":
        if texto.lower() in ["oi", "olá", "ola", "menu", "inicio"]:
            return jsonify({"resposta": menu_principal()})

        if texto == "1":
            sessoes[cliente_id]["estado"] = "servico"
            return jsonify({"resposta": "🔧 Qual serviço você deseja?"})

        if texto == "2":
            return jsonify({
                "resposta": (
                    "ℹ️ Valores e mais informações sobre os serviços "
                    "são informados somente presencialmente na oficina."
                )
            })

        if texto == "3":
            if dentro_do_horario():
                return jsonify({"resposta": "👨‍🔧 Atendimento humano acionado. Aguarde."})
            return jsonify({
                "resposta": "⏰ Atendimento humano:\nSeg–Sex 9h às 18h\nSáb 9h às 13h"
            })

        return jsonify({"resposta": "Digite *menu* para começar."})

    # ===== SERVIÇO =====
    if estado == "servico":
        sessoes[cliente_id]["servico"] = texto
        sessoes[cliente_id]["estado"] = "data"
        return jsonify({"resposta": "📅 Qual data deseja? (ex: 20/09)"})

    # ===== DATA =====
    if estado == "data":
        data_ag = texto
        livres = horarios_livres(data_ag)

        if not livres:
            return jsonify({
                "resposta": "❌ Não há horários disponíveis para essa data. Escolha outra."
            })

        sessoes[cliente_id]["data"] = data_ag
        sessoes[cliente_id]["estado"] = "horario"

        lista = "\n".join([f"⏰ {h}" for h in livres])

        return jsonify({
            "resposta": (
                "Horários disponíveis:\n"
                f"{lista}\n\n"
                "Digite o horário desejado:"
            )
        })

    # ===== HORÁRIO =====
    if estado == "horario":
        data_ag = sessoes[cliente_id]["data"]
        livres = horarios_livres(data_ag)

        if texto not in livres:
            return jsonify({
                "resposta": "❌ Horário indisponível. Escolha um dos horários listados."
            })

        salvar_agendamento(
            cliente_id,
            sessoes[cliente_id]["servico"],
            data_ag,
            texto
        )

        sessoes[cliente_id]["estado"] = "confirmado"

        return jsonify({
            "resposta": (
                "✅ *Agendamento confirmado!*\n\n"
                f"🔧 Serviço: {sessoes[cliente_id]['servico']}\n"
                f"📅 Data: {data_ag}\n"
                f"⏰ Horário: {texto}\n\n"
                "Aguardamos você na PANDA RACING DEVELOPMENT 🐼🏁"
            )
        })

    return jsonify({"resposta": "Digite *menu* para reiniciar."})

# =========================
# START LOCAL
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
