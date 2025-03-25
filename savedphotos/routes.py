# criar rotas/link do site

from savedphotos.forms import formconta, formlogin
from flask import render_template, url_for, redirect
from savedphotos import app, bcrypt, db
from savedphotos.models import Usuario, Foto
from flask_login import login_required, login_user, logout_user, current_user


@app.route("/", methods=["GET", "POST"])
def homepage():
    form = formlogin()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))  # Corrigido para passar id_usuario
    return render_template("homepage.html", form=form)


@app.route("/criarconta", methods=["GET", "POST"])
def conta():
    form_criar_conta = formconta()
    if form_criar_conta.validate_on_submit():
        senha_hash = bcrypt.generate_password_hash(form_criar_conta.senha.data).decode("utf-8")
        usuario = Usuario(name=form_criar_conta.username.data, senha=senha_hash, email=form_criar_conta.email.data)
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))  # Corrigido para passar id_usuario
    return render_template("criarconta.html", form=form_criar_conta)


@app.route("/perfil/<id_usuario>")  
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        # O usuario ta no seu perfil
        return render_template("perfilpage.html", usuario=current_user)
    else:
        usuario = Usuario.query.get(int(id_usuario))
       


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))
