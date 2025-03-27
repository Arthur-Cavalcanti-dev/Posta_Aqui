# criar rotas/link do site

from savedphotos.forms import formconta, formlogin, formfoto
from flask import render_template, url_for, redirect
from savedphotos import app, bcrypt, db
from savedphotos.models import Usuario, Foto
from flask_login import login_required, login_user, logout_user, current_user
import os
from werkzeug.utils import secure_filename

@app.route("/", methods=["GET", "POST"])
def homepage():
    form_login = formlogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("homepage.html", form=form_login)


@app.route("/criarconta", methods=["GET", "POST"])
def conta():
    form_criar_conta = formconta()
    if form_criar_conta.validate_on_submit():
        senha_hash = bcrypt.generate_password_hash(form_criar_conta.senha.data).decode("utf-8")
        usuario = Usuario(name=form_criar_conta.username.data, senha=senha_hash, email=form_criar_conta.email.data)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form=form_criar_conta)


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

                # Salvar o arquivo no bd
                foto = Foto(imagem=nomeseguro, id_usuario=current_user.id)
                db.session.add(foto)
                db.session.commit()

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
