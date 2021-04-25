import os
from flask import Flask
from flask import render_template, redirect, make_response, request, abort, jsonify, url_for
from data import db_session
from data.users import User
from data.sell import Sell
from data.jobs import Jobs
from data.chat import Chat
from forms.chat import ChatForm
from forms.change_password import PasswordForm
from forms.cabinet import CabinetForm
import datetime
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.job import JobForm
from forms.sell import SellForm
from flask_restful import abort, Api
import api as bapi

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'My_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 404)


@app.route('/success')
def success():
    return render_template('success.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/offers')
def off_index():
    session = db_session.create_session()
    return render_template('off_index.html', mas=session.query(Sell).all())


@app.route('/delete_offer/<int:id>', methods=['GET', 'POST'])
@login_required
def off_delete(id):
    db_sess = db_session.create_session()
    offer = db_sess.query(Sell).filter(Sell.id == id).filter(Sell.seller == current_user.id |
                                                             current_user.id == 1).first()
    if offer:
        db_sess.delete(offer)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/offers')


@app.route('/jobs')
def job_index():
    session = db_session.create_session()
    return render_template('job_index.html', mas=session.query(Jobs).all())


@app.route('/delete_job/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id).filter(Jobs.director == current_user.id |
                                                           current_user.id == 1).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/jobs')


@app.route('/create_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.director = current_user.id
        job.title = form.title.data
        job.description = form.description.data
        job.pay = form.pay.data
        job.start_date = datetime.datetime.now()
        f = request.files['file']
        if f:
            pictures = os.listdir('static/users_imgs/job_imgs')
            job.image = str(len(pictures)) + '.png'
            with open('static/users_imgs/job_imgs/' + str(len(pictures)) + '.png', 'wb') as file:
                file.write(f.read())
        current_user.jobs.append(job)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/jobs')
    return render_template('job.html', form=form)


@app.route('/create_offer', methods=['GET', 'POST'])
@login_required
def add_off():
    form = SellForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        sell = Sell()
        sell.seller = current_user.id
        sell.title = form.title.data
        sell.description = form.description.data
        sell.price = form.price.data
        sell.start_date = datetime.datetime.now()
        f = request.files['file']
        if f:
            pictures = os.listdir('static/users_imgs/off_imgs')
            sell.image = str(len(pictures)) + '.png'
            with open('static/users_imgs/off_imgs/' + str(len(pictures)) + '.png', 'wb') as file:
                file.write(f.read())
        current_user.sells.append(sell)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/offers')
    return render_template('offer.html', form=form)


@app.route('/job_view/<int:id>')
def view_job(id):
    session = db_session.create_session()
    return render_template('job_view.html', job=session.query(Jobs).filter(Jobs.id == id).first())


@app.route('/offer_view/<int:id>')
def view_off(id):
    session = db_session.create_session()
    return render_template('off_view.html', offer=session.query(Sell).filter(Sell.id == id).first())


@app.route('/job_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = JobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id).filter(Jobs.director == current_user.id |
                                                               current_user.id == 1).first()
        if job:
            form.title.data = job.title
            form.description.data = job.description
            form.pay.data = job.pay
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id, Jobs.director == current_user.id | current_user.id == 1).first()
        if job:
            job.title = form.title.data
            job.description = form.description.data
            job.pay = form.pay.data
            f = request.files['file']
            if f:
                pictures = os.listdir('static/users_imgs/job_imgs')
                job.image = str(len(pictures)) + '.png'
                with open('static/users_imgs/job_imgs/' + str(len(pictures)) + '.png', 'wb') as file:
                    file.write(f.read())
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('job.html', form=form)


