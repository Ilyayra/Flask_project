# Импортируем необходимые библиотеки и классы из отдельных файлов
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

# Инициализируем Flask и Api, а так же login_manager
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'My_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# Дополнтельные обработчики ошибок
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(405)
def not_found(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 404)


# Обработчик большинства успешных действий
@app.route('/success')
def success():
    return render_template('success.html')


# Обработчик для работы login_manager
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Главная страница, перенаправляет на секции объявлений или вакансий
@app.route('/')
def index():
    return render_template('index.html')


# Обработчик списка объявлений
@app.route('/offers')
def off_index():
    # Получаем из базы данных все объявления
    session = db_session.create_session()
    return render_template('off_index.html', mas=session.query(Sell).all())


# Функция удаления объявления
@app.route('/delete_offer/<int:id>', methods=['GET', 'POST'])
@login_required
def off_delete(id):
    # создаём сессию для работы с базой данных
    db_sess = db_session.create_session()
    # Ищем в базе данных объявление по заданным критериям
    offer = db_sess.query(Sell).filter(Sell.id == id).filter(Sell.seller == current_user.id |
                                                             current_user.id == 1).first()
    # Если необходимое объявление нашлось - удаляем его, иначе возвращаем ошибку
    if offer:
        db_sess.delete(offer)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/offers')


# Обработчик просмотра вакансий
@app.route('/jobs')
def job_index():
    # Получаем из базы данных все вакансии
    session = db_session.create_session()
    return render_template('job_index.html', mas=session.query(Jobs).all())


# Обработчик удаления вакансии
@app.route('/delete_job/<int:id>', methods=['GET', 'POST'])
@login_required
def job_delete(id):
    # Создаём сессию работы с базой данных и ищем подходящую вакансию
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == id).filter(Jobs.director == current_user.id |
                                                           current_user.id == 1).first()
    # Если нашли - удаляем
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/jobs')


# Обработчик создания вакансий
@app.route('/create_job', methods=['GET', 'POST'])
@login_required
def add_job():
    # Используем форму для создания вакансии
    form = JobForm()
    if form.validate_on_submit():
        # Если форма отправлена пользователем - создаём новую запись вакансии в базе данных
        db_sess = db_session.create_session()
        job = Jobs()
        job.director = current_user.id
        job.title = form.title.data
        job.description = form.description.data
        job.pay = form.pay.data
        job.start_date = datetime.datetime.now()
        # Проверяем, прикреплена ли картинка
        f = request.files['file']
        if f:
            # Если картинка прикреплена - загружаем её и сохраняем с присвоением порядкового номера
            pictures = os.listdir('static/users_imgs/job_imgs')
            # Сохраняем её номер в вакансии
            job.image = str(len(pictures)) + '.png'
            with open('static/users_imgs/job_imgs/' + str(len(pictures)) + '.png', 'wb') as file:
                file.write(f.read())
        # Добавляем вакансию и подтверждаем
        current_user.jobs.append(job)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/jobs')
    return render_template('job.html', form=form)


# Обработчик создания объявлений
@app.route('/create_offer', methods=['GET', 'POST'])
@login_required
def add_off():
    # Также инициализирует форму
    form = SellForm()
    if form.validate_on_submit():
        # Как и обработчик вакансий, создаёт запись объявления в базе данных
        db_sess = db_session.create_session()
        sell = Sell()
        sell.seller = current_user.id
        sell.title = form.title.data
        sell.description = form.description.data
        sell.price = form.price.data
        sell.start_date = datetime.datetime.now()
        f = request.files['file']
        if f:
            # Добавляет картинку к объявлению
            pictures = os.listdir('static/users_imgs/off_imgs')
            sell.image = str(len(pictures)) + '.png'
            with open('static/users_imgs/off_imgs/' + str(len(pictures)) + '.png', 'wb') as file:
                file.write(f.read())
        current_user.sells.append(sell)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/offers')
    return render_template('offer.html', form=form)


# Обработчик просмотра конкретной вакансии
@app.route('/job_view/<int:id>')
def view_job(id):
    # По id вакансии находим её в базе данных и отправляем в форму, она дальше сама справится
    session = db_session.create_session()
    return render_template('job_view.html', job=session.query(Jobs).filter(Jobs.id == id).first())


# Обработчик просмотра выбранной вакансии
@app.route('/offer_view/<int:id>')
def view_off(id):
    # Ищем объявление и возвращаем html страницу
    session = db_session.create_session()
    return render_template('off_view.html', offer=session.query(Sell).filter(Sell.id == id).first())


# Обработчик изменения вакансии
@app.route('/job_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    # Создаём уже знакомую форму вакансии
    form = JobForm()
    # Если мы только перешли на страницу, проверяем, мы ли создали запись, или являемся ли мы администратором
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id).filter(Jobs.director == current_user.id |
                                                               current_user.id == 1).first()
        if job:
            # Если проблем не возникло - загружаем данные из базы данных в форму
            form.title.data = job.title
            form.description.data = job.description
            form.pay.data = job.pay
        else:
            abort(404)
    # Если мы отправили изменённую форму, изменяем запись, не забыв проверить, имеем ли мы на это право
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


