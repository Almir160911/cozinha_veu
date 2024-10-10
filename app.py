import os
import datetime
import sqlite3
from flask import Flask, request, send_from_directory, url_for, jsonify
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
    cursor.execute("INSERT INTO pratos (nome, preco, descricao, imagem) VALUES (?, ?, ?, ?)",
                   (nome, preco, descricao, imagem))
    conn.commit()

# Função para editar um prato existente (admin)
def editar_prato(prato_id, nome, preco, descricao, imagem):
    cursor.execute("UPDATE pratos SET nome = ?, preco = ?, descricao = ?, imagem = ? WHERE id = ?",
                   (nome, preco, descricao, imagem, prato_id))
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

# Rota para processar mensagens recebidas pelo WhatsApp
@app.route("/whatsapp", methods=['POST'])
def whatsapp():
    incoming_msg = request.values.get('Body', '').lower()
    sender = request.values.get('From')
    response = MessagingResponse()
    msg = response.message()
    
    if "login" in incoming_msg:
        try:
            _, nome, senha = incoming_msg.split(':')
            usuario = autenticar_usuario(nome, senha)
            if usuario:
                user_id, user_tipo = usuario
                if user_tipo == 'cliente':
                    msg.body("Login realizado com sucesso! Digite 'listar pratos' para ver o menu.")
                elif user_tipo == 'admin':
                    msg.body("Bem-vindo, Admin! Digite 'admin help' para ver as opções.")
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
            datetime.datetime.strptime(horario_entrega, "%H:%M")
            inserir_pedido(1, prato_id, horario_entrega, observacao_entrega)
            msg.body("Pedido realizado com sucesso!")
        except ValueError:
            msg.body("Formato do pedido incorreto. Use: pedido:<prato_id>:<horário de entrega (HH:MM)>:<observação>")
    
    elif "admin help" in incoming_msg:
        msg.body("Comandos de admin:\n- 'admin criar prato:<nome>:<preço>:<descrição>:<imagem>'\n- 'admin editar prato:<prato_id>:<nome>:<preço>:<descrição>:<imagem>'\n- 'admin excluir prato:<prato_id>'\n- 'admin criar usuario:<nome>:<senha>:<tipo>'\n- 'admin editar usuario:<id>:<nome>:<senha>:<tipo>'\n- 'admin excluir usuario:<id>'")
    
    elif incoming_msg.startswith("admin criar prato"):
        try:
            _, nome, preco, descricao, imagem = incoming_msg.split(':')
            preco = float(preco)
            criar_prato(nome, preco, descricao, imagem)
            msg.body("Prato criado com sucesso!")
        except ValueError:
            msg.body("Erro ao criar o prato. Verifique os dados e tente novamente.")

    elif incoming_msg.startswith("admin editar prato"):
        try:
            _, prato_id, nome, preco, descricao, imagem = incoming_msg.split(':')
            prato_id = int(prato_id)
            preco = float(preco)
            editar_prato(prato_id, nome, preco, descricao, imagem)
            msg.body("Prato editado com sucesso!")
        except ValueError:
            msg.body("Erro ao editar o prato. Verifique os dados e tente novamente.")

    elif incoming_msg.startswith("admin excluir prato"):
        try:
            _, prato_id = incoming_msg.split(':')
            prato_id = int(prato_id)
            excluir_prato(prato_id)
            msg.body("Prato excluído com sucesso!")
        except ValueError:
            msg.body("Erro ao excluir o prato. Verifique os dados e tente novamente.")

    elif incoming_msg.startswith("admin criar usuario"):
        try:
            _, nome, senha, tipo = incoming_msg.split(':')
            criar_usuario(nome, senha, tipo)
            msg.body("Usuário criado com sucesso!")
        except ValueError:
            msg.body("Erro ao criar o usuário. Verifique os dados e tente novamente.")

    elif incoming_msg.startswith("admin editar usuario"):
        try:
            _, usuario_id, nome, senha, tipo = incoming_msg.split(':')
            usuario_id = int(usuario_id)
            editar_usuario(usuario_id, nome, senha, tipo)
            msg.body("Usuário editado com sucesso!")
        except ValueError:
            msg.body("Erro ao editar o usuário. Verifique os dados e tente novamente.")

    elif incoming_msg.startswith("admin excluir usuario"):
        try:
            _, usuario_id = incoming_msg.split(':')
            usuario_id = int(usuario_id)
            excluir_usuario(usuario_id)
            msg.body("Usuário excluído com sucesso!")
        except ValueError:
            msg.body("Erro ao excluir o usuário. Verifique os dados e tente novamente.")

    else:
        msg.body("Bem-vindo! Digite 'login:<nome>:<senha>' para começar.")
    
    return str(response)

if __name__ == "__main__":
    app.run()