@app.route('/offer_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_offer(id):
    form = SellForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        sell = db_sess.query(Sell).filter(Sell.id == id).filter(Sell.seller == current_user.id |
                                                                current_user.id == 1).first()
        if sell:
            form.title.data = sell.title
            form.description.data = sell.description
            form.price.data = sell.price
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        sell = db_sess.query(Sell).filter(Sell.id == id, Sell.seller == current_user.id | current_user.id == 1).first()
        if sell:
            sell.title = form.title.data
            sell.description = form.description.data
            sell.price = form.price.data
            f = request.files['file']
            if f:
                pictures = os.listdir('static/users_imgs/off_imgs')
                sell.image = str(len(pictures)) + '.png'
                with open('static/users_imgs/off_imgs/' + str(len(pictures)) + '.png', 'wb') as file:
                    file.write(f.read())
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('offer.html', form=form)


@app.route('/cabinet', methods=['GET', 'POST'])
@login_required
def cabinet():
    form = CabinetForm()
    if request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.address.data = current_user.address
        form.how_to_contact.data = current_user.how_to_contact
    elif form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        user.name = form.name.data
        user.surname = form.surname.data
        user.address = form.address.data
        user.how_to_contact = form.how_to_contact.data
        session.commit()
        user = session.query(User).filter(User.id == current_user.id).first()
        login_user(user)
        return redirect('/success')
    return render_template('cabinet.html', form=form)


@app.route('/cabinet/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        if user.check_password(form.old_password.data) and form.password.data == form.repeat_password.data:
            user.set_password(form.password.data)
            session.commit()
            return redirect('/success')
        return render_template('change_password.html', form=form, message='Неверный пароль')
    return render_template('change_password.html', form=form)


@app.route('/cabinet/<int:user_id>/offers')
def user_offers(user_id):
    session = db_session.create_session()
    return render_template('off_index.html', mas=session.query(Sell).filter(Sell.seller == user_id).all())


@app.route('/cabinet/<int:user_id>/jobs')
def user_jobs(user_id):
    session = db_session.create_session()
    return render_template('job_index.html', mas=session.query(Jobs).filter(Jobs.director == user_id).all())


@app.route('/cabinet/<int:user_id>')
def ones_cabinet(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    return render_template('ones_cabinet.html', user=user)


@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    session = db_session.create_session()
    chat = session.query(Chat).filter((Chat.usersids == f'{current_user.id},{user_id}') |
                                      (Chat.usersids == f'{user_id},{current_user.id}')).first()
    if not chat:
        chat = Chat()
        chat.usersids = str(current_user.id) + ',' + str(user_id)
        chat.text = ''
    user = session.query(User).filter(User.id == user_id).first()
    form = ChatForm()
    if form.validate_on_submit():
        if '@^&' in form.message.data or '$%$' in form.message.data:
            return render_template('chat.html', text=chat.text, form=form, user=
                                   {'name': user.name, 'surname': user.surname, 'id': user_id},
                                   message='сообщение содержит недопустимую комбинацию символов @^& или $%$')
        print(form.message.data)
        chat.text += f'@^&{current_user.id}$%$' + form.message.data + "@^&"
        print(chat.text)
        session.merge(chat)
        session.commit()
    return render_template('chat.html', text=chat.text, form=form, user=
                           {'name': user.name, 'surname': user.surname, 'id': user_id})


@app.route('/chats')
@login_required
def chats():
    session = db_session.create_session()
    chats = session.query(Chat).filter((Chat.usersids.like(f'%,{current_user.id}')) |
                                       (Chat.usersids.like(f'{current_user.id},%'))).all()
    mas = []
    for chat in chats:
        users = chat.usersids.split(',')
        del users[users.index(str(current_user.id))]
        user = session.query(User).filter(User.id == int(users[0])).first()
        mas.append((user.id, user.surname, user.name))
    return render_template('chats.html', mas=mas)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', form=form, message='Пароли не совпадают')
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message='Пользователь с данной почтой уже существует')
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.address = form.address.data
        user.set_password(form.password.data)
        user.create_date = datetime.datetime.now()
        user.how_to_contact = form.how_to_contact.data
        session.add(user)
        session.commit()
        session.close()
        user = session.query(User).filter(User.email == form.email.data).first()
        login_user(user)
        return redirect('/success')
    return render_template('register.html', form=form)


def main():
    db_session.global_init("db/main.db")
    app.register_blueprint(bapi.blueprint)
    # app.run('192.168.0.106', '5000')
    app.run('localhost', '5000')


app.jinja_env.globals.update(url_for=url_for)
app.jinja_env.globals.update(int=int)
app.jinja_env.globals.update(str=str)

if __name__ == '__main__':
    main()
