from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

# Configuração do app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///comunidade.db"
app.config["SECRET_KEY"] = "034846e0b016caf2ef575a271b1e6ab0afed"
app.config["UPLOAD_FOLDER"] = "static/post"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config['MAIL_USERNAME'] = "techimperium.ti@gmail.com"
app.config['MAIL_PASSWORD'] = "xhmkjnieokrkvfkr"

# extensões
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
login_manager.login_view = "homepage"

from PostaAqui import routes