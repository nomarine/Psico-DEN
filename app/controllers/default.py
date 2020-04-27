import os
from app import app, db, login_manager, ALLOWED_EXTENSIONS
from app.models.tables import User, Comment, Paciente, UF, Usuario, Agendamento, Arquivo, Gravacao, Genero, Religiao, Sessao, Contato
from datetime import datetime, date, time
from flask import render_template, redirect, request, url_for, send_from_directory, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.filter_by(username=user_id).first()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def autenticar_senha(senha, conf_senha):
    if senha != conf_senha:
        return False
    return True

def autenticar_usuario(usuario):
    usuario = Usuario.query.filter_by(username=usuario).first()
    if usuario is None:
        return True
    return False

### ROTAS BÁSICAS ###

@app.route("/dashboard")
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    return render_template('dashboard.html')

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=False)

    login_usuario = load_user(request.form["login_Usuario"])
    if login_usuario is None:
        return render_template("login.html", error=True)

    if not login_usuario.verificar_Senha(request.form["senha_Usuario"]):
        return render_template("login.html", error=True)

    login_user(login_usuario)
    return redirect(url_for('dashboard'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/upload", methods=["GET", "POST"])
def upload_Arquivo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('upload_Arquivo')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('upload_Arquivo'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            arquivo = Arquivo(titulo = filename,
                              caminho = "/./static/arquivos/" + filename)
            db.session.add(arquivo)
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    return render_template("upload_arquivo.html", arquivos = Arquivo.query.all());

@app.route("/gravador", methods=["GET", "POST"])
def gravador_Audio():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('gravador')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('gravador'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            gravacao = Gravacao(titulo = filename,
                               caminho = "/./static/gravacoes/" + filename)
            db.session.add(gravacao)
            db.session.commit()
            file.save(os.path.join('/home/nomarine/PsicoDEN/app/static/gravacoes', filename))
            #return redirect(url_for('uploaded_file',
             #                       filename=filename))
    return render_template("gravador_audio.html", gravacoes = Gravacao.query.all())

### ROTAS DE EXCLUSÃO ###

@app.route("/apagar_paciente")
def apagar_paciente():
    agendamento = Agendamento.query.filter_by(paciente_id=request.args["paciente_id"]).first()
    if agendamento is not None:
        sessao = Sessao.query.filter_by(agendamento_id=agendamento.id).first()
        if sessao is not None:
            Sessao.query.filter_by(agendamento_id=agendamento.id).delete()
        Agendamento.query.filter_by(paciente_id=request.args["paciente_id"]).delete()
    Paciente.query.filter_by(id=request.args["paciente_id"]).delete()
    db.session.commit()
    return redirect(url_for('lista_pacientes'))

@app.route("/apagar_arquivo")
def apagar_arquivo():
    Arquivo.query.filter_by(id=request.args["arquivo_id"]).delete()
    db.session.commit()
    return redirect(url_for('lista_Arquivos'))

@app.route("/apagar_agendamento")
def apagar_agendamento():
    Agendamento.query.filter_by(id=request.args["agendamento_id"]).delete()
    db.session.commit()
    return redirect(url_for('lista_Agendamentos'))

@app.route("/apagar_contato")
def apagar_Contato():
    Contato.query.filter_by(id=request.args["contato_id"]).delete()
    db.session.commit()
    return redirect(url_for('lista_Contato'))

### ROTAS DE CADASTRO ###

@app.route("/cadastro_prontuario", methods=["GET", "POST"])
def cadastro_prontuario():
    if request.method == "GET":
        return render_template("cadastro_prontuario.html", pacientes=Paciente.query.all(),
                                                           uf=UF.query.all(),
                                                           genero=Genero.query.all(),
                                                           religiao=Religiao.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    foto = request.files['foto_Paciente']
    nome_arquivo = secure_filename(foto.filename)
    hoje = date.today()
    paciente = Paciente(nome=request.form["nome_Paciente"],
                        data_nasc=request.form["datanasc_Paciente"],
                        idade=request.form["idade_Paciente"],
                        cpf=request.form["cpf_Paciente"],
                        rg=request.form["rg_Paciente"],
                        est_civil=request.form["estadocivil_Paciente"],
                        cep=request.form["cep_Paciente"],
                        endereco=request.form["endereco_Paciente"],
                        cidade=request.form["cidade_Paciente"],
                        observacao=request.form["observacao_Paciente"],
                        uf_id=request.form["estado_Paciente"],
                        genero_id=request.form["genero_Paciente"],
                        religiao_id=request.form["religiao_Paciente"],
                        foto="/./static/fotos/" + nome_arquivo,
                        )
    db.session.add(paciente)
    db.session.commit()
    paciente.idade = hoje.year - paciente.data_nasc.year
    db.session.commit()
    foto.save(os.path.join('/home/nomarine/PsicoDEN/app/static/fotos', nome_arquivo))
    return redirect(url_for('lista_pacientes'))

@app.route("/cadastro_agendamento", methods=["GET", "POST"])
def cadastro_Agendamento():
    if request.method == "GET":
        return render_template("cadastro_agendamentos.html", pacientes=Paciente.query.all(), agendamentos=Paciente.query.all());

    agendamento = Agendamento(data=request.form["data_Agendamento"],
                              horario=request.form["horario_Agendamento"],
                              assunto=request.form["assunto_Agendamento"],
                              paciente_id=request.form["nome_Paciente"],
                              )

    db.session.add(agendamento)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/cadastro_contato", methods=["GET", "POST"])
def cadastro_Contato():
    if request.method == "GET":
        return render_template("cadastro_contato.html", contato=Contato.query.all());

    contato = Contato(nome=request.form["nome_contato"],
                      telefone_1=request.form["telefone1_contato"],
                      telefone_2=request.form["telefone2_contato"],
                      email=request.form["email_contato"],
                      info=request.form["info_contato"],
                      )

    db.session.add(contato)
    db.session.commit()
    return redirect(url_for('lista_Contato'))

@app.route("/cadastro_sessao", methods=["GET", "POST"])
def cadastro_Sessao():
    if request.method == "GET":
        return render_template("cadastro_sessao.html", agendamento=Agendamento.query.filter_by(id=request.args["agendamento_id"]).first(),
                                                       sessao=Sessao.query.all());

    file = request.files['file']
    filename = secure_filename(file.filename)
    gravacao = Gravacao(titulo = filename,
                       caminho = "/./static/gravacoes/" + filename)
    db.session.add(gravacao)
    db.session.commit()
    file.save(os.path.join('/home/nomarine/PsicoDEN/app/static/gravacoes', filename))
    #return redirect(url_for('uploaded_file',
     #                       filename=filename))
    sessao = Sessao(transcricao=request.form["transcricao_Sessao"],
            agendamento_id=request.args["agendamento_id"],
            gravacao_id=gravacao.id,
            )
    db.session.add(sessao)
    db.session.commit()

    return redirect(url_for('lista_Sessao'))

@app.route("/cadastro_usuario", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method == "GET":
        return render_template("cadastro_usuario.html")

    if not autenticar_senha(request.form["senha_Usuario"], request.form["senha_conf_Usuario"]):
        return render_template("cadastro_usuario.html", error=True)

    if not autenticar_usuario(request.form["nome_Usuario"]):
        return render_template("cadastro_usuario.html", error=True)

    usuario = Usuario(username=request.form["nome_Usuario"],
                      password_hash=(request.form["senha_Usuario"]),
                     )
    db.session.add(usuario)
    db.session.commit()
    return render_template("login.html")

### ROTAS DE PÁGINAS RELATIVAS ###


@app.route("/prontuario", methods=["GET"])
def prontuario():
    return render_template("prontuario.html", pacientes = Paciente.query.filter_by(id=request.args["paciente_id"]).first(),
                                              paciente = request.args["paciente_id"],
                                              hoje = date.today());

@app.route("/agendamento", methods=["GET"])
def agendamento():
    if request.method == "GET":
        return render_template("agendamento.html", agendamento=Agendamento.query.filter_by(id=request.args["agendamento_id"]).first())

@app.route("/sessao", methods=["GET"])
def sessao():
    if request.method == "GET":
        return render_template("sessao.html", sessao=Sessao.query.filter_by(id=request.args["sessao_id"]).first())

@app.route("/contato", methods=["GET"])
def contato():
    if request.method == "GET":
        return render_template("contato.html", contato=Contato.query.filter_by(id=request.args["contato_id"]).first())


### ROTA DE LISTAGENS ###

@app.route("/lista_pacientes", methods=["GET"])
def lista_pacientes():
    if request.method == "GET":
        return render_template("pacientes.html", pacientes=Paciente.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

@app.route("/lista_agendamentos", methods=["GET"])
def lista_Agendamentos():
    if request.method == "GET":
        return render_template("lista_agendamentos.html", agendamentos=Agendamento.query.all())

@app.route("/lista_contato", methods=["GET"])
def lista_Contato():
    if request.method == "GET":
        return render_template("lista_contatos.html", contatos=Contato.query.all())

@app.route("/lista_gravacoes", methods=["GET"])
def lista_Gravacoes():
    if request.method == "GET":
        return render_template("lista_gravacoes.html", gravacoes=Gravacao.query.all())

@app.route("/lista_arquivos", methods=["GET"])
def lista_Arquivos():
    if request.method == "GET":
        return render_template("lista_arquivos.html", arquivos=Arquivo.query.all())

@app.route("/lista_sessao", methods=["GET"])
def lista_Sessao():
    if request.method == "GET":
        return render_template("lista_sessao.html", sessoes=Sessao.query.all())

### ROTAS DE ALTERALÇÃO ###

@app.route("/alteracao_paciente", methods=["GET", "POST"])
def alteracao_paciente():
    if request.method == "GET":
        return render_template("alteracao_paciente.html", pacientes = Paciente.query.filter_by(id=request.args["paciente_id"]).first(),
                                                           uf=UF.query.all(),
                                                           genero=Genero.query.all(),
                                                           religiao=Religiao.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    pacientes = Paciente.query.filter_by(nome=request.args["nome_paciente"]).first()
    foto = request.files['foto_Paciente']
    nome_arquivo = secure_filename(foto.filename)
    pacientes.nome=request.form["nome_Paciente"]
    pacientes.data_nasc=request.form["datanasc_Paciente"]
    pacientes.idade=request.form["idade_Paciente"]
    pacientes.cpf=request.form["cpf_Paciente"]
    pacientes.rg=request.form["rg_Paciente"]
    pacientes.est_civil=request.form["estadocivil_Paciente"]
    pacientes.cep=request.form["cep_Paciente"]
    pacientes.endereco=request.form["endereco_Paciente"]
    pacientes.cidade=request.form["cidade_Paciente"]
    pacientes.uf_id=request.form["estado_Paciente"]
    pacientes.genero_id=request.form["genero_Paciente"]
    pacientes.religiao_id=request.form["religiao_Paciente"]
    pacientes.foto="/./static/fotos/" + nome_arquivo
    db.session.commit()
    foto.save(os.path.join('/home/nomarine/PsicoDEN/app/static/fotos', nome_arquivo))
    return redirect(url_for('dashboard'))

### CAMINHOS DE TESTE ###

#@login_manager.user_loader
#def load_user(user_id):
#    return User.query.filter_by(username=user_id).first()

@app.route("/comentarios", methods=["GET", "POST"])
def comentario():
    if request.method == "GET":
        return render_template("comments.html", comments=Comment.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('comentario'))

    comment = Comment(content=request.form["conteudo"])
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('comentario'))


@app.route("/logar/", methods=["GET", "POST"])
def logar():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    username = request.form["username"]
    if username is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('comentario'))

@app.route("/deslogar/")
@login_required
def deslogar():
    logout_user()
    return redirect(url_for('comentario'))