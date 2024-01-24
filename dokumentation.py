from flask import (
    Blueprint, render_template
)

from zechlin.datenbank import get_database_connection, close_database_cursor

bp = Blueprint('dokumentation', __name__)

"""
    Einheitliche Variablen:
    
        webseite_titel:     Titel des Browser-Tabs
        aktives_menu:       Tag, der zum Markieren des aktuellen Menüpunktes verwendet wird
"""


@bp.route('/dokumentation/datenbank')
def datenbank_struktur() -> str:
    """
    Erstellt und rendert die Dokumentation der Datenbank

    Diese beinhaltet mehrere Diagramme zur Veranschaulichung der Struktur der MariaDB Datenbank

    :return: gerenderte Webseite
    """

    webseite_titel = 'Datenbank-Struktur'
    aktives_menu = 'dokumentation'

    return render_template('dokumentation/struktur.html', title=webseite_titel, aktives_menu=aktives_menu)


@bp.route('/dokumentation/werk')
def werk() -> str:
    """
    Erstellt und rendert die Dokumentation der Datenbank-Tabelle Werk

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Werk'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM werk;'
    )
    # Alle Werke
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/werk.html', title=webseite_titel, aktives_menu=aktives_menu, werke=werke)


@bp.route('/dokumentation/nutzung')
def nutzung() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle Nutzung

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Nutzung'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM nutzung;'
    )
    # Alle Nutzungen
    nutzungen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/nutzung.html', title=webseite_titel, aktives_menu=aktives_menu, nutzungen=nutzungen)


@bp.route('/dokumentation/quelle-nutzung')
def quelle_nutzung() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle quelle-nutzung

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Nutzungsquellen'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM quelle_nutzung;'
    )
    # Alle Quellen
    quellen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/nutzung_quelle.html', title=webseite_titel, aktives_menu=aktives_menu, quellen=quellen)


@bp.route('/dokumentation/verlag')
def verlag() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle verlag

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """
    
    webseite_titel = 'Dokumentation: Verlag'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM verlag;'
    )
    # Alle Verlage
    verlage = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/verlag.html', title=webseite_titel, aktives_menu=aktives_menu, verlage=verlage)


@bp.route('/dokumentation/ort')
def ort() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle ort

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Ort'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM ort;'
    )
    # Alle Orte
    orte = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/ort.html', title=webseite_titel, aktives_menu=aktives_menu, orte=orte)


@bp.route('/dokumentation/gattung')
def gattung() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle gattung

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Gattung'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM gattung;'
    )
    # Alle Gattungen
    gattungen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/gattung.html', title=webseite_titel, aktives_menu=aktives_menu, gattungen=gattungen)


@bp.route('/dokumentation/untergattung')
def untergattung() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle untergattung

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Untergattung'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM untergattung;'
    )
    # Alle Untergattungen
    untergattungen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/untergattung.html', title=webseite_titel, aktives_menu=aktives_menu, untergattungen=untergattungen)


@bp.route('/dokumentation/detailgattung')
def detailgattung() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle detailgattung

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Detailgattung'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM detailgattung;'
    )
    # Alle Detailgattungen
    detailgattungen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/detailgattung.html', title=webseite_titel, aktives_menu=aktives_menu, detailgattungen=detailgattungen)


@bp.route('/dokumentation/werkart')
def werkart() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle werkart

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Werkart'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM werkart;'
    )
    # Alle Werkarten
    werkarten = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/werkart.html', title=webseite_titel, aktives_menu=aktives_menu, werkarten=werkarten)


@bp.route('/dokumentation/ausgabe')
def ausgabe() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle ausgabe

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: Ausgabe'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM ausgabe;'
    )
    # Alle Ausgaben
    ausgaben = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/ausgabe.html', title=webseite_titel, aktives_menu=aktives_menu, ausgaben=ausgaben)


@bp.route('/dokumentation/rism')
def rism() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle rism

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: RISM Besetzung'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM rism;'
    )
    # Alle RISM Besetzungen
    rism_besetzungen = database_cursor.fetchall()

    close_database_cursor()

    # Übergibt Informationen an das Template und rendert die Daten
    return render_template('dokumentation/rism.html', title=webseite_titel, aktives_menu=aktives_menu, rism_besetzungen=rism_besetzungen)


@bp.route('/dokumentation/rism-kategorie')
def rism_kategorie() -> str:
    """
    Erstellt und rendert die Dokumentationsseite zur Datenbank-Tabelle rism_kategorie

    Diese Seite beinhaltet neben allen Datenbank-Einträgen auch ein ER-Diagramm (Entity Relationship) und ein Datenmodell

    :return: gerenderte Webseite
    """

    webseite_titel = 'Dokumentation: RISM Kategorie'
    aktives_menu = 'dokumentation'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM rism_kategorie;'
    )
    # Alle RISM Kategorien
    rism_kategorien = database_cursor.fetchall()

    close_database_cursor()
    return render_template('dokumentation/rism_kategorie.html', title=webseite_titel, aktives_menu=aktives_menu, rism_kategorien=rism_kategorien)
