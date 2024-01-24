from flask import (
    Blueprint, render_template
)

from zechlin import config
from zechlin.datenbank import get_database_connection, close_database_cursor

bp = Blueprint('auswertung', __name__)

"""
    Einheitliche Variablen:

        webseite_titel:     Titel des Browser-Tabs
        aktives_menu:  Tag, der zum Markieren des aktuellen Menüpunktes verwendet wird
"""


@bp.route('/auswertung/nutzung/karte')
def werknutzung_karte() -> str:
    """
    Lädt Informationen für eine kartografische Darstellung der Nutzungen und gibt diese zurück

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Nutzungs-Auswertung'
    aktives_menu = 'auswertung'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * '
        'FROM ort;'
    )
    # Alle Orte
    db_orte = database_cursor.fetchall()

    # Umwandlung Orte-Liste zu Dictionary, Ort-ID als Key
    # zuvor: [ { 'ort_id': 1, ... }, { 'ort_id': 2, ... }
    # danach: { 1: { 'ort_id: 1, ... }, 2: { 'ort_id': 2, ... }
    orte = {}
    for ort in db_orte:
        orte[ort['ort_id']] = ort
        orte[ort['ort_id']]['nutzungen'] = []

    database_cursor.execute(
        'SELECT * '
        'FROM nutzung '
        'LEFT JOIN ort ON nutzung.fk_ort_id = ort.ort_id '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
    )
    # Alle Nutzungen mit Ort- und Werkinformationen
    db_nutzungen = database_cursor.fetchall()

    # Umwandlung Nutzungen-Liste zu Dictionary, Nutzung-ID als Key
    # zuvor: [ { 'nutzung_id': 1, ... }, { 'nutzung_id': 2, ... }
    # danach: { 1: { 'nutzung_id: 1, ... }, 2: { 'nutzung_id': 2, ... }
    nutzungen = {}
    for nutzung in db_nutzungen:
        if nutzung['fk_ort_id'] is not None:
            nutzungen[nutzung['nutzung_id']] = nutzung
            orte[nutzung['fk_ort_id']]['nutzungen'].append(nutzung)

    database_cursor.execute(
        'SELECT MIN(nutzung_datum_jahr) AS min_datum_jahr, MAX(nutzung_datum_jahr) AS max_datum_jahr '
        'FROM nutzung'
    )
    # Niedrigstes und höchstes Nutzungsjahr
    statistik = database_cursor.fetchone()

    close_database_cursor()
    return render_template('auswertung/nutzung_karte.html', title=webseite_titel, aktives_menu=aktives_menu, nutzungen=nutzungen, orte=orte, statistik=statistik, config=config)


@bp.route('/auswertung/werkentstehung')
def werk_entstehung() -> str:
    """
    Lädt Informationen zum Anzeigen von Diagrammen in Bezug auf die Enstehungszeit der Werke

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Werk-Auswertung'
    aktives_menu = 'auswertung'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT MIN(werk_jahr_entstehung_ende) AS werke_jahr_entstehung_ende_min, MAX(werk_jahr_entstehung_ende) AS werke_jahr_entstehung_ende_max '
        'FROM werk'
    )
    # erste Jahreszahl & letzte Jahreszahl aus der Werkentstehung
    min_max_werk_jahr_entstehung_ende = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'LEFT JOIN gattung ON werk.fk_gattung_id = gattung.gattung_id '
        'LEFT JOIN untergattung ON werk.fk_untergattung_id = untergattung.untergattung_id '
        'LEFT JOIN detailgattung ON werk.fk_detailgattung_id = detailgattung.detailgattung_id;'
    )
    # Alle Werke
    werke = database_cursor.fetchall()

    daten_werke_entstehung_ende = {}
    # Erstellt für jedes Jahr zwischen Min-Jahr bis Max-Jahr ein Dictionary
    # Beispiel: { 1990: {}, 1991: {}, ... }
    for jahr in range(min_max_werk_jahr_entstehung_ende['werke_jahr_entstehung_ende_min'], min_max_werk_jahr_entstehung_ende['werke_jahr_entstehung_ende_max'] + 1):
        daten_werke_entstehung_ende[jahr] = {}
        daten_werke_entstehung_ende[jahr]['werke'] = []
        daten_werke_entstehung_ende[jahr]['gattungen'] = {}
        daten_werke_entstehung_ende[jahr]['untergattungen'] = {}

    anzahl_werke_ohne_jahr_entstehung_ende = 0
    # Befüllt leeres daten_werke_zeit Dictionary mit Werkinhalten:
    # Beispiel: { 1990: { 'anzahl': 15, 'werke': [ { 'werk_id': 1, ...}, ... ] } }
    for werk in werke:
        if werk['werk_jahr_entstehung_ende'] is None:
            anzahl_werke_ohne_jahr_entstehung_ende += 1
            continue

        daten_werke_entstehung_ende[werk['werk_jahr_entstehung_ende']]['werke'].append(werk)

    anzahl_werke_ohne_gattung = 0
    anzahl_werke_ohne_untergattung = 0
    # Erweitert das bestehende Dictionary um Gattung/Untergattung
    # Aufbau Gattung: { 1990: { ..., 'gattungen': { 1: [ { 'werk_id': 5, ..., 'gattung_id': 1 }, ... ] } } }
    for werk in werke:
        if werk['werk_jahr_entstehung_ende'] is None:
            continue

        if werk['gattung_id'] is None:
            anzahl_werke_ohne_gattung += 1
            continue

        if werk['gattung_id'] not in daten_werke_entstehung_ende[werk['werk_jahr_entstehung_ende']]['gattungen']:
            daten_werke_entstehung_ende[werk['werk_jahr_entstehung_ende']]['gattungen'][werk['gattung_id']] = []

        daten_werke_entstehung_ende[werk['werk_jahr_entstehung_ende']]['gattungen'][werk['gattung_id']].append(werk)

        if werk['untergattung_id'] is None:
            anzahl_werke_ohne_untergattung += 1
            continue

        if werk['untergattung_id'] not in daten_werke_entstehung_ende[werk['werk_jahr_entstehung_ende']]['untergattungen']:
            daten_werke_entstehung_ende[werk['werk_jahr_entstehung_ende']]['untergattungen'][werk['untergattung_id']] = []

        daten_werke_entstehung_ende[werk['werk_jahr_entstehung_ende']]['untergattungen'][werk['untergattung_id']].append(werk)

    statistik = {}
    statistik['anzahl_werke_ohne_jahr_entstehung_ende'] = anzahl_werke_ohne_jahr_entstehung_ende
    statistik['anzahl_werke_ohne_gattung'] = anzahl_werke_ohne_gattung
    statistik['anzahl_werke_ohne_untergattung'] = anzahl_werke_ohne_untergattung

    close_database_cursor()
    return render_template('auswertung/werk_entstehung.html', title=webseite_titel, aktives_menu=aktives_menu, werke=werke, daten_werke_entstehung_ende=daten_werke_entstehung_ende, statistik=statistik)


