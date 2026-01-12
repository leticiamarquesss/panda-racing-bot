from flask import Flask, request
import requests
from database import criar_tabela, salvar_horario, horarios_ocupados

app = Flask(__name__)
criar_tabela()
VERIFY_TOKEN = "panda_verify"

BOT_TOKEN = "7582315674AAHE8PjojORKJJawbZKcSLpfsjs-eIN5px4"
TELEGRAM_API = f"https://api.telegram.org/bot7582315674AAHE8PjojORKJJawbZKcSLpfsjs-eIN5px4"
ATENDENTE_ID = 123456789  # seu chat_id do Telegram

HORARIOS_FIXOS = ["09:00", "11:00", "13:00", "15:00", "17:00"]
estado = {}  # ex: {chat_id: {"modo": "bot"}}

# --- Funções auxiliares ---
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
    # Apenas devolve o texto puro, WhatsApp espera body
    return texto.strip()

WHATSAPP_PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"  # colocar depois
WHATSAPP_TOKEN = "YOUR_META_TOKEN"  # colocar depois

def enviar_whatsapp(numero, mensagem):
    # Se o token/número não estiver definido, apenas printa
    if WHATSAPP_PHONE_NUMBER_ID == "YOUR_PHONE_NUMBER_ID" or WHATSAPP_TOKEN == "YOUR_META_TOKEN":
        print(f"[Simulado] Enviando para {numero}: {mensagem}")
        return

    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }
    requests.post(url, json=data, headers=headers)


# --- Webhook WhatsApp ---
@app.route("/webhook/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        # Verificação do Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Token inválido", 403

    # POST → Mensagens recebidas
    dados = request.json
    try:
        msg = dados["entry"][0]["changes"][0]["value"]["messages"][0]
        numero = msg["from"]
        texto = msg["text"]["body"]
        # Reaproveita sua lógica
        resposta_texto = resposta(texto)
        enviar_whatsapp(numero, resposta_texto)
    except:
        pass
    return "OK", 200

# --- Rota home ---
@app.route("/", methods=["GET"])
def home():
    return "Bot PANDA RACING DEVELOPMENT ativo 🐼"

# --- Webhook Telegram / atendimento humano ---
@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.json
    chat_id = dados.get("chat_id")
    texto = dados.get("message", "").strip()
    texto_lower = texto.lower()

    # Atendente responde
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
        return "OK", 200

    # Cliente modo humano
    modo = estado.get(chat_id, {}).get("modo", "bot")
    if modo == "humano":
        enviar(ATENDENTE_ID, f"📩 Cliente {chat_id}:\n{texto}")
        return "OK", 200

    # Fluxo original do bot
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
    # (aqui você mantém o restante do seu fluxo original...)

    return resposta("Digite *menu* para ver as opções.")

# --- Inicialização Flask no Render ---
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
