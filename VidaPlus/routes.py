# Importa as bibliotecas necessárias para a aplicação
from VidaPlus import app, db
from flask import render_template, url_for, request, redirect, jsonify
from VidaPlus.models import Contato, Paciente
from VidaPlus.forms import ContatoForm

# === ROTAS ===

# ===== ROTAS CRUD PACIENTE =====

# ROTA PARA CADASTRAR PACIENTE
@app.route('/api/pacientes', methods=['POST'])
def cadastrar_paciente():
    # Pega os dados enviados
    data = request.get_json()

    # Pega os campos do paciente
    nome = data.get('nome')
    data_nascimento = data.get('data_nascimento')
    cpf = data.get('cpf')
    endereco = data.get('endereco')
    telefone = data.get('telefone')

    if not nome or not data_nascimento or not cpf:
        return jsonify({'erro': 'Nome, data de nascimento e CPF são obrigatórios'}), 400

    # CPF repetido
    if Paciente.query.filter_by(cpf=cpf).first():
        return jsonify({'erro': 'Já existe paciente com esse CPF'}), 400

    paciente = Paciente(
        nome=nome,
        data_nascimento=data_nascimento,
        cpf=cpf,
        endereco=endereco,
        telefone=telefone
    )

    db.session.add(paciente)
    db.session.commit()

    return jsonify({'mensagem': 'Paciente cadastrado com sucesso!'}), 201


# ROTA QUE LISTA OS PACIENTES
@app.route('/api/pacientes', methods=['GET'])
def listar_pacientes():
    # Busca todos os pacientes no banco
    pacientes = Paciente.query.all()
    lista = []
    for p in pacientes:
        lista.append({
            'id': p.id,
            'nome': p.nome,
            'data_nascimento': p.data_nascimento,
            'cpf': p.cpf,
            'endereco': p.endereco,
            'telefone': p.telefone
        })
    return jsonify(lista)


# ROTA QUE BUSCA PACIENTE PELO ID
@app.route('/api/pacientes/<int:id>', methods=['GET'])
def pegar_paciente(id):
    # Procura o paciente no banco
    paciente = Paciente.query.get(id)
    if not paciente:
        return jsonify({'erro': 'Paciente não encontrado'}), 404

    dados = {
        'id': paciente.id,
        'nome': paciente.nome,
        'data_nascimento': paciente.data_nascimento,
        'cpf': paciente.cpf,
        'endereco': paciente.endereco,
        'telefone': paciente.telefone
    }
    return jsonify(dados)


# ROTA PARA EDITAR OS DADOS DO PACIENTE PELO ID
@app.route('/api/pacientes/<int:id>', methods=['PUT'])
def atualizar_paciente(id):
    paciente = Paciente.query.get(id)
    if not paciente:
        return jsonify({'erro': 'Paciente não encontrado'}), 404

    data = request.get_json()

    # Atualiza só se vier no JSON, senão deixa igual
    paciente.nome = data.get('nome', paciente.nome)
    paciente.data_nascimento = data.get('data_nascimento', paciente.data_nascimento)
    paciente.cpf = data.get('cpf', paciente.cpf)
    paciente.endereco = data.get('endereco', paciente.endereco)
    paciente.telefone = data.get('telefone', paciente.telefone)

    db.session.commit()

    return jsonify({'mensagem': 'Paciente atualizado com sucesso!'})


# ROTA PARA EXCLUIR PACIENTE PELO ID
@app.route('/api/pacientes/<int:id>', methods=['DELETE'])
def deletar_paciente(id):
    paciente = Paciente.query.get(id)
    if not paciente:
        return jsonify({'erro': 'Paciente não encontrado'}), 404

    db.session.delete(paciente)
    db.session.commit()

    return jsonify({'mensagem': f'Paciente {id} deletado com sucesso!'})


# ===== ROTAS CRUD PROFISSIONAL =====

# ROTA PARA CADASTRAR O PROFISSIONAL
@app.route('/api/profissionais', methods=['POST'])
def cadastrar_profissional():
    data = request.get_json()
    nome = data.get('nome')
    especialidade = data.get('especialidade')
    crm = data.get('crm')
    telefone = data.get('telefone')
    email = data.get('email')

    # Só cadastra se tiver nome e CRM
    if not nome or not crm:
        return jsonify({'erro': 'Nome e CRM são obrigatórios'}), 400

    # Verifica se já existe CRM igual
    if Profissional.query.filter_by(crm=crm).first():
        return jsonify({'erro': 'Já existe profissional com esse CRM'}), 400

    profissional = Profissional(
        nome=nome,
        especialidade=especialidade,
        crm=crm,
        telefone=telefone,
        email=email
    )

    db.session.add(profissional)
    db.session.commit()

    return jsonify({'mensagem': 'Profissional cadastrado com sucesso!'}), 201



# ===== ROTAS DE CONTATO =====

# ROTA PARA MENSAGEM DE CONTATO EM JSON
@app.route('/api/contato', methods=['POST'])
def api_contato():

    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    assunto = data.get('assunto')
    mensagem = data.get('mensagem')

    if not nome or not email or not assunto or not mensagem:
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

    # Cria e salva o contato
    contato = Contato(
        nome=nome,
        email=email,
        assunto=assunto,
        mensagem=mensagem
    )
    db.session.add(contato)
    db.session.commit()

    return jsonify({'mensagem': 'Contato cadastrado com sucesso!'}), 201


# ROTA QUE LISTA OS CONTATOS EM JSON
@app.route('/api/contatos', methods=['GET'])
def lista_contatos():
    contatos = Contato.query.all()
    lista_de_contatos = []
    for contato in contatos:
        lista_de_contatos.append({
            'id': contato.id,
            'nome': contato.nome,
            'email': contato.email,
            'assunto': contato.assunto,
            'mensagem': contato.mensagem
        })

    return jsonify(lista_de_contatos)


# ROTA PARA DELETAR UM CONTATO PELO ID
@app.route('/api/contatos/<int:id>', methods=['DELETE'])
def deletar_contato(id):
    # Busca o contato pelo ID
    contato = Contato.query.get(id)
    if not contato:
        
        return jsonify({'erro': 'Contato não encontrado'}), 404

    # Monta um dicionário com os dados do contato (antes de deletar)
    dados_contato = {
        'id': contato.id,
        'nome': contato.nome,
        'email': contato.email,
        'assunto': contato.assunto,
        'mensagem': contato.mensagem
    }

    # Deleta o contato do banco
    db.session.delete(contato)
    db.session.commit()

    return jsonify({
        'contato_deletado': dados_contato,
        'mensagem': f'Contato {id} deletado com sucesso!'
    })

# ROTA PARA A EDIÇÃO DOS CONTATOS DA LISTA
@app.route('/api/contatos/<int:id>', methods=['PUT'])
def atualizar_contato(id):
    # Busca o contato pelo ID
    contato = Contato.query.get(id)
    if not contato:
        
        return jsonify({'erro': 'Contato não encontrado'}), 404

    data = request.get_json()

    # Atualiza os campos do contato (se vierem no JSON)
    contato.nome = data.get('nome', contato.nome)
    contato.email = data.get('email', contato.email)
    contato.assunto = data.get('assunto', contato.assunto)
    contato.mensagem = data.get('mensagem', contato.mensagem)

    # Salva as mudanças no banco
    db.session.commit()

    return jsonify({
        'mensagem': f'Contato {id} atualizado com sucesso!',
        'contato_atualizado': {
            'id': contato.id,
            'nome': contato.nome,
            'email': contato.email,
            'assunto': contato.assunto,
            'mensagem': contato.mensagem
        }
    })