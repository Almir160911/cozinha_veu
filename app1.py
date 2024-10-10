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

# Função para criar um novo prato (admin)
def criar_prato(nome, preco, descricao, imagem):
    cursor.execute("INSERT INTO pratos (nome, preco, descricao, imagem) VALUES (?, ?, ?, ?)", (nome, preco, descricao, imagem))
    conn.commit()

# Função para editar um prato existente (admin)
def editar_prato(prato_id, nome, preco, descricao, imagem):
    cursor.execute("UPDATE pratos SET nome = ?, preco = ?, descricao = ?, imagem = ? WHERE id = ?", (nome, preco, descricao, imagem, prato_id))
    conn.commit()

# Função para excluir um prato (admin)
def excluir_prato(prato_id):
    cursor.execute("DELETE FROM pratos WHERE id = ?", (prato_id,))
    conn.commit()

# Função para criar um novo usuário (admin)
def criar_usuario(nome, senha, tipo):
    cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)", (nome, senha, tipo))
    conn.commit()

# Função para editar um usuário existente (admin)
def editar_usuario(usuario_id, nome, senha, tipo):
    cursor.execute("UPDATE usuarios SET nome = ?, senha = ?, tipo = ? WHERE id = ?", (nome, senha, tipo, usuario_id))
    conn.commit()

# Função para excluir um usuário (admin)
def excluir_usuario(usuario_id):
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()

# Rota para servir as imagens dos pratos
@app.route('/imagens/<filename>')
def enviar_imagem(filename):
    return send_from_directory(IMAGEM_PATH, filename)

# Função para enviar imagem usando Twilio
def enviar_imagem_twilio(to, image_filename, body):
    try:
        image_url = url_for('enviar_imagem', filename=image_filename, _external=True)
        client.messages.create(
            body=body,
            from_='whatsapp:+14155238886',
            media_url=[image_url],
            to=to
        )
    except ValueError:
        print(str(image_url))

# Variáveis para armazenar estados dos usuários
user_states = {}

# Função para processar mensagens recebidas pelo WhatsApp
@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').lower()
    sender = request.values.get('From')
    response = MessagingResponse()
    msg = response.message()
    
    # Recuperar o estado do usuário
    user_state = user_states.get(sender, None)

    if user_state is None:
        # Se não há estado, iniciar com a tela de login
        if "login" in incoming_msg:
            try:
                _, nome, senha = incoming_msg.split(':')
                usuario = autenticar_usuario(nome, senha)
                if usuario:
                    user_id, user_tipo = usuario
                    user_states[sender] = {"user_id": user_id, "user_tipo": user_tipo, "state": "menu"}
                    msg.body(f"Login realizado com sucesso! Tipo de usuário: {user_tipo}. Digite 'menu' para começar.")
                else:
                    msg.body("Nome de usuário ou senha incorretos.")
            except ValueError:
                msg.body("Formato de login incorreto. Use: login:<nome_usuario>:<senha>")
        else:
            msg.body("Bem-vindo! Digite 'login:<nome>:<senha>' para começar.")
    
    elif user_state["state"] == "menu":
        if user_state["user_tipo"] == "cliente":
            msg.body("Opções:\n1. Listar pratos\n2. Fazer pedido\nDigite o número da opção desejada.")
            user_states[sender]["state"] = "cliente_opcao"
        elif user_state["user_tipo"] == "admin":
            msg.body("Opções de Admin:\n1. Gerenciar pratos\n2. Gerenciar usuários\nDigite o número da opção desejada.")
            user_states[sender]["state"] = "admin_opcao"
    
    elif user_state["state"] == "cliente_opcao":
        if incoming_msg == "1":
            pratos = listar_pratos()
            pratos_msg = "Aqui estão os pratos disponíveis:\n"
            for prato in pratos:
                prato_id, nome_prato, preco, descricao, imagem = prato
                pratos_msg += f"{prato_id}: {nome_prato} - R$ {preco:.2f}\nDescrição: {descricao}\n\n"
                if imagem:
                    enviar_imagem_twilio(sender, imagem, f"{nome_prato} - R$ {preco:.2f}")
            pratos_msg += "Digite 'pedido:<prato_id>:<horário de entrega (HH:MM)>:<observação>' para fazer um pedido."
            msg.body(pratos_msg)
            user_states[sender]["state"] = "cliente_menu"
    
    elif user_state["state"] == "admin_opcao":
        if incoming_msg == "1":
            msg.body("Opções de Prato:\n1. Criar prato\n2. Editar prato\n3. Excluir prato\nDigite o número da opção.")
            user_states[sender]["state"] = "admin_prato"
        elif incoming_msg == "2":
            msg.body("Opções de Usuário:\n1. Criar usuário\n2. Editar usuário\n3. Excluir usuário\nDigite o número da opção.")
            user_states[sender]["state"] = "admin_usuario"

    elif user_state["state"] == "admin_prato":
        if incoming_msg == "1":
            msg.body("Digite o nome do prato que deseja criar.")
            user_states[sender]["state"] = "admin_criar_prato_nome"
        elif incoming_msg == "2":
            msg.body("Digite o ID do prato que deseja editar.")
            user_states[sender]["state"] = "admin_editar_prato"
        elif incoming_msg == "3":
            msg.body("Digite o ID do prato que deseja excluir.")
            user_states[sender]["state"] = "admin_excluir_prato"
    
    elif user_state["state"] == "admin_criar_prato_nome":
        user_states[sender]["novo_prato_nome"] = incoming_msg
        msg.body("Digite o preço do prato.")
        user_states[sender]["state"] = "admin_criar_prato_preco"
    
    elif user_state["state"] == "admin_criar_prato_preco":
        try:
            preco = float(incoming_msg)
            user_states[sender]["novo_prato_preco"] = preco
            msg.body("Digite a descrição do prato.")
            user_states[sender]["state"] = "admin_criar_prato_descricao"
        except ValueError:
            msg.body("Por favor, insira um preço válido.")
    
    elif user_state["state"] == "admin_criar_prato_descricao":
        user_states[sender]["novo_prato_descricao"] = incoming_msg
        msg.body("Digite o nome do arquivo da imagem do prato (se houver).")
        user_states[sender]["state"] = "admin_criar_prato_imagem"
    
    elif user_state["state"] == "admin_criar_prato_imagem":
        nome = user_states[sender]["novo_prato_nome"]
        preco = user_states[sender]["novo_prato_preco"]
        descricao = user_states[sender]["novo_prato_descricao"]
        imagem = incoming_msg
        criar_prato(nome, preco, descricao, imagem)
        msg.body(f"Prato {nome} criado com sucesso!")
        user_states[sender]["state"] = "menu"
    
    return str(response)

if __name__ == "__main__":
    app.run()