@bp.route('/auswertung/urauffuehrungen')
def werk_urauffuehrung() -> str:
    """
    Lädt Informationen zum Anzeigen von Diagrammen in Bezug auf die Uraufführungen der Werke

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Uraufführungen-Auswertung'
    aktives_menu = 'auswertung'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT MIN(nutzung_datum_jahr) AS min_nutzung_jahr, MAX(nutzung_datum_jahr) AS max_nutzung_jahr '
        'FROM nutzung '
        'WHERE nutzung_ist_urauffuehrung IS TRUE '
    )
    # Frühestes und spätestes Nutzungsjahr
    min_max_nutzung_jahr = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT MIN(werk_jahr_entstehung_ende) AS werke_jahr_entstehung_ende_min, MAX(werk_jahr_entstehung_ende) AS werke_jahr_entstehung_ende_max '
        'FROM werk'
    )
    # erste Jahreszahl & letzte Jahreszahl aus der Werkentstehung
    min_max_werk_jahr_entstehung_ende = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM nutzung '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'WHERE nutzung_ist_urauffuehrung IS TRUE'
    )
    # Alle Uraufführungen
    urauffuehrungen = database_cursor.fetchall()

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'LEFT JOIN gattung ON werk.fk_gattung_id = gattung.gattung_id '
        'LEFT JOIN untergattung ON werk.fk_untergattung_id = untergattung.untergattung_id '
        'LEFT JOIN detailgattung ON werk.fk_detailgattung_id = detailgattung.detailgattung_id;'
    )
    # Alle Werke
    werke = database_cursor.fetchall()

    if min_max_nutzung_jahr['min_nutzung_jahr'] < min_max_werk_jahr_entstehung_ende['werke_jahr_entstehung_ende_min']:
        min_jahr = min_max_nutzung_jahr['min_nutzung_jahr']
    else:
        min_jahr = min_max_werk_jahr_entstehung_ende['werke_jahr_entstehung_ende_min']

    if min_max_nutzung_jahr['max_nutzung_jahr'] > min_max_werk_jahr_entstehung_ende['werke_jahr_entstehung_ende_max']:
        max_jahr = min_max_nutzung_jahr['max_nutzung_jahr']
    else:
        max_jahr = min_max_werk_jahr_entstehung_ende['werke_jahr_entstehung_ende_max']

    daten_auswertung = {}
    # Erstellt für jedes Jahr zwischen Min-Jahr bis Max-Jahr ein Dictionary
    # Beispiel: { 1990: {}, 1991: {}, ... }
    for jahr in range(min_jahr, max_jahr + 1):
        daten_auswertung[jahr] = {}
        daten_auswertung[jahr]['urauffuehrungen'] = []
        daten_auswertung[jahr]['werke'] = []

    anzahl_nutzungen_ohne_datum_jahr = 0
    for nutzung in urauffuehrungen:
        if nutzung['nutzung_datum_jahr'] is None:
            anzahl_nutzungen_ohne_datum_jahr += 1
            continue

        daten_auswertung[nutzung['nutzung_datum_jahr']]['urauffuehrungen'].append(nutzung)

    anzahl_werke_ohne_jahr_entstehung_ende = 0
    # Befüllt leeres daten_werke_zeit Dictionary mit Werkinhalten:
    # Beispiel: { 1990: { 'anzahl': 15, 'werke': [ { 'werk_id': 1, ...}, ... ] } }
    for werk in werke:
        if werk['werk_jahr_entstehung_ende'] is None:
            anzahl_werke_ohne_jahr_entstehung_ende += 1
            continue

        daten_auswertung[werk['werk_jahr_entstehung_ende']]['werke'].append(werk)

    database_cursor.execute(
        'SELECT COUNT(werk_id) AS anzahl_werke '
        'FROM werk '
        'LEFT JOIN werkart ON werk.fk_werkart_id = werkart.werkart_id '
        'WHERE werk_id NOT IN (SELECT fk_werk_id FROM nutzung WHERE nutzung_ist_urauffuehrung IS TRUE AND fk_werk_id IS NOT NULL) '
        'AND werkart_name = "Komposition";'
    )
    werke_ohne_urauffuehrung = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT COUNT(werk_id) AS anzahl_werke '
        'FROM werk '
        'LEFT JOIN werkart ON werk.fk_werkart_id = werkart.werkart_id '
        'WHERE werk_id IN (SELECT fk_werk_id FROM nutzung WHERE nutzung_ist_urauffuehrung IS TRUE AND fk_werk_id IS NOT NULL) '
        'AND werkart_name = "Komposition"'
    )
    werke_mit_urauffuehrung = database_cursor.fetchone()

    werke_mit_ohne_urauffuehrung = {}
    werke_mit_ohne_urauffuehrung['Werke mit Uraufführung'] = werke_mit_urauffuehrung['anzahl_werke']
    werke_mit_ohne_urauffuehrung['Werke ohne Uraufführung'] = werke_ohne_urauffuehrung['anzahl_werke']

    statistik = {}
    statistik['anzahl_nutzungen_ohne_datum_jahr'] = anzahl_nutzungen_ohne_datum_jahr
    statistik['anzahl_werke_ohne_jahr_entstehung_ende'] = anzahl_werke_ohne_jahr_entstehung_ende

    close_database_cursor()
    return render_template('auswertung/werk_urauffuehrung.html', title=webseite_titel, aktives_menu=aktives_menu, urauffuehrungen=urauffuehrungen, statistik=statistik, daten_auswertung=daten_auswertung, werke_mit_ohne_urauffuehrung=werke_mit_ohne_urauffuehrung)


@bp.route('/auswertung/nutzungen')
def werk_nutzung() -> str:
    """
    Lädt Informationen zum Anzeigen von Diagrammen in Bezug auf die Nutzungen der Werke

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Nutzungs-Auswertung'
    aktives_menu = 'auswertung'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT MIN(nutzung_datum_jahr) AS min_nutzung_jahr, MAX(nutzung_datum_jahr) AS max_nutzung_jahr '
        'FROM nutzung '
    )
    # Frühestes und spätestes Nutzungsjahr
    min_max_nutzung_jahr = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM nutzung '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'WHERE nutzung_art IN ("Aufführung", "Uraufführung", "Erstaufführung")'
    )
    # Alle Nutzungen
    nutzungen = database_cursor.fetchall()

    daten_nutzung_auswertung = {}
    # Erstellt für jedes Jahr zwischen Min-Jahr bis Max-Jahr ein Dictionary
    # Beispiel: { 1990: {}, 1991: {}, ... }
    for jahr in range(min_max_nutzung_jahr['min_nutzung_jahr'], min_max_nutzung_jahr['max_nutzung_jahr'] + 1):
        daten_nutzung_auswertung[jahr] = {}
        daten_nutzung_auswertung[jahr]['nutzungen'] = []

    anzahl_nutzungen_ohne_datum_jahr = 0
    for nutzung in nutzungen:
        if nutzung['nutzung_datum_jahr'] is None:
            anzahl_nutzungen_ohne_datum_jahr += 1
            continue

        daten_nutzung_auswertung[nutzung['nutzung_datum_jahr']]['nutzungen'].append(nutzung)

    statistik = {}
    statistik['anzahl_nutzungen_ohne_datum_jahr'] = anzahl_nutzungen_ohne_datum_jahr

    close_database_cursor()
    return render_template('auswertung/nutzungen.html', title=webseite_titel, aktives_menu=aktives_menu, statistik=statistik, daten_nutzung_auswertung=daten_nutzung_auswertung)


