import flask
from flask import jsonify, request
from data import db_session
from data.jobs import Jobs
from data.sell import Sell
from data.users import User
from datetime import datetime
from flask_login import login_required, current_user, LoginManager, login_user

blueprint = flask.Blueprint(
    'api',
    __name__,
    template_folder='templates'
)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('title', 'description', 'pay', 'id', 'director', 'start_date', 'image'))
                 for item in jobs]
        })


@blueprint.route('/api/job/<int:job_id>')
def get_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if job:
        return jsonify(
            {
                'job':
                    [job.to_dict(only=('title', 'description', 'pay', 'id', 'director', 'start_date', 'image'))]
            })
    return jsonify({'error': 'not found'})


@blueprint.route('/api/jobs', methods=['POST'])
@login_required
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'description', 'pay', 'start_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    job = Jobs()
    if 'id' in request.json:
        if db_sess.query(Jobs).filter(Jobs.id == request.json['id']):
            return jsonify({'error': 'Id already exists'})
        else:
            job.id = request.json['id']
    job.title = request.json['title']
    job.director = current_user.id
    job.description = request.json['description']
    job.pay = request.json['pay']
    job.start_date = datetime.fromisoformat(request.json['start_date'])
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter((Jobs.id == job_id),
                                     (Jobs.director == current_user.id | current_user.id == 1)).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
        return jsonify(
            {'success': 'OK'})
    return jsonify({'error': 'job not found or you do not have permission'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['POST'])
@login_required
def redact_job(job_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'description', 'pay', 'start_date']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter((Jobs.id == job_id),
                                     (Jobs.director == current_user.id | current_user.id == 1)).first()
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


@blueprint.route('/api/offers')
def get_offers():
    db_sess = db_session.create_session()
    sells = db_sess.query(Sell).all()
    return jsonify(
        {
            'offers':
                [item.to_dict(only=('title', 'description', 'price', 'id', 'seller', 'start_date', 'image'))
                 for item in sells]
        })


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


@blueprint.route('/api/offers', methods=['POST'])
@login_required
def create_offer():
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


@blueprint.route('/api/login/<email>&<password>')
def login(email, password):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and user.check_password(password):
        login_user(user)
        return jsonify({'success': 'user logged in'})
    return jsonify({'error': 'user does not exist'})


@blueprint.route('/api/register/<email>&<password>')
def register(email, password):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user:
        return jsonify({'error': 'user already exist'})
    user = User()
    user.email = email
    user.set_password(password)
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'registration comlpete'})
