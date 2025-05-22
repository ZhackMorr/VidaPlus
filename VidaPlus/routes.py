# Importa as bibliotecas necessárias para a aplicação
from VidaPlus import app, db
from flask import render_template, url_for, request, redirect, jsonify, session
from VidaPlus.models import Contato, Paciente, Profissional, Usuario, Consulta
from VidaPlus.forms import ContatoForm
from functools import wraps
from datetime import datetime

# === ROTAS ===


# ===== ROTAS DE USUÁRIO =====

# FUNÇÃO PARA CHECAR SE O USUÁRIO ESTÁ LOGADO
def precisa_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'erro': 'Precisa fazer login'}), 401
        return f(*args, **kwargs)
    return decorated_function


# FUCÃO QUE CHECA SE É ADM
def precisa_ser_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tipo_usuario' not in session or session['tipo_usuario'] != 'admin':
            return jsonify({'erro': 'Precisa ser admin'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ROTA PARA CRIAR UM USUÁRIO
@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    tipo = data.get('tipo')  # 'admin', 'profissional' ou 'paciente'

    # Checa se já existe esse email
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400

    usuario = Usuario(email=email, tipo=tipo)
    usuario.set_senha(senha)

    if tipo == 'paciente':
        nome = data.get('nome')
        data_nascimento = data.get('data_nascimento')
        cpf = data.get('cpf')
        endereco = data.get('endereco')
        telefone = data.get('telefone')

        # Checa se já existe paciente com esse CPF
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
        usuario.paciente_id = paciente.id

    elif tipo == 'profissional':
        nome = data.get('nome')
        especialidade = data.get('especialidade')
        crm = data.get('crm')
        telefone = data.get('telefone')
        email_prof = data.get('email_prof')  # pode ser igual ao email do usuário

        # Checa se já existe profissional com esse CRM
        if Profissional.query.filter_by(crm=crm).first():
            return jsonify({'erro': 'Já existe profissional com esse CRM'}), 400

        profissional = Profissional(
            nome=nome,
            especialidade=especialidade,
            crm=crm,
            telefone=telefone,
            email=email_prof
        )
        db.session.add(profissional)
        db.session.commit()
        usuario.profissional_id = profissional.id

    # Admin não precisa criar nada extra

    db.session.add(usuario)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado!'}), 201


# ROTA DE LOGIN
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    senha = data.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()

    # Checa se existe e se a senha tá certa
    if usuario and usuario.check_senha(senha):
        # Guarda na sessão
        session['usuario_id'] = usuario.id
        session['tipo_usuario'] = usuario.tipo
        return jsonify({'mensagem': 'Login ok!', 'tipo': usuario.tipo})

    return jsonify({'erro': 'Email ou senha errados'}), 401


# ROTA DE LOGOUT
@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({'mensagem': 'Logout ok!'})

# Exemplo de rota protegida: (só admin pode ver todos os usuários)
@app.route('/api/usuarios', methods=['GET'])
@precisa_login
@precisa_ser_admin
def listar_usuarios():
    usuarios = Usuario.query.all()
    lista = []
    for u in usuarios:
        lista.append({
            'id': u.id,
            'email': u.email,
            'tipo': u.tipo,
            'paciente_id': u.paciente_id,
            'profissional_id': u.profissional_id
        })
    return jsonify(lista)


# ROTA PARA EDITAR O USUÁRIO PELO ID
@app.route('/api/usuarios/<int:id>', methods=['PUT'])
@precisa_login
@precisa_ser_admin
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    data = request.get_json()
    # Só permite editar email e senha (por segurança)
    if 'email' in data:
        # Checa se já existe outro usuário com esse email
        if Usuario.query.filter(Usuario.email == data['email'], Usuario.id != id).first():
            return jsonify({'erro': 'Email já cadastrado'}), 400
        usuario.email = data['email']
    if 'senha' in data:
        usuario.set_senha(data['senha'])

    db.session.commit()
    return jsonify({'mensagem': 'Usuário atualizado com sucesso!'})


# ROTA PARA DELETAR USUÁRIO PELO ID
@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
@precisa_login
@precisa_ser_admin
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    # Se for paciente, deleta o paciente (e as consultas dele)
    if usuario.tipo == 'paciente' and usuario.paciente_id:
        paciente = Paciente.query.get(usuario.paciente_id)
        if paciente:
            db.session.delete(paciente)

    # Se for profissional, deleta o profissional (e as consultas dele)
    elif usuario.tipo == 'profissional' and usuario.profissional_id:
        profissional = Profissional.query.get(usuario.profissional_id)
        if profissional:
            db.session.delete(profissional)

    # Por fim, deleta o usuário
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensagem': f'Usuário {id} deletado com sucesso!'})



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
def buscar_paciente(id):
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
def editar_paciente(id):
    paciente = Paciente.query.get(id)
    if not paciente:
        return jsonify({'erro': 'Paciente não encontrado'}), 404

    data = request.get_json()
    paciente.nome = data.get('nome', paciente.nome)
    paciente.data_nascimento = data.get('data_nascimento', paciente.data_nascimento)
    paciente.cpf = data.get('cpf', paciente.cpf)
    paciente.endereco = data.get('endereco', paciente.endereco)
    paciente.telefone = data.get('telefone', paciente.telefone)

    db.session.commit()
    return jsonify({'mensagem': 'Paciente atualizado com sucesso!'})


# ROTA PARA EXCLUIR PACIENTE PELO ID
@app.route('/api/pacientes/<int:id>', methods=['DELETE'])
@precisa_login
@precisa_ser_admin
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


# ROTA PARA LISTAR PROFISSIONAIS
@app.route('/api/profissionais', methods=['GET'])
def listar_profissionais():
    # Pega todos os profissionais do banco
    profissionais = Profissional.query.all()
    lista = []

    for p in profissionais:
        lista.append({
            'id': p.id,
            'nome': p.nome,
            'especialidade': p.especialidade,
            'crm': p.crm,
            'telefone': p.telefone,
            'email': p.email
        })

    return jsonify(lista)


# ROTA PARA BUSCAR PROFISSIONAL PELO ID
@app.route('/api/profissionais/<int:id>', methods=['GET'])
def buscar_profissional(id):
    prof = Profissional.query.get(id)
    
    if not prof:
        
        return jsonify({'erro': 'Profissional não encontrado'}), 404
    
    dados = {
        'id': prof.id,
        'nome': prof.nome,
        'especialidade': prof.especialidade,
        'crm': prof.crm,
        'telefone': prof.telefone,
        'email': prof.email
    }
    
    return jsonify(dados)


# ROTA PARA EDITAR INFORMAÇÕES DO PROFISSIONAL PELO ID
@app.route('/api/profissionais/<int:id>', methods=['PUT'])
def editar_profissional(id):
    prof = Profissional.query.get(id)
    if not prof:
        return jsonify({'mensagem': 'Profissional não encontrado'}), 404
    dados = request.get_json()
    prof.nome = dados.get('nome', prof.nome)
    prof.especialidade = dados.get('especialidade', prof.especialidade)
    prof.crm = dados.get('crm', prof.crm)
    prof.telefone = dados.get('telefone', prof.telefone)
    prof.email = dados.get('email', prof.email)
    db.session.commit()
    return jsonify({'mensagem': 'Profissional atualizado com sucesso!'})


# ROTA PARA DELETAR UM PROFISSIONAL PELO ID
@app.route('/api/profissionais/<int:id>', methods=['DELETE'])
@precisa_login
@precisa_ser_admin
def deletar_profissional(id):
    prof = Profissional.query.get(id)
    if not prof:
        return jsonify({'mensagem': 'Profissional não encontrado'}), 404
    db.session.delete(prof)
    db.session.commit()
    return jsonify({'mensagem': 'Profissional deletado com sucesso!'})


# ===== ROTAS DE CONSULTAS =====

# ROTA PARA CRIAR UMA CONSILTA
@app.route('/api/consultas', methods=['POST'])
def criar_consulta():
    data = request.get_json()
    data_hora = datetime.strptime(data.get('data_hora'), '%Y-%m-%d %H:%M')
    paciente_id = data.get('paciente_id')
    profissional_id = data.get('profissional_id')
    status = data.get('status', 'agendada')
    observacoes = data.get('observacoes', '')

    # Verifica se mandou os campos obrigatórios
    if not paciente_id or not profissional_id or not data_hora:
        return jsonify({'erro': 'Campos obrigatórios não informados'}), 400

    # Verifica se o paciente existe
    paciente = Paciente.query.get(paciente_id)
    if not paciente:
        return jsonify({'erro': 'Paciente não encontrado'}), 404

    # Verifica se o profissional existe
    profissional = Profissional.query.get(profissional_id)
    if not profissional:
        return jsonify({'erro': 'Profissional não encontrado'}), 404

    consulta = Consulta(
        data_hora=data_hora,
        paciente_id=paciente_id,
        profissional_id=profissional_id,
        status=status,
        observacoes=observacoes
    )
    db.session.add(consulta)
    db.session.commit()
    return jsonify({'mensagem': 'Consulta agendada com sucesso!'}), 201


# ROTA QUE LISTA TODAS AS CONSULTAS
@app.route('/api/consultas', methods=['GET'])
def listar_consultas():
    consultas = Consulta.query.all()
    lista = []
    for c in consultas:
        lista.append({
            'id': c.id,
            'data_hora': c.data_hora.strftime('%Y-%m-%d %H:%M'),
            'paciente_id': c.paciente_id,
            'profissional_id': c.profissional_id,
            'status': c.status,
            'observacoes': c.observacoes
        })
    return jsonify(lista)


# ROTA QUE BUSCA A CONSULTA PELO ID
@app.route('/api/consultas/<int:id>', methods=['GET'])
def buscar_consulta(id):
    c = Consulta.query.get(id)
    if not c:
        return jsonify({'erro': 'Consulta não encontrada'}), 404
    return jsonify({
        'id': c.id,
        'data_hora': c.data_hora.strftime('%d-%m-%Y %H:%M'),
        'paciente_id': c.paciente_id,
        'profissional_id': c.profissional_id,
        'status': c.status,
        'observacoes': c.observacoes
    })


# ROTA QUE LISTA TODAS AS CONSULTAS DE UM PACIENTE ESPECÍFICO
@app.route('/api/pacientes/<int:id_paciente>/consultas', methods=['GET'])
def listar_consultas_paciente(id_paciente):
    try:
        # Verifica se o paciente existe
        paciente = Paciente.query.get(id_paciente)
        if not paciente:
            return jsonify({'erro': 'Paciente não encontrado'}), 404

        # Busca todas as consultas desse paciente
        consultas = Consulta.query.filter_by(paciente_id=id_paciente).all()

        lista_consultas = []
        for consulta in consultas:
            # Pega a data e hora certinho
            lista_consultas.append({
                'id': consulta.id,
                'data': consulta.data_hora.strftime('%Y-%m-%d'),
                'hora': consulta.data_hora.strftime('%H:%M'),
                'profissional_id': consulta.profissional_id,
                'status': consulta.status
            })

        return jsonify(lista_consultas)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ROTA QUE LISTA TODAS AS CONSULTAS DE UM PROFISSIONAL ESPECÍFICO
@app.route('/api/profissionais/<int:id_profissional>/consultas', methods=['GET'])
def listar_consultas_profissional(id_profissional):
    try:
        # Verifica se o profissional existe
        profissional = Profissional.query.get(id_profissional)
        if not profissional:
            return jsonify({'erro': 'Profissional não encontrado'}), 404

        # Busca todas as consultas desse profissional
        consultas = Consulta.query.filter_by(profissional_id=id_profissional).all()

        lista_consultas = []
        for consulta in consultas:
            lista_consultas.append({
                'id': consulta.id,
                'data': consulta.data_hora.strftime('%Y-%m-%d'),
                'hora': consulta.data_hora.strftime('%H:%M'),
                'paciente_id': consulta.paciente_id,
                'status': consulta.status
            })

        return jsonify(lista_consultas)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ROYA QUE EDITA A CONSULTA PELO ID
@app.route('/api/consultas/<int:id>', methods=['PUT'])
def editar_consulta(id):
    c = Consulta.query.get(id)
    if not c:
        return jsonify({'erro': 'Consulta não encontrada'}), 404
    data = request.get_json()
    if 'data_hora' in data:
        c.data_hora = datetime.strptime(data['data_hora'], '%Y-%m-%d %H:%M')
    c.paciente_id = data.get('paciente_id', c.paciente_id)
    c.profissional_id = data.get('profissional_id', c.profissional_id)
    c.status = data.get('status', c.status)
    c.observacoes = data.get('observacoes', c.observacoes)
    db.session.commit()
    return jsonify({'mensagem': 'Consulta atualizada com sucesso!'})



# ROTA PARA DELETAR A CONSULTA PELO ID
@app.route('/api/consultas/<int:id>', methods=['DELETE'])
@precisa_login
def deletar_consulta(id):
    consulta = Consulta.query.get(id)
    if not consulta:
        return jsonify({'erro': 'Consulta não encontrada'}), 404

    usuario_id = session.get('usuario_id')
    tipo_usuario = session.get('tipo_usuario')

    # Só o admin ou o paciente dono pode deletar
    if tipo_usuario == 'admin' or (tipo_usuario == 'paciente' and consulta.paciente_id == Usuario.query.get(usuario_id).paciente_id):
        db.session.delete(consulta)
        db.session.commit()
        return jsonify({'mensagem': 'Consulta deletada com sucesso!'})
    else:
        return jsonify({'erro': 'Você não tem permissão para deletar esta consulta'}), 403



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


# ===== DELETAR O BANDO DE DADOS =====
# Facilitar nos testes caso algum relacionamento entre classes não remova alguma informação
@app.route('/api/reset-database', methods=['POST'])
@precisa_login
@precisa_ser_admin
def reset_database():
    # Deleta tudo na ordem correta
    Consulta.query.delete()
    Usuario.query.delete()
    Paciente.query.delete()
    Profissional.query.delete()
    Contato.query.delete()

    db.session.commit()
    return jsonify({'mensagem': 'Banco de dados zerado com sucesso!'})