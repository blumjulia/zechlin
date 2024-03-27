from flask import request, Blueprint, abort, render_template

from zechlin.auth import login_required
from zechlin.datenbank import get_database_connection, close_database_cursor

bp = Blueprint('suche', __name__)

# Konstanten für die Ermittlung der Optionen
OPERATOR_IST = 0
OPERATOR_NICHT = 10
OPERATOR_EXAKT = 1
OPERATOR_ENTHAELT = 2
OPERATOR_BEGINNT = 3
OPERATOR_ENDET = 4
OPERATOR_EXAKT_ZAHL = 5
OPERATOR_KLEINER = 6
OPERATOR_GROESSER = 7
OPERATOR_EXAKT_NICHT = 11
OPERATOR_ENTHAELT_NICHT = 12
OPERATOR_BEGINNT_NICHT = 13
OPERATOR_ENDET_NICHT = 14

# Such-Operatoren für SQL-Query
OPERATOR_SQL = {
    OPERATOR_EXAKT: 'LIKE "{}"',
    OPERATOR_ENTHAELT: 'LIKE "%{}%"',
    OPERATOR_BEGINNT: 'LIKE "{}%"',
    OPERATOR_ENDET: 'LIKE "%{}"',
    OPERATOR_EXAKT_NICHT: 'NOT LIKE "{}"',
    OPERATOR_ENTHAELT_NICHT: 'NOT LIKE "%{}%"',
    OPERATOR_BEGINNT_NICHT: 'NOT LIKE "{}%"',
    OPERATOR_ENDET_NICHT: 'NOT LIKE "%{}"',
    OPERATOR_EXAKT_ZAHL: '= {}',
    OPERATOR_GROESSER: '> {}',
    OPERATOR_KLEINER: '< {}'
}

"""
    Einheitliche Variablen:

        webseite_titel:     Titel des Browser-Tabs
        aktives_menu:       Tag, der zum Markieren des aktuellen Menüpunktes verwendet wird
"""


