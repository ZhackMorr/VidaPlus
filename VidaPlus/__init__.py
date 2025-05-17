# Importa as bibliotecas necessárias para a aplicação
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicia a aplicação
app = Flask(__name__)

# Define o bando de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Medida de seguranã
app.config['SECRET_KEY'] = 'SF943-34RF-34F43'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importa as rotas do arquivo de rotas para a aplicação
from VidaPlus import routes
from VidaPlus.models import Contato
from VidaPlus.models import Paciente