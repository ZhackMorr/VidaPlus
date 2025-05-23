# VidaPlus - Sistema de Gestão de Saúde

Esse projeto é uma API feita em Flask para gerenciar pacientes, profissionais de saúde e consultas. Foi desenvolvido como trabalho final da faculdade, focando em praticar CRUD, autenticação e organização de código.

## O que dá pra fazer

- Cadastrar, listar, editar e deletar pacientes, profissionais e consultas
- Login e controle de acesso por tipo de usuário (admin, profissional, paciente)
- Agendamento e gerenciamento de consultas
- Rotas protegidas para ações sensíveis

## Como rodar

1. Clone o repositório
2. Instale as dependências (`pip install -r requirements.txt`)
3. Rode o arquivo `main.py`
4. Use o Postman ou Insomnia para testar os endpoints

## Tecnologias usadas

- Python 3
- Flask
- SQLAlchemy

## Observações

O sistema usa autenticação por sessão (não JWT). Para evoluções futuras, seria legal adicionar interface gráfica, relatórios e autenticação por token.