@bp.route('/ergebnis/schnellsuche', methods=['GET'])
@login_required
def ergebnis_schnellsuche() -> str:
    """
    Erstellt und rendert die Ergebnisse der Schnellsuche

    Dies beinhaltet aufgelistete Werke, Verlage, Orte, Nutzungen, Gattungen, Untergattungen und Detailgattungen

    :return: gerenderte Webseite
    """

    webseite_titel = 'Suchergebnis'
    aktives_menu = 'suche'

    # Suchbegriff aus Übergabe-Parametern
    suchbegriff = request.args['suchbegriff']

    if not suchbegriff:
        abort(404, 'Suchbegriff konnte nicht gefunden werden.')

    database_connection = get_database_connection()
    database_cursor = database_connection.cursor(dictionary=True)

    anzahl_ergebnisse = 0

    # Werke
    database_cursor.execute(
        'SELECT werk.*, verlag.verlag_name, '
        'GROUP_CONCAT(IFNULL(werk_titel,""), IFNULL(werk_untertitel, ""), IFNULL(werk_inhalt, ""), IFNULL(werk_jahr_entstehung_beginn, ""), IFNULL(werk_jahr_entstehung_ende, ""), IFNULL(werk_nummer_zechlin, ""), IFNULL(werk_textgrundlage_person, ""), IFNULL(werk_textgrundlage_werk, ""), IFNULL(werk_kuenstler_name, ""), IFNULL(werk_ort_autograph, ""), IFNULL(werk_ort_autograph_kopie, ""), IFNULL(werk_existenzhinweis, ""), IFNULL(werk_widmung, "") SEPARATOR ",") AS suchRelevant '
        'FROM werk '
        'LEFT JOIN verlag ON werk.fk_verlag_id_aktuell = verlag.verlag_id '
        'GROUP BY werk.werk_id '
        'HAVING suchRelevant LIKE ?;',
        ('%' + suchbegriff + '%',)
    )
    # Werke, welche im Titel, Untertitel, Inhalt, Entstehung Beginn/Ende, Werknummer, Textgrundlage Person/Werk, Künstlername, Autograph + Kopie, Existenzhinweis oder Widmung den Suchbegriff
    # Per GROUP_CONCAT wird ein String aus den einzelnen Einträgen erstellt (= "titel,untertitel,inhalt,[...]) -> dadurch kann der String auf Basis des Suchbegriffs durchsucht werden
    werke = database_cursor.fetchall()
    anzahl_ergebnisse += len(werke)

    database_cursor.execute(
        'SELECT werkart.* '
        'FROM werkart '
        'WHERE werkart_name LIKE ?',
        ('%' + suchbegriff + '%',)
    )
    # Werkarten, welche im Namen den Suchbegriff beinhalten
    werkarten = database_cursor.fetchall()
    anzahl_ergebnisse += len(werkarten)

    # Verlage
    database_cursor.execute(
        'SELECT *, '
        'GROUP_CONCAT(IFNULL(verlag_name, ""), IFNULL(verlag_dnb, ""), IFNULL(verlag_webseite, "") SEPARATOR ",") AS suchRelevant '
        'FROM verlag '
        'GROUP BY verlag_id '
        'HAVING suchRelevant LIKE ?;',
        ('%' + suchbegriff + '%',)
    )
    # Verlage, welche im Namen, DNB oder der Webseite den Suchbegriff beinhalten
    verlage = database_cursor.fetchall()
    anzahl_ergebnisse += len(verlage)

    # Orte
    database_cursor.execute(
        'SELECT *, '
        'GROUP_CONCAT(IFNULL(ort_name, ""), IFNULL(ort_adresse, "") SEPARATOR ",") AS suchRelevant '
        'FROM ort '
        'GROUP BY ort_id '
        'HAVING suchRelevant LIKE ?;',
        ('%' + suchbegriff + '%',)
    )
    # Orte, welche im Namen oder der Adresse den Suchbegriff beinhalten
    orte = database_cursor.fetchall()
    anzahl_ergebnisse += len(orte)

    # Nutzungen
    database_cursor.execute(
        'SELECT nutzung.*, werk.werk_titel, ort.ort_name, ort.ort_adresse, quelle_nutzung.quelle_nutzung_name, '
        'GROUP_CONCAT(IFNULL(nutzung_kontext, ""), IFNULL(nutzung_erstauffuehrung_kommentar, ""), IFNULL(nutzung_kommentar, ""), IFNULL(nutzung_datum_kommentar, ""), IFNULL(nutzung_beteiligte, ""), IFNULL(ort_name, ""), IFNULL(ort_adresse, ""), IFNULL(quelle_nutzung_name, "") SEPARATOR ",") AS suchRelevant '
        'FROM nutzung '
        'LEFT JOIN ort ON nutzung.fk_ort_id = ort.ort_id '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'LEFT JOIN quelle_nutzung ON nutzung.nutzung_id = quelle_nutzung.fk_nutzung_id '
        'GROUP BY nutzung.nutzung_id '
        'HAVING suchRelevant LIKE ?;',
        ('%' + suchbegriff + '%',)
    )
    # Nutzungen, welche im Kontext, Kommentaren, Beteiligten, Ort Name/Adresse oder der Quelle den Suchbegriff beinhalten
    nutzungen = database_cursor.fetchall()
    anzahl_ergebnisse += len(nutzungen)

    # Gattungen
    database_cursor.execute(
        'SELECT * '
        'FROM gattung '
        'WHERE gattung_name LIKE ?;',
        ('%' + suchbegriff + '%',)
    )
    # Gattungen, welche im Namen den Suchbegriff beinhalten
    gattungen = database_cursor.fetchall()
    anzahl_ergebnisse += len(gattungen)

    # Untergattungen
    database_cursor.execute(
        'SELECT * '
        'FROM untergattung '
        'LEFT JOIN gattung ON untergattung.fk_gattung_id = gattung.gattung_id '
        'WHERE untergattung_name LIKE ?;',
        ('%' + suchbegriff + '%',)
    )
    # Untergattungen, welche im Namen den Suchbegriff beinhalten
    untergattungen = database_cursor.fetchall()
    anzahl_ergebnisse += len(untergattungen)

    # Detailgattung
    database_cursor.execute(
        'SELECT * '
        'FROM detailgattung '
        'LEFT JOIN untergattung ON detailgattung.fk_untergattung_id = untergattung.untergattung_id '
        'WHERE detailgattung.detailgattung_name LIKE ?;',
        ('%' + suchbegriff + '%',)
    )
    # Detailgattungen, welche im Namen den Suchbegriff beinhalten
    detailgattungen = database_cursor.fetchall()
    anzahl_ergebnisse += len(detailgattungen)

    close_database_cursor()
    return render_template('suche/ergebnis_schnellsuche.html', title=webseite_titel, aktives_menu=aktives_menu, suchbegriff=suchbegriff, anzahl_ergebnisse=anzahl_ergebnisse, werke=werke, werkarten=werkarten, verlage=verlage, orte=orte, nutzungen=nutzungen, gattungen=gattungen, untergattungen=untergattungen, detailgattungen=detailgattungen)


