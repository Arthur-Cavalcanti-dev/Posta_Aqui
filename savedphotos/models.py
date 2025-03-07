from savedphotos import db, login_manager, app
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    fotos = db.relationship('Foto', backref='usuario', lazy=True) 

class Foto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(255), default='default.png')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)


with app.app_context():
    db.create_all()
