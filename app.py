from flask import Flask, request, jsonify
import requests
from database import criar_tabela, salvar_horario, horarios_ocupados

app = Flask(__name__)
criar_tabela()
VERIFY_TOKEN = "panda_verify"

@app.route("/webhook/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():

    # Verificação do Meta
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "erro"

    dados = request.json

    try:
        msg = dados["entry"][0]["changes"][0]["value"]["messages"][0]
        numero = msg["from"]
        texto = msg["text"]["body"]
    except:
        return "ok"

    # REAPROVEITA SUA LÓGICA ATUAL
    resposta_texto = resposta(texto)  # ou processar_bot(texto)
    enviar_whatsapp(numero, resposta_texto)

    return "ok"

BOT_TOKEN = 7582315674AAHE8PjojORKJJawbZKcSLpfsjs-eIN5px4
TELEGRAM_API = f"https://api.telegram.org/bot7582315674:AAHE8PjojORKJJawbZKcSLpfsjs-eIN5px4"
ATENDENTE_ID = 123456789  # seu chat_id do Telegram

HORARIOS_FIXOS = ["09:00", "11:00", "13:00", "15:00", "17:00"]

# Guarda o estado do atendimento de cada cliente
estado = {}  # ex: {chat_id: {"modo": "bot"}}

def enviar(chat_id, texto):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown"
    })

def horarios_disponiveis():
    ocupados = horarios_ocupados()
    return [h for h in HORARIOS_FIXOS if h not in ocupados]

def resposta(texto):
    return jsonify({"reply": texto.strip()})

@app.route("/", methods=["GET"])
def home():
    return "Bot PANDA RACING DEVELOPMENT ativo 🐼"

@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.json
    chat_id = dados.get("chat_id")
    texto = dados.get("message", "").strip()
    texto_lower = texto.lower()

    # --- Verifica se é o atendente respondendo ---
    if chat_id == ATENDENTE_ID:
        if texto.startswith("/r"):
            try:
                _, cliente_id, *mensagem = texto.split()
                enviar(int(cliente_id), " ".join(mensagem))
            except Exception:
                enviar(ATENDENTE_ID, "Erro no comando /r. Use: /r <chat_id> <mensagem>")
        elif texto.startswith("/fim"):
            try:
                _, cliente_id = texto.split()
                estado[int(cliente_id)] = {"modo": "bot"}
                enviar(int(cliente_id), "🤖 Atendimento finalizado. Posso ajudar em algo mais?")
            except Exception:
                enviar(ATENDENTE_ID, "Erro no comando /fim. Use: /fim <chat_id>")
        return "ok"

    # --- Verifica se o cliente já está no modo humano ---
    modo = estado.get(chat_id, {}).get("modo", "bot")
    if modo == "humano":
        enviar(ATENDENTE_ID, f"📩 Cliente {chat_id}:\n{texto}")
        return "ok"

    # --- FLUXO ORIGINAL DO BOT ---
    # MENU INICIAL
    if texto_lower in ["menu", "oi", "olá", "ola", "inicio", "start"]:
        return resposta("""
Olá! 👋  
Bem-vindo à *PANDA RACING DEVELOPMENT* 🐼🏁  

Por favor, escolha uma opção:

1️⃣ Serviços  
2️⃣ Informações gerais  
3️⃣ Falar com atendente  
4️⃣ Desmarcar agendamento
""")

    # SERVIÇOS
    if texto_lower == "1":
        return resposta("""
🔧 *Serviços Disponíveis*

1️⃣ Remap  
2️⃣ Manutenções  
3️⃣ Projetos  

Escolha uma opção:
""")

    # QUALQUER SERVIÇO → AGENDAMENTO
    if texto_lower in ["remap", "manutencoes", "manutenções", "projetos", "1", "2", "3"]:
        livres = horarios_disponiveis()
        if not livres:
            return resposta("No momento não há horários disponíveis.")
        lista = "\n".join(livres)
        return resposta(f"""
📅 *Agendamento de Atendimento*

Todos os valores e informações detalhadas são informados somente na oficina,
pois variam conforme o veículo.

Horários disponíveis:
{lista}

Digite o horário desejado (ex: 09:00)
""")

    # CONFIRMAR HORÁRIO
    if ":" in texto:
        livres = horarios_disponiveis()
        if texto in livres:
            salvar_horario(texto)
            return resposta(f"""
✅ *Agendamento Confirmado*

Seu atendimento foi agendado com sucesso para o horário selecionado.

📍 *PANDA RACING DEVELOPMENT*  
Rua Gonçalo Ferreira, 379  
Ponte Grande – Mogi das Cruzes

Aguardamos você!
""")
        else:
            return resposta("⛔ Esse horário não está disponível. Escolha um horário livre.")

    # INFORMAÇÕES GERAIS
    if texto_lower == "2":
        return resposta("""
ℹ️ *Informações Gerais*

As informações técnicas e valores são informados somente presencialmente na oficina,
pois variam de acordo com cada veículo.

Estamos à disposição!
""")

    # FALAR COM ATENDENTE (OPÇÃO 3)
    if texto_lower == "3":
        estado[chat_id] = {"modo": "humano"}
        enviar(ATENDENTE_ID, f"📩 Novo atendimento do cliente {chat_id}:\nMensagem inicial: {texto}")
        return resposta("""👤 *Atendimento Humano*

Sua mensagem foi encaminhada para o atendente.  
Ele responderá em breve pelo Telegram.""")

    # DESMARCAR
    if texto_lower == "4":
        return resposta("""
❌ *Desmarcar Agendamento*

Para cancelar ou alterar um agendamento,
sua mensagem será encaminhada para atendimento humano.
Digite 3 para falar com o atendente.
""")

    return resposta("Digite *menu* para ver as opções.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
