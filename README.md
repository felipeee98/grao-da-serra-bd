# Empório & Café Grão da Serra

**Aluno:** Felipe Lopes de Goes Couto

**Curso:** Engenharia de Computação

**Disciplina:** Banco de Dados

## Sobre o projeto

O projeto consiste em um sistema de atendimento e gerenciamento de uma cafeteria, utilizando um banco de dados MySQL conectado a uma interface gráfica em Python.

## Tecnologias utilizadas

- Python
- MySQL
- CustomTkinter
- MySQL Connector
- Matplotlib

## Funcionalidades

- Consulta ao cardápio de produtos.
- Abertura e finalização de pedidos.
- Adição e remoção de itens.
- Desconto por fidelidade.
- Controle automático de estoque.
- Relatório de vendas por categoria.
- Reajuste e histórico de preços.

## Conexão com o banco de dados

A conexão entre a interface e o banco de dados foi realizada utilizando Python e a biblioteca mysql-connector-python. Os dados de acesso ficam no arquivo conexao.py, utilizando um usuário local específico para o sistema. A interface utiliza comandos SELECT para consultar as views e chamadas de procedures para realizar operações como abrir pedidos, adicionar produtos e finalizar compras. Os triggers são executados automaticamente pelo MySQL.

## Como executar

1. Instalar o Python e o MySQL Server.
2. Executar o arquivo database.sql no MySQL Workbench.
3. Executar o arquivo atividades.sql.
4. Executar o arquivo configuracao.sql com um usuário administrador.
5. Instalar as dependências com:

`python -m pip install -r requirements.txt`

6. Executar o arquivo ABRIR_SISTEMA.bat ou utilizar o comando:

`python interface.py`

A conta de acesso fornecida destina-se exclusivamente à demonstração local do projeto.