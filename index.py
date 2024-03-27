import flask.wrappers
from flask import (
    Blueprint, redirect, render_template, url_for, abort
)

from zechlin import config
from zechlin.auth import login_required

bp = Blueprint('index', __name__)

"""
    Einheitliche Variablen:

        webseite_titel:     Titel des Browser-Tabs
        aktives_menu:       Tag, der zum Markieren des aktuellen Menüpunktes verwendet wird
"""


@bp.route('/')
@login_required
def index() -> str:
    """
    Startseite mit Schnellsuche

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Start'
    aktives_menu = 'start'

    return render_template('start/index.html', title=webseite_titel, aktives_menu=aktives_menu)


@bp.route('/pid/<pid>')
@login_required
def pid(pid) -> flask.wrappers.Response:
    """
    Weiterleitung zur Entität auf Basis der PID

    PID Aufbau [projekt][separator][objekt][separator][ID]
    z. B. zechlin_werk_2

    :param pid: Eindeutige persistente ID
    :return: gerenderte Webseite
    """

    komponenten = pid.split(config.pid['separator'])

    if not len(komponenten) == 3:
        abort(400, 'Die angegebene PID ist ungültig')

    if komponenten[1] not in config.pid['objekt']:
        abort(400, f'Der angegebene Objekttyp "{komponenten[1]}" der PID existiert nicht.')

    if komponenten[1] == config.pid['objekt']['werk']:
        return redirect(url_for('werk.werk', werk_id=komponenten[2]))
    elif komponenten[1] == config.pid['objekt']['werkart']:
        return redirect(url_for('objekt.werkart', werkart_id=komponenten[2]))
    elif komponenten[1] == config.pid['objekt']['verlag']:
        return redirect(url_for('objekt.verlag', verlag_id=komponenten[2]))
    elif komponenten[1] == config.pid['objekt']['ort']:
        return redirect(url_for('objekt.ort', ort_id=komponenten[2]))
    elif komponenten[1] == config.pid['objekt']['nutzung']:
        return redirect(url_for('nutzung.nutzung', nutzung_id=komponenten[2]))
    elif komponenten[1] == config.pid['objekt']['gattung']:
        return redirect(url_for('objekt.gattung', gattung_id=komponenten[2]))
    elif komponenten[1] == config.pid['objekt']['untergattung']:
        return redirect(url_for('objekt.untergattung', untergattung_id=komponenten[2]))
    elif komponenten[1] == config.pid['objekt']['detailgattung']:
        return redirect(url_for('objekt.detailgattung', detailgattung_id=komponenten[2]))
