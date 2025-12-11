from flask import render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from appfleshi import app
from appfleshi.forms import LoginForm, RegisterForm, PhotoForm
from appfleshi import app, database, bcrypt
from appfleshi.models import User, Photo, Like
import os
from werkzeug.utils import secure_filename

@app.route('/', methods=['GET', 'POST'])
def homepage():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('feed'))
    return render_template('homepage.html', form=login_form)

@app.route("/createaccount", methods=['GET', 'POST'])
def createaccount():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        password = bcrypt.generate_password_hash(register_form.password.data)
        user = User(username=register_form.username.data, password=password, email=register_form.email.data)
        database.session.add(user)
        database.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('profile', user_id=user.id))
    return render_template('createaccount.html', form=register_form)

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if int(user_id) == current_user.id:
        photo_form = PhotoForm()
        if photo_form.validate_on_submit():
            file = photo_form.photo.data #Pega o arquivo
            secure_name = secure_filename(file.filename) #Gera um nome seguro
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], secure_name) #Cria uma variável para armazenar o caminho static/posts_photos/nome_arquivo.png
            file.save(path) #Salva o caminho
            photo = Photo(file_name = secure_name, user_id = current_user.id)
            database.session.add(photo)
            database.session.commit()
        return render_template('profile.html', user=current_user, form=photo_form)
    else:
        user = User.query.get(int(user_id))
        return render_template('profile.html', user=user, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route("/feed")
@login_required
def feed():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()

    for photo in photos:
        photo.user_liked = any(like.user_id == current_user.id for like in photo.likes)
        # O código percorre a lista de fotos do feed e define o valor da variável "photo.user_liked" de acordo com o valor retornado pelo "any",
        # já que a lista de likes do objeto fotos é percorrida e compara o id do user que curtiu com o id do user atual. Se os ids forem iguais,
        # é armazenado o valor TRUE na variável user_liked, que será usado para mostrar a cor do botão no feed


    return render_template("feed.html", photos=photos)


@app.route("/like/<int:photo_id>", methods=['POST'])
def like_photo(photo_id):
    photo = Photo.query.get(photo_id)

    existing_likes = Like.query.filter_by(photo_id=photo_id, user_id=current_user.id).first()

    if existing_likes:
        database.session.delete(existing_likes)
    else:
        like = Like(photo_id=photo_id, user_id=current_user.id)
        database.session.add(like)

    database.session.commit()

    return redirect(url_for('feed', user_id=current_user.id))

