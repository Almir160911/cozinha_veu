# refatorar este código python para integrar como um chatbot no whatzap
import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk  # Biblioteca Pillow para lidar com imagens
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter.messagebox import askyesnocancel

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('pedidos_comida.db')
cursor = conn.cursor()

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

# Função para exibir a janela do cliente com imagens
def janela_cliente(user_id):
    janela_cliente = tk.Toplevel()
    janela_cliente.title("Área do Cliente")

    label_bem_vindo = tk.Label(janela_cliente, text="Bem-vindo! Selecione um prato para fazer o pedido.")
    label_bem_vindo.pack()

    pratos = listar_pratos()

    if not pratos:
        messagebox.showinfo("Sem Pratos", "Nenhum prato disponível no momento.")
        return
    
    # Variável para armazenar o prato selecionado
    prato_selecionado = tk.StringVar()
    prato_selecionado.set(None)  # Valor inicial (nenhum selecionado)

    # Frame para exibir os pratos
    frame_pratos = tk.Frame(janela_cliente)
    frame_pratos.pack()

    # Exibir lista de pratos com descrição e imagem
    for i, (prato_id, nome_prato, preco, descricao, imagem_caminho) in enumerate(pratos):
        prato_frame = tk.Frame(frame_pratos)
        prato_frame.pack(anchor=tk.W, pady=10)

        # Carregar e redimensionar a imagem do prato
        if imagem_caminho:
            try:
                imagem = Image.open(imagem_caminho)
                imagem = imagem.resize((100, 100), Image.ANTIALIAS)  # Redimensiona a imagem
                imagem_tk = ImageTk.PhotoImage(imagem)
                label_imagem = tk.Label(prato_frame, image=imagem_tk)
                label_imagem.image = imagem_tk  # Precisa manter uma referência para evitar que seja descartada pelo GC
                label_imagem.grid(row=0, column=0, rowspan=3, padx=10)
            except Exception as e:
                print(f"Erro ao carregar a imagem: {e}")
        
        prato_texto = f"{nome_prato} - R$ {preco:.2f}\nDescrição: {descricao}"
        label_prato = tk.Radiobutton(prato_frame, text=prato_texto, variable=prato_selecionado, value=prato_id)
        label_prato.grid(row=0, column=1, sticky="w")

    # Campo para horário de entrega
    label_horario = tk.Label(janela_cliente, text="Horário de entrega (HH:MM):")
    label_horario.pack()

    entry_horario = tk.Entry(janela_cliente)
    entry_horario.pack()

    # Campo para observação
    label_observacao = tk.Label(janela_cliente, text="Observação:")
    label_observacao.pack()
    
    entry_observacao = tk.Entry(janela_cliente)
    entry_observacao.pack()

    def realizar_pedido():
        prato_escolhido = prato_selecionado.get()
        if prato_escolhido:
            horario_entrega = entry_horario.get()
            observacao_entrega = entry_observacao.get()
            try:
                # Verifica o formato do horário
                datetime.datetime.strptime(horario_entrega, "%H:%M")
                inserir_pedido(user_id, prato_escolhido, horario_entrega, observacao_entrega)
                messagebox.showinfo("Sucesso", "Pedido realizado com sucesso!")
            except ValueError:
                messagebox.showerror("Erro", "Horário inválido. Por favor, insira no formato HH:MM.")
        else:
            messagebox.showerror("Erro", "Selecione um prato para fazer o pedido.")

    btn_pedido = tk.Button(janela_cliente, text="Realizar Pedido", command=realizar_pedido)
    btn_pedido.pack()

    janela_cliente.mainloop()

# Função para a tela de login
def login():
    nome = entry_nome.get()
    senha = entry_senha.get()
    
    usuario = autenticar_usuario(nome, senha)
    
    if usuario:
        user_id, user_tipo = usuario
        if user_tipo == 'cliente':
            janela_cliente(user_id)
        elif user_tipo == 'admin':
            janela_admin()
    else:
        messagebox.showerror("Erro", "Nome de usuário ou senha incorretos")

# Função para exibir a janela do administrador
def janela_admin():
    janela_admin = tk.Toplevel()
    janela_admin.title("Área do Administrador")

    label_bem_vindo = tk.Label(janela_admin, text="Bem-vindo, Admin!")
    label_bem_vindo.pack()

    label_nome_prato = tk.Label(janela_admin, text="Nome do Prato:")
    label_nome_prato.pack()

    entry_nome_prato = tk.Entry(janela_admin)
    entry_nome_prato.pack()

    label_preco_prato = tk.Label(janela_admin, text="Preço do Prato (R$):")
    label_preco_prato.pack()

    entry_preco_prato = tk.Entry(janela_admin)
    entry_preco_prato.pack()

    label_descricao_prato = tk.Label(janela_admin, text="Descrição do Prato:")
    label_descricao_prato.pack()

    entry_descricao_prato = tk.Entry(janela_admin)
    entry_descricao_prato.pack()

    label_imagem_prato = tk.Label(janela_admin, text="Caminho da Imagem do Prato:")
    label_imagem_prato.pack()

    # Botão para selecionar a imagem do prato
    def selecionar_imagem():
         
        caminho_imagem = filedialog.askopenfilenames(             
            title="Selecione a Imagem do Prato"
            
        )
        entry_imagem_prato.delete(0, tk.END)
        entry_imagem_prato.insert(0, caminho_imagem)

    entry_imagem_prato = tk.Entry(janela_admin)
    entry_imagem_prato.pack()

    btn_selecionar_imagem = tk.Button(janela_admin, text="Selecionar Imagem", command=selecionar_imagem)
    btn_selecionar_imagem.pack()

    def adicionar_prato():
        nome_prato = entry_nome_prato.get()
        preco_prato = entry_preco_prato.get()
        descricao_prato = entry_descricao_prato.get()
        imagem_prato = entry_imagem_prato.get()

        try:
            preco_prato = float(preco_prato)
            cursor.execute("INSERT INTO pratos (nome, preco, descricao, imagem) VALUES (?, ?, ?, ?)", 
                           (nome_prato, preco_prato, descricao_prato, imagem_prato))
            conn.commit()
            messagebox.showinfo("Sucesso", "Prato adicionado com sucesso!")
        except ValueError:
            messagebox.showerror("Erro", "Preço inválido. Insira um número válido.")

    btn_adicionar = tk.Button(janela_admin, text="Adicionar Prato", command=adicionar_prato)
    btn_adicionar.pack()

    janela_admin.mainloop()

# Criação da janela de login
janela_login = tk.Tk()
janela_login.title("Login")

label_nome = tk.Label(janela_login, text="Nome de Usuário:")
label_nome.pack()

entry_nome = tk.Entry(janela_login)
entry_nome.pack()

label_senha = tk.Label(janela_login, text="Senha:")
label_senha.pack()

entry_senha = tk.Entry(janela_login, show="*")
entry_senha.pack()

btn_login = tk.Button(janela_login, text="Login", command=login)
btn_login.pack()

janela_login.mainloop()

# Fechar a conexão com o banco de dados ao final
conn.close()
