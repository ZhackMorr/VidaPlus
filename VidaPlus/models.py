# Importa o banco de dados criado no arquivo init
from VidaPlus import db

#Importa bibliotecas necessárias
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ===== MODELOS PARA O CRUD =====

# Modelo para armazenar contatos enviados para a empresa VidaPlus
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
    consultas = db.relationship('Consulta', backref='profissional', cascade="all, delete-orphan")

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
    consultas = db.relationship('Consulta', backref='paciente', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Paciente {self.nome}>'

# Modelo para adicionar o relacionamento entre  Paciente-Consulta e Profissiona-Consulta
class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id'), nullable=False)
    status = db.Column(db.String(20), default='agendada')  # agendada, concluída, cancelada
    observacoes = db.Column(db.Text)


# ===== MODELO PARA LOGIN E SENHA =====

# Modelo para usuários do sistema (login)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)  # guarda senha com hash
    tipo = db.Column(db.String(20), nullable=False)  # admin, profissional ou paciente

    # Guarda o ID do paciente ou profissional (se for um deles)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id', ondelete='CASCADE'), nullable=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id', ondelete='CASCADE'), nullable=True)

    # Funções pra lidar com a senha
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)