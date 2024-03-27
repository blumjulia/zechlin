from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from zechlin import config
from zechlin.auth import login_required
from zechlin.datenbank import get_database_connection, close_database_cursor

bp = Blueprint('nutzung', __name__)

"""
    Einheitliche Variablen:

        webseite_titel:     Titel des Browser-Tabs
        aktives_menu:       Tag, der zum Markieren des aktuellen Menüpunktes verwendet wird
"""


@bp.route('/nutzung/<nutzung_id>')
@login_required
def nutzung(nutzung_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Nutzung'

    Dies beinhaltet mehrere Verweise auf zugehörige Entitäten und Informationen

    :param: nutzung_id: ID der Entität Nutzung
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Werk-Nutzungen'
    aktives_menu = 'nutzungen'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * '
        'FROM nutzung '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'LEFT JOIN gattung ON werk.fk_gattung_id = gattung.gattung_id '
        'LEFT JOIN untergattung ON werk.fk_untergattung_id = untergattung.untergattung_id '
        'LEFT JOIN detailgattung ON werk.fk_detailgattung_id = detailgattung.detailgattung_id '
        'LEFT JOIN ort ON nutzung.fk_ort_id = ort.ort_id '
        'WHERE nutzung_id = ?',
        (nutzung_id,)
    )
    # Nutzung auf Basis der Nutzung-ID (+ Werk, Gattung, Untergattung, Detailgattung und Ort)
    nutzung = database_cursor.fetchone()

    besetzung = None

    # Nur wenn das Werk bekannt ist, kann es auch eine Besetzung geben
    if nutzung['fk_werk_id'] is not None:
        database_cursor.execute(
            'SELECT * '
            'FROM rism '
            'LEFT JOIN rism_kategorie ON rism.fk_rism_kategorie_id = rism_kategorie.rism_kategorie_id '
            'LEFT JOIN werk_rism ON rism.rism_id = werk_rism.fk_rism_id '
            'WHERE fk_werk_id = ?',
            (nutzung['fk_werk_id'],)
        )
        # RISM Besetzung auf Basis der Werk-ID
        besetzung = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * '
        'FROM quelle_nutzung '
        'WHERE fk_nutzung_id = ?',
        (nutzung_id,)
    )
    # Da mehrere Quellen zu einer Nutzung möglich -> nicht nur als Left Join
    quellen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('nutzung/nutzung.html', title=webseite_titel, aktives_menu=aktives_menu, nutzung=nutzung, config=config, besetzung=besetzung, quellen=quellen)


@bp.route('/nutzung/verzeichnis')
@login_required
def verzeichnis() -> str:
    """
    Erstellt und rendert das Nutzungsverzeichnis

    Dies beinhaltet eine erweiterte Suche nach Nutzungen
    Aber auch die 20 neuesten Nutzungen sowie 20 am häufigsten genutzten Werke

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Nutzungsverzeichnis'
    aktives_menu = 'nutzungen'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT MIN(nutzung_datum_jahr) AS min_jahr, MAX(nutzung_datum_jahr) AS max_jahr '
        'FROM nutzung '
    )
    # niedrigstes und höchstes Nutzungsjahr (für erweiterte Suche)
    nutzung_jahr_min_max = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT nutzung_art '
        'FROM nutzung '
        'GROUP BY nutzung_art'
    )
    # Nutzungsarten für erweiterte Suche
    nutzungsarten = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * FROM ort;'
    )
    # Orte für erweiterte Suche
    orte = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT nutzung.*, werk.werk_titel '
        'FROM nutzung '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'WHERE fk_werk_id IS NOT NULL '
        'ORDER BY nutzung_Datum_jahr DESC, nutzung_datum_monat DESC, nutzung_datum_tag DESC '
        'LIMIT 20'
    )
    # Letzten 20 Nutzungen (zeitlich)
    letzte_nutzungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT COUNT(nutzung_id) AS anzahl_nutzungen, nutzung.*, werk.werk_titel '
        'FROM nutzung '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'WHERE werk_id IS NOT NULL '
        'GROUP BY fk_werk_id '
        'ORDER BY anzahl_nutzungen DESC '
        'LIMIT 20'
    )
    # 20 häufigsten Nutzungen (Werke)
    meiste_nutzungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT werk_titel FROM werk'
    )
    # Alle Werke (für erweiterte Suche)
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('nutzung/verzeichnis.html', title=webseite_titel, aktives_menu=aktives_menu, nutzung_jahr_min_max=nutzung_jahr_min_max, nutzungsarten=nutzungsarten, orte=orte, letzte_nutzungen=letzte_nutzungen, meiste_nutzungen=meiste_nutzungen, werke=werke)