@bp.route('/auswertung/werke/verlag')
def werk_verlag() -> str:
    """
    Lädt Informationen zum Anzeigen von Diagrammen in Bezug auf die Nutzungen der Werke

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Verlag-Auswertung'
    aktives_menu = 'auswertung'

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * '
        'FROM werk '
        'LEFT JOIN werkart ON werk.fk_werkart_id = werkart.werkart_id '
        'LEFT JOIN verlag ON werk.fk_verlag_id_aktuell = verlag.verlag_id '
        'WHERE werkart_name = "Komposition" '
        'ORDER BY fk_verlag_id_aktuell '
    )
    # Alle Werke mit zugehörigem Verlag
    werke = database_cursor.fetchall()

    daten_verlage = {}

    # Erstellen eines Dummy-Eintrages für "unverlegt"
    daten_verlage[0] = {}
    daten_verlage[0]['verlag_name'] = 'unverlegt'
    daten_verlage[0]['werke'] = []

    # Erstellt für jedes werk ein entsprechender Verlagindex:
    # { 1: { 'verlag_id': 1, ..., 'werke': [ { 'werk_id': 5, ... }, ... ] } }
    for werk in werke:
        if werk['fk_verlag_id_aktuell'] is None:
            daten_verlage[0]['werke'].append(werk)
            continue

        if werk['fk_verlag_id_aktuell'] not in daten_verlage:
            daten_verlage[werk['fk_verlag_id_aktuell']] = {}
            daten_verlage[werk['fk_verlag_id_aktuell']]['verlag_id'] = werk['verlag_id']
            daten_verlage[werk['fk_verlag_id_aktuell']]['verlag_name'] = werk['verlag_name']
            daten_verlage[werk['fk_verlag_id_aktuell']]['verlag_dnb'] = werk['verlag_dnb']
            daten_verlage[werk['fk_verlag_id_aktuell']]['werke'] = []

        daten_verlage[werk['fk_verlag_id_aktuell']]['werke'].append(werk)

    close_database_cursor()
    return render_template('auswertung/verlag.html', title=webseite_titel, aktives_menu=aktives_menu, daten_verlage=daten_verlage)
