# Importa as bibliotecas necessárias para a aplicação
from VidaPlus import app
from VidaPlus.models import Contato
from VidaPlus.models import Paciente


# Roda a aplicação no navegador
if __name__ == '__main__':
    app.run(debug=True)