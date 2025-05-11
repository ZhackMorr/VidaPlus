# Importa as bibliotecas necessárias para a aplicação
from flask import Flask

# Inicia a aplicação
app = Flask(__name__)

# Importa as rotas do arquivo de rotas para a aplicação
from VidaPlus.routes import homepage