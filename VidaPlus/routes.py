# Importa as bibliotecas necessárias para a aplicação
from VidaPlus import app
from flask import render_template


# === ROTAS ===

# PÁGINA INICIAL
@app.route('/')
def homepage():
    return render_template('index.html')