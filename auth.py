import functools
import re
from datetime import datetime, timedelta

from flask import (
    Blueprint, redirect, g, url_for, render_template, session, request
)

from zechlin import credentials
from zechlin.datenbank import get_database_connection, close_database_cursor

bp = Blueprint('auth', __name__)


@bp.route('/access', methods=['GET', 'POST'])
def access():
    user = _get_user()

    if user['user_auth_attempts'] >= 10:
        return redirect(url_for('auth.blocked'))

    if request.method == 'GET':
        return render_template('auth/access.html')

    post_params = request.form
    if 'code' not in post_params:
        response = {
            'status': False,
            'message': 'In Ihrer Nachricht konnte kein Code gefunden werden, bitte versuchen Sie es erneut.'
        }
        return render_template('auth/access.html', response=response)

    code = re.sub(r'[^a-zA-Z0-9]', '', post_params['code'])

    if post_params['code'] != code or code != credentials.config['access']['password']:
        user['user_auth_attempts'] += 1

        _update_user(user)

        response = {
            'status': False,
            'message': 'Der eingegebene Code ist falsch.',
            'input': post_params['code']
        }
        return render_template('auth/access.html', response=response)

    user['user_access'] = True
    user['user_auth_attempts'] = 0
    _update_user(user)

    return redirect(url_for('index.index'))


def _get_user():
    remote_addr = request.remote_addr
    proxy_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    if remote_addr != proxy_address and proxy_address is not None:
        ip_address = proxy_address
    else:
        ip_address = remote_addr

    database_connection = get_database_connection()
    database_cursor = database_connection.cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM user WHERE user_ip_address = ?',
        (ip_address,)
    )
    user_from_db = database_cursor.fetchone()

    if user_from_db:
        user_from_db['user_access'] = user_from_db['user_access'] == 1
        return user_from_db

    database_cursor.execute(
        'INSERT INTO user '
        '(user_access, user_auth_attempts, user_blocked_until, user_blocked_count, user_ip_address) '
        'VALUES (FALSE, 0, NULL, 0, ?)',
        (ip_address,)
    )
    database_connection.commit()
    close_database_cursor()
    return database_cursor.execute('SELECT * FROM user WHERE user_id = ?', (database_cursor.lastrowid,))


def _update_user(user):
    session['user'] = user

    database_connection = get_database_connection()
    database_cursor = database_connection.cursor(dictionary=True)

    database_cursor.execute(
        'UPDATE user SET '
        'user_access = ?, '
        'user_auth_attempts = ?, '
        'user_blocked_until = ?, '
        'user_blocked_count = ?, '
        'user_ip_address = ? '
        'WHERE user_id = ?',
        (user['user_access'], user['user_auth_attempts'], user['user_blocked_until'], user['user_blocked_count'], user['user_ip_address'], user['user_id'])
    )
    database_connection.commit()

    database_cursor.execute('SELECT * FROM user WHERE user_id = ?', (user['user_id'],))
    close_database_cursor()
    return database_cursor.fetchone()


@bp.route('/blocked', methods=['GET'])
def blocked():
    user = _get_user()

    if user is None:
        return redirect(url_for('auth.access'))

    if user['user_auth_attempts'] >= 10:
        user['user_blocked_count'] += 1
        user['user_auth_attempts'] = 0

        block_time = 2 ** user['user_blocked_count']
        user['user_blocked_until'] = datetime.now() + timedelta(hours=block_time)
        _update_user(user)

    if user['user_blocked_until'] is None:
        return redirect(url_for('auth.access'))

    if user['user_blocked_until'] < datetime.now():
        user['user_blocked_until'] = None
        _update_user(user)
        return redirect(url_for('auth.access'))


    info = {
        'duration': 2 ** user['user_blocked_count']
    }

    return render_template('auth/blocked.html', info=info)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user = _get_user()

        if user is None:
            return redirect(url_for('auth.access'))
        elif user['user_blocked_until']:
            return redirect(url_for('auth.blocked'))
        elif not user['user_access']:
            return redirect(url_for('auth.access'))
        else:
            return view(**kwargs)

    return wrapped_view
