#Extensões
from PostaAqui import db, login_manager, app
from flask_login import UserMixin
from datetime import datetime

#pegando o id do usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

#colunas do usuario
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    fotos = db.relationship('Foto', backref='usuario', lazy=True) 

#colunas de foto
class Foto(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(255), default='default.png')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tags = db.Column(db.String(100), nullable = False)
    nome_foto = db.Column(db.String(100), nullable = False)

#colunas de denuncia
class Denuncia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_foto = db.Column(db.Integer, db.ForeignKey('foto.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    data = db.Column(db.DateTime, default=datetime.utcnow)    
denuncias = db.relationship('Denuncia', backref='foto', cascade="all, delete", lazy=True)


with app.app_context():
    db.create_all()
