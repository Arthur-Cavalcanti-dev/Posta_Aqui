from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from savedphotos.models import Usuario

class formlogin(FlaskForm):
    email = StringField("E-mail", validators=[Email(), DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=3, max=50)])
    login_botao = SubmitField("Entrar")

class formconta(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=3, max=50)])
    username = StringField("Usuário", validators=[DataRequired(), Length(min=3, max=20)])
    confirmacao_de_senha = PasswordField("Confirme sua senha", validators=[EqualTo('senha')])
    conta_botao = SubmitField("Criar conta")

    def validate_email(self, field):
        usuario = Usuario.query.filter_by(email=field.data).first()
        if usuario:
            raise ValidationError("Este e-mail já está cadastrado.")
        
class fromfoto(FlaskForm):
    foto = FileField("foto", validators=[DataRequired()])
    botao_enviar = SubmitField("Enviar")
    botao_cancelar = SubmitField("Cancelar")
