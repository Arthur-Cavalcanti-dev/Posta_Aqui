#Extensões
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from PostaAqui.models import Usuario

#Form de login
class formlogin(FlaskForm):
    email = StringField("E-mail", validators=[Email(), DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=3, max=50)])
    login_botao = SubmitField("Entrar")

#Form de nova conta
class formconta(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=3, max=50)])
    username = StringField("Usuário", validators=[DataRequired(), Length(min=3, max=20)])
    confirmacao_de_senha = PasswordField("Confirme sua senha", validators=[EqualTo('senha')])
    conta_botao = SubmitField("Criar conta")

    #verificar se o email já tem cadastro
    def validate_email(self, field):
        usuario = Usuario.query.filter_by(email=field.data).first()
        if usuario:
            raise ValidationError("Este e-mail já está cadastrado.")

#Validação de tag        
def validador_tag (form, field):
    tags = field.data.split(" ")
    for tag in tags:
        tag = tag.strip()
        if not tag.startswith("#"):
            raise ValidationError ("Todas as tags devem começar com #")
        
#Form de foto        
class formfoto(FlaskForm):
    foto = FileField("foto", validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'heic', 'heif']) ])
    botao_enviar = SubmitField("Enviar")
    nome_foto = StringField("Nome da foto", validators=[ DataRequired(), Length(min=2, max=100)],
                      render_kw={"placeholder": "Título..."})
    tag = StringField("Tags", validators=[ DataRequired(), Length(min=2, max=100), validador_tag ],
                      render_kw={"placeholder": "Tags..."})

#form da barra de pesquisa
class formpesquisa (FlaskForm):
    Barra_de_pesquisa = StringField ("Pesquisa", validators= [DataRequired(), Length(min=2, max=40)],
                                      render_kw={"placeholder": "Pesquisar..."})
    botao_pesquisa = SubmitField ("Pesquisar")