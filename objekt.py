from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort
)

from zechlin import config
from zechlin.auth import login_required
from zechlin.datenbank import get_database_connection, close_database_cursor

bp = Blueprint('objekt', __name__)

"""
    Einheitliche Variablen:

        webseite_titel:     Titel des Browser-Tabs
        aktives_menu:       Tag, der zum Markieren des aktuellen Menüpunktes verwendet wird
"""


@bp.route('/gattung/<gattung_id>')
@login_required
def gattung(gattung_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Gattung'

    Dies beinhaltet mehrere Verweise auf zugehörige Entitäten und Informationen

    :param: gattung_id: ID der Entität Gattung
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Gattung'
    aktives_menu = 'werke'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM gattung WHERE gattung_id = ?;',
        (gattung_id,)
    )
    # Gattung auf Basis der Gattung-ID
    gattung = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * FROM untergattung WHERE fk_gattung_id = ?',
        (gattung_id,)
    )
    # Untergeordnete Untergattungen der Gattung
    untergattungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'LEFT JOIN gattung ON werk.fk_gattung_id = gattung.gattung_id '
        'WHERE gattung_id = ?',
        (gattung_id,)
    )
    # Werke dieser Gattung auf Basis Gattung-ID
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('objekt/gattung.html', title=webseite_titel, aktives_menu=aktives_menu, gattung=gattung, untergattungen=untergattungen, werke=werke, config=config)


@bp.route('/untergattung/<untergattung_id>')
@login_required
def untergattung(untergattung_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Untergattung'

    Dies beinhaltet mehrere Verweise auf zugehörige Entitäten und Informationen

    :param: untergattung_id: ID der Entität Untergattung
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Untergattung'
    aktives_menu = 'werke'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * '
        'FROM untergattung '
        'LEFT JOIN gattung ON untergattung.fk_gattung_id = gattung.gattung_id '
        'WHERE untergattung_id = ?;',
        (untergattung_id,)
    )
    # Untergattung auf Basis der Untergattung-ID (+ übergeordnete Gattung)
    untergattung = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * FROM detailgattung WHERE fk_untergattung_id = ?',
        (untergattung_id,)
    )
    # Untergeordnete Detailgattungen
    detailgattungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'LEFT JOIN untergattung ON werk.fk_untergattung_id = untergattung.untergattung_id '
        'WHERE untergattung_id = ?',
        (untergattung_id,)
    )
    # Werke dieser Untergattung auf Basis von Untergattung-ID
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('objekt/untergattung.html', title=webseite_titel, aktives_menu=aktives_menu, untergattung=untergattung, detailgattungen=detailgattungen, werke=werke, config=config)


@bp.route('/detailgattung/<detailgattung_id>')
@login_required
def detailgattung(detailgattung_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Detailgattung'

    Dies beinhaltet mehrere Verweise auf zugehörige Entitäten und Informationen

    :param: detailgattung_id: ID der Entität Gattung
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Detailgattung'
    aktives_menu = 'werke'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * '
        'FROM detailgattung '
        'LEFT JOIN untergattung ON detailgattung.fk_untergattung_id = untergattung.untergattung_id '
        'LEFT JOIN gattung ON untergattung.fk_gattung_id = gattung.gattung_id '
        'WHERE detailgattung_id = ?;',
        (detailgattung_id,)
    )
    # Detailgattung auf Basis von Detailgattung-ID (+ übergeordnete Untergattung und Gattung)
    detailgattung = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'LEFT JOIN detailgattung ON werk.fk_detailgattung_id = detailgattung.detailgattung_id '
        'WHERE detailgattung_id = ?',
        (detailgattung_id,)
    )
    # Werke dieser Detailgattung auf Basis von Detailgattung-ID
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('objekt/detailgattung.html', title=webseite_titel, aktives_menu=aktives_menu, detailgattung=detailgattung, werke=werke, config=config)


@bp.route('/ort/<ort_id>')
@login_required
def ort(ort_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Ort'

    Dies beinhaltet mehrere Verweise auf zugehörige Entitäten und Informationen

    :param: ort_id: ID der Entität Ort
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Ort'
    aktives_menu = 'nutzungen'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM ort WHERE ort_id = ?',
        (ort_id,)
    )
    # Ort auf Basis der Ort-ID
    ort = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM nutzung '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'WHERE fk_ort_id = ?',
        (ort_id,)
    )
    # Nutzungen, die an diesem Ort stattgefunden haben (+ gespieltes Werk)
    nutzungen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('objekt/ort.html', title=webseite_titel, aktives_menu=aktives_menu, ort=ort, nutzungen=nutzungen, config=config)
@bp.route('/verlag/<verlag_id>')
@login_required
def verlag(verlag_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Verlag'

    Dies beinhaltet mehrere Verweise auf zugehörige Entitäten und Informationen

    :param: verlag_id: ID der Entität Verlag
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Verlag'
    aktives_menu = 'werke'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM verlag WHERE verlag_id = ?',
        (verlag_id,)
    )
    # Verlag auf Basis der Verlag-ID
    verlag = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'WHERE fk_verlag_id_aktuell = ?',
        (verlag_id,)
    )
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('objekt/verlag.html', title=webseite_titel, aktives_menu=aktives_menu, werke=werke, verlag=verlag, config=config)
@bp.route('/werkart/<werkart_id>')
@login_required
def werkart(werkart_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Werkart'

    Dies beinhaltet den Verweis auf zugeordnete Werke

    :param: werart_id: ID der Entität Werkart
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Werkart'
    aktives_menu = 'werke'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM werkart WHERE werkart_id = ?',
        (werkart_id,)
    )
    # Verlag auf Basis der Verlag-ID
    werkart = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'WHERE fk_werkart_id = ?',
        (werkart_id,)
    )
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('objekt/werkart.html', title=webseite_titel, aktives_menu=aktives_menu, werke=werke, werkart=werkart, config=config)
