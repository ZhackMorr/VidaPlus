# Importa o banco de dados criado no arquivo init
from VidaPlus import db

#Importa bibliotecas necessárias
from datetime import datetime

# Modelo para armazenar contatos enviados pelo formulário
class Contato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    nome = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    assunto = db.Column(db.String(100), nullable=True)
    mensagem = db.Column(db.String(500), nullable=True)
    respondido = db.Column(db.Integer, default=0)

# Modelo de Profissional de Saúde (tipo médico)
class Profissional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100))
    crm = db.Column(db.String(20), unique=True)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    def __repr__(self):
        return f'<Profissional {self.nome}>'

# Modelo para armazenar pacientes no banco de dados
class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Paciente {self.nome}>'