from flask import (
    Blueprint, render_template
)

from zechlin.datenbank import get_database_connection, close_database_cursor
from zechlin import config

bp = Blueprint('werk', __name__)

"""
    Einheitliche Variablen:

        webseite_titel:     Titel des Browser-Tabs
        aktives_menu:       Tag, der zum Markieren des aktuellen Menüpunktes verwendet wird
"""


@bp.route('/werk/<werk_id>')
def werk(werk_id) -> str:
    """
    Erstellt und rendert die Übersichtsseite der Entität 'Werk'

    Dies beinhaltet mehrere Verweise auf zugehörige Entitäten und Informationen

    :param: werk_id: ID der Entität Werk
    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Werk-Nutzungen'
    aktives_menu = 'werke'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'LEFT JOIN verlag ON werk.fk_verlag_id_aktuell = verlag.verlag_id '
        'LEFT JOIN gattung ON werk.fk_gattung_id = gattung.gattung_id '
        'LEFT JOIN untergattung ON werk.fk_untergattung_id = untergattung.untergattung_id '
        'LEFT JOIN detailgattung ON werk.fk_detailgattung_id = detailgattung.detailgattung_id '
        'LEFT JOIN werkart ON werk.fk_werkart_id = werkart.werkart_id '
        'WHERE werk_id = ?',
        (werk_id,)
    )
    # Werk auf Basis der Werk-ID (+ Verlag, Gattung, Untergattung, Detailgattung und Werkart)
    werk = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM rism '
        'LEFT JOIN werk_rism ON rism.rism_id = werk_rism.fk_rism_id '
        'LEFT JOIN rism_kategorie ON rism.fk_rism_kategorie_id = rism_kategorie.rism_kategorie_id '
        'WHERE werk_rism.fk_werk_id = ?',
        (werk_id,)
    )
    # Besetzungen und deren Kategorie auf Basis der Werk-ID
    # Da mögliche mehrere Besetzungen nicht per LEFT JOIN möglich
    besetzungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * FROM werk WHERE werk_id = ?',
        (werk['fk_werk_id_gesamtwerk'],)
    )
    # Optionales Gesamtwerk
    gesamtwerk = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * FROM werk WHERE werk_id = ?',
        (werk['fk_werk_id_fassung_von'],)
    )
    # Optionales Grundwerk
    werk_fassung_von = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * FROM werk WHERE fk_werk_id_fassung_von = ?',
        (werk['werk_id'],)
    )
    # Optionale Fassung von Werk (werk-id)
    fassung_von_werk = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * '
        'FROM ausgabe '
        'LEFT JOIN verlag ON ausgabe.fk_verlag_id = verlag.verlag_id '
        'WHERE ausgabe.fk_werk_id = ?',
        (werk_id,)
    )
    # Optionale Ausgaben dieses Werkes
    ausgaben = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * '
        'FROM nutzung '
        'LEFT JOIN ort ON nutzung.fk_ort_id = ort.ort_id '
        'WHERE nutzung.fk_werk_id = ? AND nutzung.nutzung_ist_urauffuehrung = TRUE',
        (werk_id,)
    )
    # Optionale Uraufführung zum Werk
    urauffuehrung = database_cursor.fetchone()

    close_database_cursor()
    return render_template('werk/werk.html', title=webseite_titel, aktives_menu=aktives_menu, werk=werk, ausgaben=ausgaben, urauffuehrung=urauffuehrung, besetzungen=besetzungen, gesamtwerk=gesamtwerk, werk_fassung_von=werk_fassung_von, fassung_von_werk=fassung_von_werk, config=config)


@bp.route('/werk/verzeichnis')
def verzeichnis() -> str:
    """
    Erstellt und rendert das Werkverzeichnis

    Dies beinhaltet eine erweiterte Suche nach Werken
    Zusätzlich werden alle Gattungen/Untergattungen/Detailgattungen wählbar aufgelistet
    Auch alle Besetzungsmöglichkeiten mit Kategorie sind angegeben

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Werkverzeichnis'
    aktives_menu = 'werke'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * FROM werk;'
    )
    # Alle Werke zur erweiterten Werksuche (Vorschlagsliste: Werktitel)
    werke = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * FROM verlag;'
    )
    # Alle Verlage zur erweiterten Werksuche
    verlage = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT detailgattung.*, untergattung.fk_gattung_id, untergattung.untergattung_name, COUNT(werk_id) AS anzahl_werke '
        'FROM detailgattung '
        'LEFT JOIN untergattung ON detailgattung.fk_untergattung_id = untergattung.untergattung_id '
        'LEFT JOIN werk ON detailgattung.detailgattung_id = werk.fk_detailgattung_id '
        'GROUP BY detailgattung_id;'
    )
    # Alle Detailgattungen + Anzahl zugeordneter Werke (für Gattung-Auflistung)
    detailgattungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT untergattung.*, COUNT(werk_id) AS anzahl_werke '
        'FROM untergattung '
        'LEFT JOIN werk ON untergattung.untergattung_id = werk.fk_untergattung_id '
        'GROUP BY untergattung_id;'
    )
    # Alle Untergattungen + Anzahl zugeordneter Werke (für Gattung-Auflistung)
    untergattungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT gattung.*, COUNT(werk_id) AS anzahl_werke '
        'FROM gattung '
        'LEFT JOIN werk ON gattung.gattung_id = werk.fk_gattung_id '
        'GROUP BY gattung_id;'
    )
    # Alle Gattungen + Anzahl zugeordneter Werke (für Gattung-Auflistung)
    gattungen = database_cursor.fetchall()

    werk_gattungen = {}

    # Zusammenführung der drei Listen (Gattung, Untergattung, Detailgattung) auf Basis der jeweiligen Foreign Keys
    # Ausschnitt:
    # [ { 'gattung_id': 1, ..., 'untergattungen': [
    #       { 'untergattung_id': 1, ..., 'detailgattungen': [
    #               { 'detailgattung_id': 1, ... }, ...
    #       ] }, ...
    #   ] }, ...
    # ]
    for gattung in gattungen:
        werk_gattungen[gattung['gattung_id']] = gattung
        werk_gattungen[gattung['gattung_id']]['untergattungen'] = {}

    for untergattung in untergattungen:
        werk_gattungen[untergattung['fk_gattung_id']]['untergattungen'][untergattung['untergattung_id']] = untergattung
        werk_gattungen[untergattung['fk_gattung_id']]['untergattungen'][untergattung['untergattung_id']]['detailgattungen'] = {}

    for detailgattung in detailgattungen:
        werk_gattungen[detailgattung['fk_gattung_id']]['untergattungen'][detailgattung['fk_untergattung_id']]['detailgattungen'][detailgattung['detailgattung_id']] = detailgattung

    database_cursor.execute(
        'SELECT rism_kategorie.*, COUNT(werk_rism_id) AS anzahl_werke '
        'FROM rism_kategorie '
        'LEFT JOIN rism ON rism_kategorie.rism_kategorie_id = rism.fk_rism_kategorie_id '
        'LEFT JOIN werk_rism ON rism.rism_id = werk_rism.fk_rism_id '
        'GROUP BY rism_kategorie_id;'
    )
    # RISM Kategorien mit Anzahl verwendeter Werke für Besetzungsauflistung
    rism_kategorien = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT rism.*, COUNT(werk_rism_id) AS anzahl_werke '
        'FROM rism '
        'LEFT JOIN werk_rism ON rism.rism_id = werk_rism.fk_rism_id '
        'GROUP BY rism.rism_id'
    )
    # RISM Besaetzungen mit Anzahl verwendeter Werke für Besetzungsauflistung
    besetzungen_rism = database_cursor.fetchall()

    werk_besetzungen = {}

    # Zusammenführung der zwei Listen (RISM, RISM-Kategorie) auf Basis der Foreign Keys
    # Ausschnitt:
    # { 'rism_kategorie_id': { 'rism_kategorie_id': 1, ..., 'besetzungen': [ { 'rism_id': 1, ..., 'anzahl_werke': 5 }, ...] }, 'rism_kategorie_id': { ... }, ...  ]
    for rism_kategorie in rism_kategorien:
        werk_besetzungen[rism_kategorie['rism_kategorie_id']] = rism_kategorie
        werk_besetzungen[rism_kategorie['rism_kategorie_id']]['besetzungen'] = {}

    for besetzung_rism in besetzungen_rism:
        werk_besetzungen[besetzung_rism['fk_rism_kategorie_id']]['besetzungen'][besetzung_rism['rism_id']] = besetzung_rism

    close_database_cursor()
    return render_template('werk/verzeichnis.html', title=webseite_titel, aktives_menu=aktives_menu, werke=werke, verlage=verlage, werk_gattungen=werk_gattungen, werk_besetzungen=werk_besetzungen, gattungen=gattungen, untergattungen=untergattungen, detailgattungen=detailgattungen, rism_kategorien=rism_kategorien, besetzungen_rism=besetzungen_rism)
