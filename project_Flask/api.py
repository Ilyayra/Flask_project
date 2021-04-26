# Импортируем необходимые библиотеки
import flask
from flask import jsonify, request
from data import db_session
from data.jobs import Jobs
from data.sell import Sell
from data.users import User
from datetime import datetime
from flask_login import login_required, current_user, LoginManager, login_user

# Создаём blueprint
blueprint = flask.Blueprint(
    'api',
    __name__,
    template_folder='templates'
)
# Инициализируем LoginManager()
login_manager = LoginManager()


# Обработчик загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# Api получения всех вакансий
@blueprint.route('/api/jobs')
def get_jobs():
    # Создаём сессию с базой данных и получаем все вакансии
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    # Отправляем JSON со всеми вакансиями
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('title', 'description', 'pay', 'id', 'director', 'start_date', 'image'))
                 for item in jobs]
        })


# Обработчик получения одной вакансии по id
@blueprint.route('/api/job/<int:job_id>')
def get_job(job_id):
    # Ищем в БД вакансию по id
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        # Если такая вакансия имеется, возвращаем, иначе возвращаем JSON с описанием ошибки
        return jsonify(
            {
                'job':
                    [job.to_dict(only=('title', 'description', 'pay', 'id', 'director', 'start_date', 'image'))]
            })
    return jsonify({'error': 'not found'})


# Обработчик создания вакансии через Api
@blueprint.route('/api/jobs', methods=['POST'])
@login_required
def create_job():
    # Если в запросе - правильный JSON, создаём вакансию
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'description', 'pay', 'start_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    job = Jobs()
    # Если в JSON передан id, то проверяем, не занят ли этот id
    if 'id' in request.json:
        if db_sess.query(Jobs).filter(Jobs.id == request.json['id']):
            return jsonify({'error': 'Id already exists'})
        else:
            job.id = request.json['id']
    job.title = request.json['title']
    job.director = current_user.id
    job.description = request.json['description']
    job.pay = request.json['pay']
    job.start_date = datetime.now()
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# Api Удаление вакансии
@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    # Находим запись, которую мы можем удалить с данным id
    job = db_sess.query(Jobs).filter((Jobs.id == job_id),
                                     (Jobs.director == current_user.id | current_user.id == 1)).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
        return jsonify(
            {'success': 'OK'})
    return jsonify({'error': 'job not found or you do not have permission'})


# Обработчик редактирования записи
@blueprint.route('/api/jobs/<int:job_id>', methods=['POST'])
@login_required
def redact_job(job_id):
    # В целом мало отличается от создания записи
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'description', 'pay', 'start_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter((Jobs.id == job_id),
                                     (Jobs.director == current_user.id | current_user.id == 1)).first()
    # Только если запись есть, то изменяем, если нет, то создаём
    if not job:
        job = Jobs()
        job.id = job_id
    job.title = request.json['title']
    job.director = current_user.id
    job.description = request.json['description']
    job.pay = request.json['pay']
    job.start_date = datetime.fromisoformat(request.json['start_date'])
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# Api получение всех объявлений
@blueprint.route('/api/offers')
def get_offers():
    # Получаем из БД все объявления и отправляем в виде JSON
    db_sess = db_session.create_session()
    sells = db_sess.query(Sell).all()
    return jsonify(
        {
            'offers':
                [item.to_dict(only=('title', 'description', 'price', 'id', 'seller', 'start_date', 'image'))
                 for item in sells]
        })


# Api получения выбранного объявления
@blueprint.route('/api/offer/<int:sell_id>')
def get_offer(sell_id):
    db_sess = db_session.create_session()
    sell = db_sess.query(Sell).filter(Sell.id == sell_id).first()
    if sell:
        return jsonify(
            {
                'offers':
                    [sell.to_dict(only=('title', 'description', 'price', 'id', 'seller', 'start_date', 'image'))]
            })
    return jsonify({'error': 'not found'})


# Api создания объявления
@blueprint.route('/api/offers', methods=['POST'])
@login_required
def create_offer():
    # Схоже с созданием вакансии, но поэтому легко ошибиться в их атрибутах
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'description', 'price', 'start_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    sell = Sell()
    if 'id' in request.json:
        if db_sess.query(Sell).filter(Sell.id == request.json['id']):
            return jsonify({'error': 'Id already exists'})
        else:
            sell.id = request.json['id']
    sell.title = request.json['title']
    sell.seller = current_user.id
    sell.description = request.json['description']
    sell.price = request.json['price']
    sell.start_date = datetime.fromisoformat(request.json['start_date'])
    db_sess.add(sell)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# Api удаления объявления
@blueprint.route('/api/offers/<int:offer_id>', methods=['DELETE'])
@login_required
def delete_offer(offer_id):
    db_sess = db_session.create_session()
    sell = db_sess.query(Sell).filter((Sell.id == offer_id),
                                      (Sell.seller == current_user.id | current_user.id == 1)).first()
    if sell:
        db_sess.delete(sell)
        db_sess.commit()
        return jsonify(
            {'success': 'OK'})
    return jsonify({'error': 'offer not found or you do not have permission'})


# Изменение объявления
@blueprint.route('/api/offers/<int:offer_id>', methods=['POST'])
@login_required
def redact_offer(offer_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'description', 'price', 'start_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    offer = db_sess.query(Sell).filter((Sell.id == offer_id),
                                       (Sell.seller == current_user.id | current_user.id == 1)).first()
    if not offer:
        offer = Sell()
        offer.id = offer_id
    offer.title = request.json['title']
    offer.seller = current_user.id
    offer.description = request.json['description']
    offer.price = request.json['price']
    offer.start_date = datetime.fromisoformat(request.json['start_date'])
    db_sess.add(offer)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# Api авторизация через адресную сторку
@blueprint.route('/api/login/<email>&<password>')
def login(email, password):
    # Ищем нужного пользователя и отчитываемся по результату
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': 'user logged in'})
    return jsonify({'error': 'user does not exist'})


# Api регистрация нового пользователя
@blueprint.route('/api/register/<email>&<password>')
def register(email, password):
    db_sess = db_session.create_session()
    # Проверяем существует ли уже данный пользователь
    user = db_sess.query(User).filter(User.email == email).first()
    if user:
        return jsonify({'error': 'user already exist'})
    user = User()
    user.email = email
    user.set_password(password)
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'registration comlpete'})
