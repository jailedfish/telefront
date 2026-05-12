from datetime import timedelta
import logging
from types import NoneType

from tokenman import Tokenman
import requests
from flask import Flask, request, redirect, make_response
from jinja2 import Environment, FileSystemLoader
import redis
import os
from hashlib import sha3_256
from models import *
from datetime import datetime
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs.log')
    ]
)
app_token = Tokenman()
app = Flask('flask', static_folder='static')
redis = redis.from_url(os.getenv('REDIS_URL'))
t_env = Environment(loader=FileSystemLoader('./templates'))


@app.errorhandler(404)
def handle_404(handler):
    return render_error(status=404,
                              comment='Страница не найдена, если вы были перенаправлены сюда автоматически, '
                                      'то мне очень жаль')

@app.errorhandler(500)
def handle_404(handler):
    return render_error(status=500,
                              comment='На сервере обнаружена критическая ошибка, обработка запроса невозможна. Свяжитесь с администратором: <a href="https://t.me/herr_jailedfish">@jailedfish</a>')


def check_token():
    try:
        token = request.cookies.get('token', '')
        user_id = int(request.cookies.get('uid', 1))
    except ValueError as e:
        logging.warning('Incorrect cookies type', exc_info=e)
        return False
    token_excepted = (redis.getex(f'token_{user_id}', timedelta(days=7)))
    if isinstance(token_excepted, NoneType):
        return False

    return token == token_excepted.decode()


def render_error(status: int | None = 500, comment: str | None = 'Ошибка сервера'):
    return t_env.get_template('error.html').render(status=status, comment=comment), status


@app.get('/')
def get_index():
    try:
        user_id = int(request.cookies.get('uid', 1))
    except ValueError:
        return render_error(400, 'Ошибка файлов cookie, попробуйте очистить кеш браузера')

    if not (check_token()):
        return redirect('/register')

    user = session.get(User, user_id)

    return t_env.get_template('index.html').render(user_name=user.name)

@app.get('/register')
def get_register():
    return t_env.get_template('register.html').render()

@app.post('/register')
def register():
    try:
        name = request.form.get('name')
        tg_id = int(request.form.get('tg_id', ''))
    except ValueError as e:
        return render_error(400, 'Ошибка запроса, разработчику очень жаль')
    users = session.query(User).where(User.name == name or User.tg_id == tg_id).all()
    print(users)
    if users:
        return render_error(409, 'Пользователь с таким именем или id уже существует')
    user = User(name=name, tg_id=tg_id)
    session.add(user)
    try:
        session.commit()
    except:
        session.rollback()

    token = sha3_256((name + datetime.now().isoformat()).encode()).hexdigest()
    redis.set(f'token_{tg_id}_authorising', token)
    res = make_response(redirect('/login'))
    res.set_cookie('token', token, 60*5)
    return res

@app.get('/2fa')
def get_2fa():
    try:
        tg_id = int(request.args.get('tg_id', ''))
        error = 'True' == request.args.get('wrong_code', 'False')
    except ValueError as e:
        print(e)
        return render_error(400, 'Ошибка запроса, разработчику очень жаль')
    user = session.query(User).filter(User.tg_id == tg_id).one_or_none()
    logging.error(session.query(User).all())
    logging.error(tg_id == 6873126006)
    if user is None:
        return render_error(404, 'пользователь с таким telegram id не найден, зарегистрируйтесь и попробуйте снова')
    if not error:
        data = requests.post(url='http://host.docker.internal:8180/api/message',
                             headers={"Authorization": f"Bearer {app_token.get_token()}", 'User-id': '1'},
                             json={'user_id': tg_id}).json()

        if not data.get('success', False):
            if data.get('error_subcode') == 'NoUserFound':

                return render_error(404, 'Пользователь с таким telegram id не найден, проверьте правильность ввода')
            if data.get('error_subcode', '') == 'WrongToken':
                app_token.renew_token()
                data = requests.post(url='http://host.docker.internal:8180/api/message',
                                     headers={"Authorization": f"Bearer {app_token.get_token()}", 'User-id': '1'},
                                     json={'user_id': tg_id}).json()

        print(data)
        if data.get('error_subcode', '') != 'MsgAlreadySent':

            redis.set(f'code_{tg_id}', data.get('data', {}).get('code', ''), timedelta(minutes=5))

    resp = t_env.get_template('2fa.html').render(wrong_code=error)
    return resp

@app.get('/login')
def get_login():
    return t_env.get_template('login.html').render()

@app.post('/login')
def login():
    try:
        full_code = int(request.form.get('code'))
        tg_id = int(request.form.get('tg_id', ''))
    except ValueError as e:
        return render_error(400, 'Ошибка запроса, разработчику очень жаль')

    code = redis.get(f'code_{tg_id}')
    if isinstance(code, None):
        try:
            code = int(code.decode())
        except:
            code = -1
    print(f'code: {code}, i_code: {full_code}')
    if code != full_code:
        return redirect(f'/2fa?wrong_code=True&tg_id={tg_id}')
    user = session.query(User).filter(User.tg_id == tg_id).one()
    token = sha3_256((user.name+datetime.now().isoformat()).encode()).hexdigest()
    redis.set(f'token_{user.id}', token, timedelta(days=7))
    resp = make_response(redirect('/'))
    resp.set_cookie('token', token)
    resp.set_cookie('uid', str(user.id))
    return resp

@app.get('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('token', '', 0)
    resp.set_cookie('uid', '', 0)
    return resp

app.run(host='0.0.0.0', port=8080, debug=False)