Aplicação de Pedido de Comida com Chatbot e Interface Gráfica

Esta aplicação é um sistema de pedidos de comida que simula interações com chatbot e possui uma interface gráfica construída usando Tkinter. Ela suporta o cliente para fazer pedidos e o administrador para gerenciar o cardápio e os pedidos, com persistência de dados em um banco de dados SQLite.
Funcionalidades

    Autenticação de Usuário: Suporte para clientes e administradores.
    Interface Gráfica: Clientes podem navegar pelos pratos disponíveis, realizar pedidos e especificar horários de entrega. Administradores podem adicionar novos pratos ao cardápio.
    Gestão de Pedidos: Pedidos são salvos no banco de dados SQLite com confirmação e controle de status.
    Persistência de Dados: Armazena usuários, pratos e pedidos no banco de dados SQLite (pedidos_comida.db).

Tecnologias Utilizadas

    Python 3
    Tkinter: Para criação da interface gráfica.
    SQLite: Para persistência de dados (usuários, pratos e pedidos).

Pré-requisitos

    Python 3: Verifique se o Python 3 está instalado na sua máquina.
        Baixar Python

    Tkinter: Esta biblioteca geralmente vem incluída no Python. Caso não esteja instalada, siga as instruções abaixo:

        Para Ubuntu/Debian:

        bash

        sudo apt-get install python3-tk

        Para macOS: O Tkinter já vem incluído nas instalações do Python.

        Para Windows: Tkinter é instalado por padrão com o Python.

Instalação

    Clone o repositório:

    bash

git clone https://github.com/usuario/nome-do-repositorio.git
cd nome-do-repositorio

Instale as dependências (se necessário):

Não são necessárias dependências externas além de Tkinter e SQLite.

Configure o banco de dados SQLite:

O banco de dados será criado automaticamente na primeira execução da aplicação. Alternativamente, você pode usar o script abaixo para criar usuários iniciais (administrador e cliente).

Opcional: Crie usuários iniciais (administrador e cliente) usando o script abaixo:

python

import sqlite3

conn = sqlite3.connect('pedidos_comida.db')
cursor = conn.cursor()

def inserir_usuario(nome, senha, tipo):
    cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)", (nome, senha, tipo))
    conn.commit()

inserir_usuario("admin", "admin123", "admin")
inserir_usuario("cliente1", "cliente123", "cliente")

conn.close()

Execute este script uma vez para adicionar os seguintes usuários:

    Usuário administrador: admin / admin123
    Usuário cliente: cliente1 / cliente123

Execute a aplicação principal:

bash

    python main.py

Uso
1. Tela de Login

    A aplicação iniciará com uma tela de login.
        Credenciais de administrador: admin / admin123
        Credenciais de cliente: cliente1 / cliente123

2. Interface do Cliente

    Após fazer login como cliente, será exibido um menu com os pratos disponíveis.
    Selecione um prato no menu suspenso, insira o horário de entrega e clique em "Realizar Pedido" para confirmar o pedido.
    O pedido será salvo no sistema e confirmado.

3. Interface do Administrador

    Após fazer login como administrador, você poderá adicionar novos pratos ao cardápio inserindo o nome do prato e o preço.
    Você também poderá gerenciar outras funções administrativas, como visualizar e modificar pedidos (melhoria futura).

Estrutura do Projeto

bash

/nome-do-repositorio
   ├── pedidos_comida.db         # Banco de dados SQLite (gerado automaticamente na primeira execução)
   ├── main.py                   # Arquivo principal da aplicação com Tkinter
   ├── criar_usuarios.py         # Script opcional para criar usuários iniciais (admin e cliente)
   └── README.md                 # Documentação

Melhorias Futuras

    Rastreamento de Pedidos: Adicionar funcionalidade para que os clientes possam acompanhar o status de seus pedidos.
    Histórico de Pedidos: Permitir que os clientes visualizem o histórico de pedidos realizados.
    Painel de Administração Avançado: Permitir que o administrador atualize e exclua pratos do cardápio, além de gerenciar pedidos de forma mais eficiente.
    Processamento de Linguagem Natural (NLP): Implementar um chatbot que utilize processamento de linguagem natural para interações com os clientes.

Licença

Este projeto está licenciado sob os termos da licença MIT.

Esse arquivo README.md em português oferece uma visão geral clara do projeto, incluindo como instalar, executar e utilizar a aplicação, além de descrever suas funcionalidades e futuras melhorias. Ele pode ser adaptado conforme as necessidades específicas do seu projeto.
ChatGPT pode cometer erros. Considere verificar informações importantes.


flatpak run org.sqlitebrowser.sqlitebrowser
# Cozinha_Pedido_Whatzap
# cozinha
# cozinha
# cozinha
# cozinha