# обработчик изменения объявления
@app.route('/offer_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_offer(id):
    # Использую форму объявления отпраляем или получем данные
    form = SellForm()
    if request.method == "GET":
        # Проверяем, что мы можем изменить запись и что она существует
        db_sess = db_session.create_session()
        sell = db_sess.query(Sell).filter(Sell.id == id).filter(Sell.seller == current_user.id |
                                                                current_user.id == 1).first()
        if sell:
            form.title.data = sell.title
            form.description.data = sell.description
            form.price.data = sell.price
        else:
            abort(404)
    # При получении формы сохраняем изменения
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


# Личный кабинет пользователя
@app.route('/cabinet', methods=['GET', 'POST'])
@login_required
def cabinet():
    # Используем специальную форму для демонстрации и изменения  личных данных
    form = CabinetForm()
    # При отправке формы записываем в неё текущие данные о пользователе
    if request.method == 'GET':
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.address.data = current_user.address
        form.how_to_contact.data = current_user.how_to_contact
    # При получении формы записываем изменения в базу данных
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


# обработчик смены пароля
@app.route('/cabinet/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    # Используя специальную форму для смены пароля запрашиваем у пользователя его старый и новый пароли
    form = PasswordForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        # Если старый пароль введён верно, устанавливаем новый пароль
        if user.check_password(form.old_password.data) and form.password.data == form.repeat_password.data:
            user.set_password(form.password.data)
            session.commit()
            return redirect('/success')
        return render_template('change_password.html', form=form, message='Неверный пароль')
    return render_template('change_password.html', form=form)


# Просмотр объявлений пользователя
@app.route('/cabinet/<int:user_id>/offers')
def user_offers(user_id):
    # Получаем объявления по id пользователя и отправляем в форму
    session = db_session.create_session()
    return render_template('off_index.html', mas=session.query(Sell).filter(Sell.seller == user_id).all())


# обработчик функции просмотра вакансий выбранного пользователя
@app.route('/cabinet/<int:user_id>/jobs')
def user_jobs(user_id):
    # Получаем список вакансий пользователя и отправляем его на вывод
    session = db_session.create_session()
    return render_template('job_index.html', mas=session.query(Jobs).filter(Jobs.director == user_id).all())


# Просмотр кабинета любого пользователя
@app.route('/cabinet/<int:user_id>')
def ones_cabinet(user_id):
    # Получаем данные пользователя из базы данных и отправляем в html форму на обработку
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    return render_template('ones_cabinet.html', user=user)


# Обработчик чата с другим пользователем
@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    session = db_session.create_session()
    # Ищем чат между данными двумя пользователями
    chat = session.query(Chat).filter((Chat.usersids == f'{current_user.id},{user_id}') |
                                      (Chat.usersids == f'{user_id},{current_user.id}')).first()
    if not chat:
        # Если такового нет - создаём чат
        chat = Chat()
        chat.usersids = str(current_user.id) + ',' + str(user_id)
        chat.text = ''
    # Получаем пользователя - сочатовца, чтобы знать к кому разговор нести
    user = session.query(User).filter(User.id == user_id).first()
    form = ChatForm()
    # Использем форму для получения нового сообщения
    if form.validate_on_submit():
        # Проверяем содержатся ли в сообщении технические комбинации символов
        # Если имеются, просим их заменить
        if '@^&' in form.message.data or '$%$' in form.message.data:
            return render_template('chat.html', text=chat.text, form=form, user=
                                   {'name': user.name, 'surname': user.surname, 'id': user_id},
                                   message='сообщение содержит недопустимую комбинацию символов @^& или $%$')
        # Иначе сохраняем сообщение в базе данных
        chat.text += f'@^&{current_user.id}$%$' + form.message.data + "@^&"
        session.merge(chat)
        session.commit()
    return render_template('chat.html', text=chat.text, form=form, user=
                           {'name': user.name, 'surname': user.surname, 'id': user_id})


# Обработчик просмотра всех чатов пользователя
@app.route('/chats')
@login_required
def chats():
    session = db_session.create_session()
    # Ищем чаты с участием пользователя
    chats = session.query(Chat).filter((Chat.usersids.like(f'%,{current_user.id}')) |
                                       (Chat.usersids.like(f'{current_user.id},%'))).all()
    mas = []
    # Создаём спсок с данными пользователей - соучастников чатов
    for chat in chats:
        users = chat.usersids.split(',')
        del users[users.index(str(current_user.id))]
        user = session.query(User).filter(User.id == int(users[0])).first()
        mas.append((user.id, user.surname, user.name))
    return render_template('chats.html', mas=mas)


# Обработчик авторизации пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Используем форму, чтобы запросить данные авторизации
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # Если пользователь существует и пароль верен - авторизуем
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# Обработчик выхода из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Обработчик регистрации нового пользователя
@app.route('/register', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    # Формой запрашивем регистрационные данные
    if form.validate_on_submit():
        # Если пользователь отправил форму, проверяем корректность заполнения
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', form=form, message='Пароли не совпадают')
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message='Пользователь с данной почтой уже существует')
        # Если всё ОК, создаём нового пользователя
        user = User()
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.address = form.address.data
        user.set_password(form.password.data)
        user.create_date = datetime.datetime.now()
        user.how_to_contact = form.how_to_contact.data
        # И сохраняем его в базе данных
        session.add(user)
        session.commit()
        session.close()
        # Ну и сразу авторизуем
        user = session.query(User).filter(User.email == form.email.data).first()
        login_user(user)
        return redirect('/success')
    return render_template('register.html', form=form)


# функция инициализации приложения
def main():
    db_session.global_init("db/main.db")
    app.register_blueprint(bapi.blueprint)
    # app.run('192.168.0.106', '5000')
    app.run('localhost', '5000')


# Добавляем в обработчик необходимые функции
app.jinja_env.globals.update(url_for=url_for)
app.jinja_env.globals.update(int=int)
app.jinja_env.globals.update(str=str)

if __name__ == '__main__':
    main()
