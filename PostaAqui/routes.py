#Extensões
from PostaAqui.forms import formconta, formlogin, formfoto, formpesquisa
from flask import render_template, url_for, redirect, session, send_from_directory, request, jsonify
from PostaAqui import app, bcrypt, db, mail
from PostaAqui.models import Usuario, Foto, Denuncia
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from rapidfuzz import fuzz
import random, os
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

#homepage com sistema de login
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
        <h1>Confirmação de E-mail – Poste Aqui</h1>

        <p>Olá,</p>

        <p>Recebemos um pedido de cadastro utilizando este endereço de e-mail na plataforma <strong>Poste Aqui</strong>.</p>

        <p>Para ativar sua conta e concluir o processo de verificação, por favor clique no link abaixo:</p>

        <p><a href="{link}" style="background-color: #007BFF; color: #ffffff; padding: 10px 20px; text-decoration: none; 
        border-radius: 5px;">Confirmar E-mail</a></p>

        <p>Se você não realizou este cadastro, pode simplesmente ignorar esta mensagem. Nenhuma ação adicional será tomada.</p>
        
        <hr>

        <p>Esta é uma mensagem automática. Em caso de dúvidas, entre em contato com nossa equipe em 
        <a href="mailto:techimperium.ti@gmail.com">techimperium.ti@gmail.com</a>.</p>
        
        <p>Atenciosamente, <br> Equipe Poste Aqui.</p>"""

        mail.send(msg)

        return render_template("verificacaodeemail.html")
    
    return render_template("criarconta.html", form=form)

#Rota de confirmação de email
@app.route("/confirmar_email/<token>")
def confirmar_email(token):
    try:
        email = serializer.loads(token, salt="verificacao-email", max_age=1200) 
    except:
        "Link inválido ou expirado"

    dados = session.get("dados_temp")

    #comparar os email temp com a variavel email
    if not dados or dados["email"] != email:
        return "Erro: dados não encontrados ou e-mail não confere."

    # Criar o usuário no bd
    novo_usuario = Usuario(name=dados["name"], email=dados["email"], senha=dados["senha"])
    db.session.add(novo_usuario)
    db.session.commit()

    login_user(novo_usuario)
    session.pop("dados_temp", None)

    return redirect(url_for("perfil", id_usuario=novo_usuario.id))

#perfil do usuario
@app.route("/perfil/<id_usuario>", methods=["POST", "GET"])
@login_required
def perfil(id_usuario):
    usuario = Usuario.query.get(int(id_usuario))
    Formfoto = formfoto()

    # paginação (padrão = 1)
    page = request.args.get('page', 1, type=int)
    fotos_paginadas = Foto.query.filter_by(id_usuario=usuario.id).order_by(Foto.id.desc()).paginate(page=page, per_page=12)

    if int(id_usuario) == int(current_user.id):
        # O usuário está no próprio perfil
        if Formfoto.validate_on_submit():
            arquivo = Formfoto.foto.data
            if arquivo:
                nomeseguro = secure_filename(arquivo.filename)

                # Salvar o arquivo na pasta
                caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                       app.config["UPLOAD_FOLDER"], nomeseguro)
                arquivo.save(caminho)

                tag = Formfoto.tag.data.strip()
                nomefoto = Formfoto.nome_foto.data.strip()

                foto = Foto(imagem=nomeseguro, id_usuario=current_user.id, tags=tag, nome_foto=nomefoto)
                db.session.add(foto)
                db.session.commit()

                return redirect(url_for("perfil", id_usuario=current_user.id))

        return render_template("perfilpage.html", usuario=current_user, form=Formfoto, fotos_paginadas=fotos_paginadas)

    else:
        # O usuário está no perfil de outra pessoa
        return render_template("perfilpage.html", usuario=usuario, form=None, fotos_paginadas=fotos_paginadas)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

#rota do feed
@app.route("/feed", methods=["GET", "POST"])
def feed():
    Formpesquisa = formpesquisa()

    #paginação
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Pega até 200 fotos aleatórias a cada acesso
    todas_fotos = Foto.query.all()
    fotos_selecionadas = random.sample(todas_fotos, min(1200, len(todas_fotos)))
    todas_fotos_lista = fotos_selecionadas

    # Sistema de pesquisa
    if Formpesquisa.validate_on_submit():
        busca = Formpesquisa.Barra_de_pesquisa.data.lower()
        resultados_relevantes = []
        resultados_ids = set()

        # pesquisa com base na tag
        for foto in todas_fotos_lista:
            otimizacao_tag = [tag[1:].lower() for tag in foto.tags.split() if tag.startswith("#")]
            for tag in otimizacao_tag:
                if fuzz.partial_ratio(busca, tag) > 70:
                    resultados_relevantes.append(foto)
                    resultados_ids.add(foto.id)
                    break

        # Preencher com fotos aleatórias não relacionadas
        restantes = [f for f in todas_fotos_lista if f.id not in resultados_ids]
        random.shuffle(restantes)

        fotos_ordenadas = resultados_relevantes + restantes
        fotos_final = fotos_ordenadas

    else:
        fotos_final = todas_fotos_lista  # exibir aleatórias diretamente

    # Paginação manual
    total = len(fotos_final) # Total de fotos disponíveis
    start = (page - 1) * per_page # Índice inicial da página
    end = start + per_page # Índice final da página
    fotos_paginadas = fotos_final[start:end] # Recorte apenas das fotos dessa página

    class FakePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page #Calcula o número total de páginas

        #logica da paginação manual
        def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if (
                    num <= left_edge
                    or (num >= self.page - left_current and num <= self.page + right_current)
                    or num > self.pages - right_edge
                ):
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

        @property
        def has_prev(self):
            return self.page > 1

        @property
        def has_next(self):
            return self.page < self.pages

        @property
        def prev_num(self):
            return self.page - 1

        @property
        def next_num(self):
            return self.page + 1

    pagination = FakePagination(fotos_paginadas, page, per_page, total)

    return render_template("feed.html", fotos_paginadas=pagination, Formpesquisa=Formpesquisa)

#sistema de download
@app.route("/Download/<filename>")
def Download_de_Arquivos (filename):
    caminho = os.path.join(app.root_path, "static", "post")
    return send_from_directory(caminho, filename, as_attachment=True)

#sistema de excluir
@app.route("/excluir/<int:id_usuario>/<filename>")
def excluir_arquivos(id_usuario, filename):
    if int(id_usuario) == int(current_user.id):
        foto = Foto.query.filter_by(id_usuario=id_usuario, imagem=filename).first()
        if foto:
            db.session.delete(foto)
            db.session.commit()
    return redirect(url_for('perfil', id_usuario=id_usuario))

#sistema de denuncia
@app.route("/denuncia/<filename>")
@login_required
def denuncia_foto(filename):
    foto = Foto.query.filter_by(imagem=filename).first()

    denuncia = Denuncia(id_foto=foto.id, id_usuario=current_user.id)
    db.session.add(denuncia)
    db.session.commit()
    
    total_denuncias = Denuncia.query.filter_by(id_foto=foto.id).count()

    if total_denuncias > 2:
        db.session.delete(foto)
        db.session.commit()
    
    return redirect(request.referrer)

#janela de erro
@app.errorhandler(404)
def pagina_não_encontrada(error):
    return render_template ("error404.html"), 404

@app.errorhandler(500)
def erro_no_servidor(erro):
    return render_template ("error500.html"), 500

#documentação do site
@app.route("/sobre-nos")
def Sobre_nos():
    return render_template("sobre_nos.html")

@app.route("/Termos-de-Uso")
def Termos_de_Uso():
    return render_template("Termos_de_Uso.html")

@app.route("/Politica_de_privacidade")
def Politica_de_privacidade():
    return render_template ("Politica_de_privacidade.html")

@app.route("/perguntas_frequentes")
def perguntas_frequentes():
    return render_template ("perguntas_frequentes.html")

@app.before_request
def forcar_https():
    if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)