@bp.route('/ergebnis/werksuche', methods=['GET'])
@login_required
def ergebnis_werksuche() -> str:
    """
    Erstellt und rendert die Ergebnisse der erweiterten Werksuche

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Ergebnis erweiterte Suche'
    aktives_menu = 'suche'

    # Form Element-Namen und deren Werte (HTML-Form)
    eingaben = request.args

    # SQL Query Grundstruktur
    sql_query_select = 'SELECT * '
    sql_query_from = 'FROM werk '
    sql_query_joins = ''
    sql_query_where = ''
    rism_query_joins = False

    such_bedingungen = []

    # Erweiterung der Suche um Titel, falls angegeben
    if 'titel' in eingaben and eingaben['titel'] != '':
        operator = int(eingaben['titel_operator']) + int(eingaben['titel_nicht'])
        such_bedingungen.append('werk.werk_titel ' + OPERATOR_SQL[operator].format(eingaben['titel']))

    # Erweiterung der Suche um Untertitel, falls angegeben
    if 'untertitel' in eingaben and eingaben['untertitel'] != '':
        operator = int(eingaben['untertitel_operator']) + int(eingaben['untertitel_nicht'])
        such_bedingungen.append('werk.werk_untertitel ' + OPERATOR_SQL[operator].format(eingaben['untertitel']))

    # Erweiterung der Suche um Werkinhalt, falls angegeben
    if 'werkinhalt' in eingaben and eingaben['werkinhalt'] != '':
        operator = int(eingaben['werkinhalt_operator']) + int(eingaben['werkinhalt_nicht'])
        such_bedingungen.append('werk.werk_inhalt ' + OPERATOR_SQL[operator].format(eingaben['werkinhalt']))

    # Erweiterung der Suche um Entstehungsjahr Beginn, falls angegeben
    if 'jahr_entstehung_beginn' in eingaben and eingaben['jahr_entstehung_beginn'] != '':
        such_bedingungen.append('(werk.werk_jahr_entstehung_beginn IS NOT NULL AND werk.werk_jahr_entstehung_beginn >= ' + eingaben['jahr_entstehung_beginn'] + ')')

    # Erweiterung der Suche um Entstehungsjahr Ende, falls angegeben
    if 'jahr_entstehung_ende' in eingaben and eingaben['jahr_entstehung_ende'] != '':
        such_bedingungen.append('(werk.werk_jahr_entstehung_ende IS NOT NULL AND werk.werk_jahr_entstehung_ende <= ' + eingaben['jahr_entstehung_ende'] + ')')

    # Erweiterung der Suche um Textgrundlage (Person oder Werk), falls angegeben
    if 'textgrundlage' in eingaben and eingaben['textgrundlage'] != '':
        operator = int(eingaben['textgrundlage_operator']) + int(eingaben['textgrundlage_nicht'])
        such_bedingungen.append('(werk.werk_textgrundlage_person ' + OPERATOR_SQL[operator].format(eingaben['textgrundlage']) + ' OR werk.werk_textgrundlage_werk ' + OPERATOR_SQL[operator].format(eingaben['textgrundlage']) + ')')

    # Erweiterung der Suche um Spieldauer, falls angegeben
    if 'spieldauer' in eingaben and eingaben['spieldauer'] != '':
        operator = int(eingaben['spieldauer_operator'])
        zeit = int(eingaben['spieldauer']) * int(eingaben['spieldauer_einheit'])
        such_bedingungen.append('werk.werk_spieldauer_in_s ' + OPERATOR_SQL[operator].format(zeit))

    # Erweiterung der Suche um Widmung, falls angegeben
    if 'widmung' in eingaben and eingaben['widmung'] != '':
        operator = int(eingaben['widmung_operator']) + int(eingaben['widmung_nicht'])
        such_bedingungen.append('werk.werk_widmung ' + OPERATOR_SQL[operator].format(eingaben['widmung']))

    # Erweiterung der Suche um Gattung, falls angegeben
    if 'gattung' in eingaben and eingaben['gattung'] != '0':
        such_bedingungen.append('werk.fk_gattung_id = ' + eingaben['gattung'])

    # Erweiterung der Suche um Untergattung, falls angegeben
    if 'untergattung' in eingaben and eingaben['untergattung'] != '0':
        such_bedingungen.append('werk.fk_untergattung_id = ' + eingaben['untergattung'])

    # Erweiterung der Suche um Detailgattung, falls angegeben
    if 'detailgattung' in eingaben and eingaben['detailgattung'] != '0':
        such_bedingungen.append('werk.fk_detailgattung_id = ' + eingaben['detailgattung'])

    # Erweiterung der Suche um RISM Kategorie, falls angegeben
    if 'rism_kategorie' in eingaben and eingaben['rism_kategorie'] != '0':
        rism_query_joins = True
        such_bedingungen.append('rism.fk_rism_kategorie_id = ' + eingaben['rism_kategorie'])

    # Erweiterung der Suche um RISM, falls angegeben
    if 'rism' in eingaben and eingaben['rism'] != '0':
        rism_query_joins = True
        such_bedingungen.append('rism.rism_id = ' + eingaben['rism'])

    # Erweiterung der Suche um Verlag, falls angegeben
    if 'verlag_aktuell' in eingaben and eingaben['verlag_aktuell'] != '0':
        such_bedingungen.append('werk.fk_verlag_id_aktuell = ' + eingaben['verlag_aktuell'])

    # Erweiterung des SQL Queries um JOINs
    if (rism_query_joins):
        sql_query_joins += ' LEFT JOIN werk_rism ON werk.werk_id = werk_rism.fk_werk_id '
        sql_query_joins += ' LEFT JOIN rism ON werk_rism.fk_rism_id = rism.rism_id '

    # Zusammensetzung des 'WHERE CLAUSE'-Teils
    if len(such_bedingungen) > 0:
        sql_query_where = 'WHERE ' + ' AND '.join(such_bedingungen)

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        sql_query_select + sql_query_from + sql_query_joins + sql_query_where
    )
    # Alle Werke, die der Suche entsprechen
    werke = database_cursor.fetchall()

    close_database_cursor()
    return render_template('suche/ergebnis_werksuche.html', title=webseite_titel, aktives_menu=aktives_menu, eingaben=eingaben, werke=werke)


@bp.route('/ergebnis/nutzungssuche', methods=['GET'])
@login_required
def ergebnis_nutzungssuche():
    """
    Erstellt und rendert die Ergebnisse der erweiterten Nutzungssuche

    :return: gerenderte Webseite
    """

    webseite_titel = 'Zechlin | Ergebnis erweiterte Nutzungssuche'
    aktives_menu = 'suche'

    # Form Element-Namen und deren Werte (HTML-Form)
    eingaben = request.args

    # SQL Query Grundstruktur
    sql_query_select = 'SELECT nutzung.*, ort.ort_name, werk.werk_titel '
    sql_query_from = 'FROM nutzung '
    sql_query_joins = 'LEFT JOIN ort ON nutzung.fk_ort_id = ort.ort_id '
    sql_query_joins += ' LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
    sql_query_where = ''

    such_bedingungen = []

    # Erweiterung der Suche um Werktitel, falls angegeben
    if 'werktitel' in eingaben and eingaben['werktitel'] != '':
        operator = int(eingaben['werktitel_operator']) + int(eingaben['werktitel_nicht'])
        such_bedingungen.append('werk.werk_titel ' + OPERATOR_SQL[operator].format(eingaben['werktitel']))

    # Erweiterung der Suche um Nutzungskontext, falls angegeben
    if 'kontext' in eingaben and eingaben['kontext'] != '':
        operator = int(eingaben['kontext_operator']) + int(eingaben['kontext_nicht'])
        such_bedingungen.append('nutzung.nutzung_kontext ' + OPERATOR_SQL[operator].format(eingaben['kontext']))

    # Erweiterung der Suche um Nutzungsart, falls angegeben
    if 'art' in eingaben and eingaben['art'] != '':
        such_bedingungen.append('nutzung.nutzung_art = "' + eingaben['art'] + '"')

    # Erweiterung der Suche um Nutzungsbeteiligte, falls angegeben
    if 'beteiligte' in eingaben and eingaben['beteiligte'] != '':
        operator = int(eingaben['beteiligte_operator']) + int(eingaben['beteiligte_nicht'])
        such_bedingungen.append('nutzung.nutzung_beteiligte ' + OPERATOR_SQL[operator].format(eingaben['beteiligte']))

    # Erweiterung der Suche um Nutzungstag, falls angegeben
    if 'nutzung_datum_tag' in eingaben and eingaben['nutzung_datum_tag'] != '0':
        operator = int(eingaben['nutzung_datum_operator'])
        such_bedingungen.append('(nutzung.nutzung_datum_tag IS NOT NULL AND nutzung.nutzung_datum_tag ' + OPERATOR_SQL[operator].format(eingaben['nutzung_datum_tag'] + ')'))

    # Erweiterung der Suche um Nutzungsmonat, falls angegeben
    if 'nutzung_datum_monat' in eingaben and eingaben['nutzung_datum_monat'] != '0':
        operator = int(eingaben['nutzung_datum_operator'])
        such_bedingungen.append('(nutzung.nutzung_datum_monat IS NOT NULL AND nutzung.nutzung_datum_monat ' + OPERATOR_SQL[operator].format(eingaben['nutzung_datum_monat'] + ')'))

    # Erweiterung der Suche um Nutzungsjahr, falls angegeben
    if 'nutzung_datum_jahr' in eingaben and eingaben['nutzung_datum_jahr'] != '0':
        operator = int(eingaben['nutzung_datum_operator'])
        such_bedingungen.append('(nutzung.nutzung_datum_jahr IS NOT NULL AND nutzung.nutzung_datum_jahr ' + OPERATOR_SQL[operator].format(eingaben['nutzung_datum_jahr'] + ')'))

    # Erweiterung der Suche um Nutzungs-Spieldauer, falls angegeben
    if 'spieldauer' in eingaben and eingaben['spieldauer'] != '':
        operator = int(eingaben['spieldauer_operator'])
        zeit = int(eingaben['spieldauer']) * int(eingaben['spieldauer_einheit'])
        such_bedingungen.append('nutzung.nutzung_spieldauer_in_s ' + OPERATOR_SQL[operator].format(zeit))

    # Erweiterung der Suche um Nutzungsort, falls angegeben
    if 'ort' in eingaben and eingaben['ort'] != '0':
        such_bedingungen.append('nutzung.fk_ort_id = ' + eingaben['ort'])

    if len(such_bedingungen) > 0:
        # Zusammensetzen der 'WHERE CLAUSE'-Teils
        sql_query_where = 'WHERE ' + ' AND '.join(such_bedingungen)

    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        sql_query_select + sql_query_from + sql_query_joins + sql_query_where
    )
    # Alle Nutzungen basierend auf den Suchparametern
    nutzungen = database_cursor.fetchall()

    close_database_cursor()
    return render_template('suche/ergebnis_nutzungssuche.html', title=webseite_titel, aktives_menu=aktives_menu, eingaben=eingaben, nutzungen=nutzungen)
