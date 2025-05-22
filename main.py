# Importa as bibliotecas necessárias para a aplicação
from VidaPlus import app
from VidaPlus.models import Contato
from VidaPlus.models import Paciente
from VidaPlus.models import Profissional
from VidaPlus.models import Usuario


# Roda a aplicação no navegador
if __name__ == '__main__':
    app.run(debug=True)