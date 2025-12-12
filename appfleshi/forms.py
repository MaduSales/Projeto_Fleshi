from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp #Usando Regex para validar senha

from appfleshi import bcrypt
from appfleshi.models import User


class PhotoForm(FlaskForm):
    photo = FileField("Foto", validators=[DataRequired()])
    submit = SubmitField("Postar")
    caption = StringField("Legenda", validators=[Length(max=42)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("E-mail inválido!")
        return None

    def validate_password(self, password):
        if self.email.errors:
            return None

        user = User.query.filter_by(email=self.email.data).first()
        if not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError("Senha inválida!")
        return None


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8, max=60), Regexp(regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,60}', message="A senha precisa ter pelo menos 1 caracter maiúsculo, 1 minúsculo, 1 número e 1 caracter especial.")])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas não são iguais!')])
    submit = SubmitField('Criar Conta')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("E-mail já cadastrado")
        return None

    def validate_username(self, username):
        if self.email.errors:
            return None

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("O usuário já existe")
        return None

