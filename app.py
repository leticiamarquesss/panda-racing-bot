from flask import Flask, request, jsonify
from database import criar_tabela, salvar_horario, horarios_ocupados

app = Flask(__name__)
criar_tabela()

HORARIOS_FIXOS = [
    "09:00", "11:00", "13:00", "15:00", "17:00"
]

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
    texto = dados.get("message", "").strip().lower()

    # MENU INICIAL
    if texto in ["menu", "oi", "olá", "ola", "inicio", "start"]:
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
    if texto == "1":
        return resposta("""
🔧 *Serviços Disponíveis*

1️⃣ Remap  
2️⃣ Manutenções  
3️⃣ Projetos  

Escolha uma opção:
""")

    # QUALQUER SERVIÇO → AGENDAMENTO
    if texto in ["1", "2", "3"] and dados.get("context") == "servicos":
        pass

    if texto in ["remap", "manutencoes", "manutenções", "projetos", "1", "2", "3"]:
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
    if texto == "2":
        return resposta("""
ℹ️ *Informações Gerais*

As informações técnicas e valores são informados somente presencialmente na oficina,
pois variam de acordo com cada veículo.

Estamos à disposição!
""")

    # FALAR COM ATENDENTE
    if texto == "3":
        return resposta("""
👤 *Atendimento Humano*

Horários de atendimento:
• Segunda a sexta: 9h às 18h  
• Sábado: 9h às 13h  

Sua mensagem será encaminhada para atendimento.
""")

    # DESMARCAR
    if texto == "4":
        return resposta("""
❌ *Desmarcar Agendamento*

Para cancelar ou alterar um agendamento,
sua mensagem será encaminhada para atendimento humano.
""")

    return resposta("Digite *menu* para ver as opções.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
