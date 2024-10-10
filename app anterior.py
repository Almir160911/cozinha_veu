import os
import datetime
import sqlite3
from flask import Flask, request, send_from_directory, url_for
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('pedidos_comida.db', check_same_thread=False)
cursor = conn.cursor()

# Configurar o Twilio
account_sid = 'AC977d432ca95d4525dfbfd776a4fea29c'
#auth_token = 'df7338779ca7c1e58ddfa5f774778786'
auth_token = 'b6943dd9dfb061d635f48e066e14c061'
client = Client(account_sid, auth_token)

# Criação da instância Flask
app = Flask(__name__)

# Definir caminho para as imagens
IMAGEM_PATH = os.path.join(os.getcwd(), 'imagens')

# Função para autenticar o usuário
def autenticar_usuario(nome, senha):
    cursor.execute("SELECT id, tipo FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
    return cursor.fetchone()

# Função para listar pratos
def listar_pratos():
    cursor.execute("SELECT id, nome, preco, descricao, imagem FROM pratos")
    return cursor.fetchall()

# Função para inserir um novo pedido
def inserir_pedido(usuario_id, prato_id, horario_entrega, observacao_entrega):
    status = "Pedido confirmado"
    cursor.execute("INSERT INTO pedidos (usuario_id, prato_id, horario_entrega, status, observacao) VALUES (?, ?, ?, ?, ?)",
                   (usuario_id, prato_id, horario_entrega, status, observacao_entrega))
    conn.commit()

# Rota para servir as imagens dos pratos
@app.route('/imagens/<filename>')
def enviar_imagem(filename):
    return send_from_directory(IMAGEM_PATH, filename)

# Função para enviar imagem usando Twilio
def enviar_imagem_twilio(to, image_filename, body):
    # Gerar URL para a imagem que está na pasta 'imagens'
    try:
        print("enviar_imagem_twilio Para " + to + " imagem_filename " + image_filename + " corpo mensagem " + body)
        image_url = url_for('enviar_imagem', filename=image_filename, _external=True)
        print("passou aqui image_url ")
        
        client.messages.create(
            
            body=body,
            from_='whatsapp:+14155238886',  # Número do WhatsApp Twilio
            
            media_url=[image_url],  # URL da imagem servida pelo Flask
            to=to
        )
    except ValueError:
            print(str(image_url))

# Função para processar mensagens recebidas pelo WhatsApp
@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').lower()
    print("inicio mensagem : " + str(request.values))
    sender = request.values.get('From')
    response = MessagingResponse()
    msg = response.message()
    
    if "login" in incoming_msg:
        # Exemplo: login:<nome_usuario>:<senha>
        try:
            _, nome, senha = incoming_msg.split(':')
            usuario = autenticar_usuario(nome, senha)
            if usuario:
                user_id, user_tipo = usuario
                if user_tipo == 'cliente':
                    msg.body("Login realizado com sucesso! Digite 'listar pratos' para ver o menu.")
                    return str(response)
                elif user_tipo == 'admin':
                    msg.body("Bem-vindo, Admin!")
                    return str(response)
            else:
                msg.body("Nome de usuário ou senha incorretos.")
        except ValueError:
            msg.body("Formato de login incorreto. Use: login:<nome_usuario>:<senha>")
    
    elif "listar pratos" in incoming_msg:
        pratos = listar_pratos()
        if pratos:
            pratos_msg = "Aqui estão os pratos disponíveis:\n"
            for prato in pratos:
                prato_id, nome_prato, preco, descricao, imagem = prato
                pratos_msg += f"{prato_id}: {nome_prato} - R$ {preco:.2f}\nDescrição: {descricao}\n\n"
                
                # Enviar imagem do prato se disponível
                if imagem:
                    enviar_imagem_twilio(sender, imagem, f"{nome_prato} - R$ {preco:.2f}")
            
            pratos_msg += "Digite 'pedido:<prato_id>:<horário de entrega (HH:MM)>:<observação>' para fazer um pedido."
            msg.body(pratos_msg)
        else:
            msg.body("Nenhum prato disponível no momento.")

    elif "pedido" in incoming_msg:
        try:
            _, prato_id, horario_entrega, observacao_entrega = incoming_msg.split(':')
            prato_id = int(prato_id)
            datetime.datetime.strptime(horario_entrega, "%H:%M")  # Verificar formato do horário
            inserir_pedido(1, prato_id, horario_entrega, observacao_entrega)  # Substituir 1 pelo ID do usuário logado
            msg.body("Pedido realizado com sucesso!")
        except ValueError:
            msg.body("Formato do pedido incorreto. Use: pedido:<prato_id>:<horário de entrega (HH:MM)>:<observação>")
    
    else:
        msg.body("Bem-vindo! Digite 'login:<nome>:<senha>' para começar.")

    return str(response)

if __name__ == "__main__":
    app.run()
