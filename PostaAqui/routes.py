from PostaAqui.forms import formconta, formlogin, formfoto, formpesquisa
from flask import render_template, url_for, redirect, session, send_from_directory
from PostaAqui import app, bcrypt, db, mail
from PostaAqui.models import Usuario, Foto
from flask_login import login_required, login_user, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from rapidfuzz import fuzz
import random
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

@app.route("/", methods=["GET", "POST"])
def homepage():
    form_login = formlogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("homepage.html", form=form_login)

serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

@app.route("/criarconta", methods=["GET", "POST"])
def conta():
    form = formconta()
    if form.validate_on_submit():
        senha_hash = bcrypt.generate_password_hash(form.senha.data).decode("utf-8")

        # Salvar temporariamente os dados
        session["dados_temp"] = {"name": form.username.data, "email": form.email.data, "senha": senha_hash}

        # Gerar token com o email
        token = serializer.dumps(form.email.data, salt="verificacao-email")
        link = url_for("confirmar_email", token=token, _external=True)

        # Enviar o email
        msg = Message("Confirme seu e-mail", sender="techimperium.ti@gmail.com", recipients=[form.email.data])
        msg.body = f"Clique aqui para confirmar seu e-mail: {link}"
        msg.html = f"""
            <h1>Bem-vindo à nossa plataforma!</h1>
            <p>Para confirmar seu e-mail, clique no link abaixo:</p>
            <a href="{link}">Confirmar e-mail</a>
            <p>Se você não se cadastrou, ignore esta mensagem.</p>
            """
        mail.send(msg)

        return render_template("verificacaodeemail.html")
    
    return render_template("criarconta.html", form=form)


@app.route("/confirmar_email/<token>")
def confirmar_email(token):
    try:
        email = serializer.loads(token, salt="verificacao-email", max_age=1200) 
    except:
        return "Link inválido ou expirado."

    dados = session.get("dados_temp")

    if not dados or dados["email"] != email:
        return "Erro: dados não encontrados ou e-mail não confere."

    # Criar o usuário no bd
    novo_usuario = Usuario(name=dados["name"], email=dados["email"], senha=dados["senha"])
    db.session.add(novo_usuario)
    db.session.commit()

    login_user(novo_usuario)
    session.pop("dados_temp", None)

    return redirect(url_for("perfil", id_usuario=novo_usuario.id))


@app.route("/perfil/<id_usuario>", methods = ["POST", "GET"])  
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):

        # O usuario ta no seu perfil
        Formfoto = formfoto ()
        if Formfoto.validate_on_submit():
            arquivo = Formfoto.foto.data
            if arquivo:
                nomeseguro = secure_filename(arquivo.filename)

                # Salvar o arquivo na pasta
                caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                       app.config["UPLOAD_FOLDER"], nomeseguro)
                arquivo.save(caminho)
                
                tag = Formfoto.tag.data.strip()
                # Salvar o arquivo no bd

                foto = Foto(imagem=nomeseguro, id_usuario=current_user.id, tags = tag)
                db.session.add(foto)
                db.session.commit()
                return redirect(url_for("perfil", id_usuario=current_user.id))

        return render_template("perfilpage.html", usuario=current_user, form=Formfoto)
    
    else:
        # O usuario está em outra conta
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfilpage.html", usuario = usuario, form = None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route ("/feed", methods=["GET", "POST"])
def feed ():
    Formpesquisa = formpesquisa()
    fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()[:200]
    todas_as_fotos = Foto.query.all()
    Buscar = ""
    resultado = []

    # sistema da barra de pesquisa
    if Formpesquisa.validate_on_submit():
        busca = Formpesquisa.Barra_de_pesquisa.data.lower()
        for foto in fotos:
            otimizacao_tag = [tag[1:].lower() for tag in foto.tags.split() if tag.startswith("#")]
            for tag in otimizacao_tag:
                if fuzz.partial_ratio(busca, tag) > 70:
                    resultado.append(foto)
                    break
        fotos = resultado

        # Fotos aleátorias a baixo das que foram pesquisadas
        if len(fotos) < 10:
            fotos_ids = [f.id for f in fotos]
            outras_fotos = [f for f in todas_as_fotos if f.id not in fotos_ids]
            fotos_aleatorias = random.sample(outras_fotos, min(10 - len(fotos), len(outras_fotos)))
            fotos.extend(fotos_aleatorias)
        else:
            fotos = todas_as_fotos


    return render_template ("feed.html", fotos = fotos, Formpesquisa = Formpesquisa)

@app.route("/Download/<filename>")
def Download_de_Arquivos (filename):
    caminho = os.path.join(app.root_path, "static", "post")
    return send_from_directory(caminho, filename, as_attachment=True)
