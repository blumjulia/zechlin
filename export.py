# https://schema.org/docs/schemas.html
# https://www.bach-digital.de/receive/BachDigitalWork_work_00001496?XSL.Style=jsonld
# https://www.bach-digital.de/receive/BachDigitalWork_work_00011958?XSL.Style=jsonld
# https://www.w3.org/TR/json-ld11/#design-goals-and-rationale
import json

from flask import Blueprint, url_for

from zechlin import config
from zechlin.auth import login_required
from zechlin.datenbank import get_database_connection

bp = Blueprint('export', __name__)

# JSON-LD Kontext zur Entität 'Werk'
JSON_LD_WERK_CONTEXT = {
    'schema': 'https://schema.org/',
    'Werktitel': 'schema:name',
    'Werkuntertitel': 'schema:alternativeHeadline',
    'Werknummer': 'schema:alternateName',
    'FassungVon': 'schema:isBasedOn',
    'Gattung': 'schema:musicCompositionForm',
    'Untergattung': 'schema:musicCompositionForm',
    'Detailgattung': 'schema:musicCompositionForm',
    'Komponist': 'schema:composer',
    'Besetzung': 'schema:musicArrangement',
    'Besetzung rism': 'schema:musicArrangement',
    'Textgrundlage (Personen)': 'schema:comment',
    'Textgrundlage (Text)': 'schema:comment',
    'Entstehungszeit': 'schema:temporalCoverage',
    'Uraufführung': 'schema:firstPerformance',
    'GND-IDN': 'schema:identifier'
}

# JSON-LD Kontext zur Entität 'Person'
JSON_LD_PERSON_CONTEXT = {
    'schema': 'https://schema.org/',
    'Name': 'schema:name',
    'akademischer Titel': 'schema:honorificPrefix',
    'Titel': 'schema:honorificPrefix',
    'Adelstitel': 'schema:honorificPrefix',
    'Vorname': 'schema:givenName',
    'Rufname': 'schema:additionalName',
    'Nachname': 'schema:familyName',
    'Weitere Namensformen': 'schema:additionalName',
    'Geschlecht': 'schema:gender',
    'Ethnikon': 'schema:nationality',
    'Geburtsdatum': 'schema:birthDate',
    'Geburtsort': 'schema:birthPlace',
    'Todesdatum': 'schema:deathDate',
    'Sterbeort': 'schema:deathPlace',
    'Beruf(e)': 'schema:jobTitle',
    'Geographischer Wirkungsbereich': 'schema:workLocation',
    'Institutionelle Zugehörigkeit': 'schema:memberOf',
    'GND-ID': 'schema:identifier',
    'VIA-ID': 'schema:identifier',
}

# JSON-LD Kontext zur Entität 'Nutzung'
JSON_LD_EVENT_CONTEXT = {
    'schema': 'https://schema.org/',
    'Name': 'schema:name',
    'startDate': 'schema:startDate',
    'Komponist': 'schema:composer',
    'Ort': 'schema:location',
    'Aufgeführtes Werk': 'schema:workPerformed',
    'Beteiligte': 'schema:text',  # schema:performer
}

# JSON-LD Kontext zur Entität 'Ort'
JSON_LD_PLACE_CONTEXT = {
    'schema': 'https://schema.org',
    'Name': 'schema:name',
    'Adresse': 'schema:address',
    'Latitude': 'schema:latitude',
    'Longitude': 'schema:longitude'
}

# JSON-LD Daten zur Person Ruth Zechlin
JSON_LD_RUTH_ZECHLIN = {
    '@type': 'schema:Person',
    '@context': JSON_LD_PERSON_CONTEXT,
    'Name': 'Zechlin, Ruth',
    'Vorname': 'Ruth',
    'Nachname': 'Zechlin',
    'Weitere Namensformen': 'Ruth Oschatz, Oschatz, Ruth, Zechlin, Ruth, R. Zechlin, R. Oschatz',
    'Geschlecht': 'weiblich',
    'Geburtsdatum': '1926-06-22',
    'Geburtsort': 'Grosshartmannsdorf',
    'Todesdatum': '2007-08-04',
    'Sterbeort': 'München',
    'GND-ID': {'@type': 'schema:PropertyValue', 'schema:propertyID': 'GND-ID', 'schema:value': 'https://d-nb.info/gnd/118830511'},
    'VIA-ID': {'@type': 'schema:PropertyValue', 'schema:propertyID': 'VIA-ID', 'schema:value': 'https://viaf.org/viaf/74650202/'},
}

# ISO 8601 Standard zur Angabe von Datum + Uhrzeit
ISO_8601_DATUM_ZEIT = '{jahr}-{monat}-{tag}T{stunde}:{minute}:00Z'
ISO_8601_DATUM = '{jahr}-{monat}-{tag}'
ISO_8601_MONAT_JAHR = '{jahr}-{monat}'
ISO_8601_JAHR = '{jahr}'


@bp.route('/export/json_ld/werk/<int:werk_id>')
@login_required
def json_ld_werk(werk_id) -> json:
    return _get_json_ld_werk(werk_id, True)


@bp.route('/export/json_ld/nutzung/<int:nutzung_id>')
@login_required
def json_ld_nutzung(nutzung_id) -> json:
    return _get_json_ld_nutzung(nutzung_id, True)


@bp.route('/export/json_ld/ort/<int:ort_id>')
@login_required
def json_ld_ort(ort_id) -> json:
    return _get_json_ld_ort(ort_id)

def _get_json_ld_werk(werk_id, nutzung_beinhalten=True):
    """
        Gibt die Entität Werk im JSON-LD Format zurück

        :param werk_id: ID des angefragten Werkes
        :param nutzung_beinhalten: Boolscher Wert zur Vermeidung von Mehrfachverweisen
        :return: JSON-LD des Werkes
        """
    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT werk.*, gattung.gattung_name, untergattung.untergattung_name, detailgattung.detailgattung_name '
        'FROM werk '
        'LEFT JOIN gattung ON werk.fk_gattung_id = gattung.gattung_id '
        'LEFT JOIN untergattung ON werk.fk_untergattung_id = untergattung.untergattung_id '
        'LEFT JOIN detailgattung ON werk.fk_detailgattung_id = detailgattung.detailgattung_id '
        'WHERE werk.werk_id = ? ',
        (werk_id,)
    )
    # Einzelnes Werk, basierend auf Werk-ID (+ zugehörigen Gattung, Untergattung und Detailgattung)
    werk = database_cursor.fetchone()

    database_cursor.execute(
        'SELECT * '
        'FROM rism '
        'LEFT JOIN werk_rism ON rism.rism_id = werk_rism.fk_rism_id '
        'WHERE fk_werk_id = ?',
        (werk_id,)
    )
    # Alle RISM Besetzungen des Werkes
    besetzungen_rism = database_cursor.fetchall()

    # Grundstruktur JSON-LD (schema.org)
    json_return = {
        '@context': JSON_LD_WERK_CONTEXT,
        '@type': 'schema:MusicComposition',
        '@id': url_for('index.pid', pid=config.pid['prefix'] + config.pid['separator'] + config.pid['objekt']['werk'] + config.pid['separator'] + str(werk['werk_id']), _external=True),
        'encodingFormat': 'application/json',
        'Werktitel': werk['werk_titel'],
    }

    if werk['werk_untertitel'] is not None:
        json_return['Werkuntertitel'] = werk['werk_untertitel']

    if werk['werk_nummer_zechlin'] is not None:
        json_return['Werknummer'] = werk['werk_nummer_zechlin']

    if werk['fk_werk_id_fassung_von'] is not None:
        json_return['FassungVon'] = _get_json_ld_werk(werk['fk_werk_id_fassung_von'])

    if werk['fk_gattung_id'] is not None:
        json_return['Gattung'] = werk['gattung_name']

    if werk['fk_untergattung_id'] is not None:
        json_return['Untergattung'] = werk['untergattung_name']

    if werk['fk_detailgattung_id'] is not None:
        json_return['Detailgattung'] = werk['detailgattung_name']

    # Einbinden des vordefinierten JSON-LD zur Person Ruth Zechlin (Kontext + Daten)
    json_return['Komponist'] = JSON_LD_RUTH_ZECHLIN

    # Besetzungsangaben werden als Array hinzugefügt
    if len(besetzungen_rism) > 0:
        json_return['Besetzung'] = []
        json_return['Besetzung rism'] = []

        for besetzung in besetzungen_rism:
            json_return['Besetzung'].append(besetzung['rism_beschreibung'])
            json_return['Besetzung rism'].append(besetzung['rism_code'])

    if werk['werk_textgrundlage_person'] is not None:
        json_return['Textgrundlage (Personen)'] = werk['werk_textgrundlage_person']

    if werk['werk_textgrundlage_werk'] is not None:
        json_return['Textgrundlage (Text)'] = werk['werk_textgrundlage_werk']

    if werk['werk_jahr_entstehung_beginn'] is not None and werk['werk_jahr_entstehung_ende'] is not None:
        if werk['werk_jahr_entstehung_beginn'] == werk['werk_jahr_entstehung_ende']:
            json_return['Entstehungszeit'] = str(werk['werk_jahr_entstehung_beginn'])
        else:
            json_return['Entstehungszeit'] = str(werk['werk_jahr_entstehung_beginn']) + '-' + str(werk['werk_jahr_entstehung_ende'])
    else:
        json_return['Entstehungszeit'] = 'unbekannt'

    database_cursor.execute(
        'SELECT * '
        'FROM nutzung '
        'WHERE fk_werk_id = ? AND nutzung_ist_urauffuehrung = TRUE',
        (werk_id,)
    )
    # Uraufführung des Werkes
    urauffuehrung = database_cursor.fetchone()

    if urauffuehrung and nutzung_beinhalten:
        # Nutzung nur hinzufügen wenn angegeben um mehrfach-verweis zu verhindern
        json_return['Uraufführung'] = json_ld_nutzung(urauffuehrung['nutzung_id'], False)

    # Rückgabe im JSON-Format
    return json_return

def _get_json_ld_nutzung(nutzung_id, gespieltes_werk=True):
    """
        Gibt die Entität Nutzung im JSON-LD Format zurück

        :param nutzung_id: ID der angefragten Nutzung
        :param gespieltes_werk: Boolscher Wert zur Vermeidung von Mehrfachverweisen
        :return: JSON-LD der Nutzung
        """
    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT nutzung.*, werk.werk_kuenstler_name '
        'FROM nutzung '
        'LEFT JOIN werk ON nutzung.fk_werk_id = werk.werk_id '
        'WHERE nutzung_id = ?',
        (nutzung_id,)
    )
    # Nutzung basierend auf nutzung_id mit Künstlername aus Werk
    nutzung = database_cursor.fetchone()

    # Grundstruktur JSON-LD (schema.org)
    json_return = {
        '@context': JSON_LD_EVENT_CONTEXT,
        '@type': 'schema:Event',
        '@id': url_for('index.pid', pid=config.pid['prefix'] + config.pid['separator'] + config.pid['objekt']['nutzung'] + config.pid['separator'] + str(nutzung['nutzung_id']), _external=True),
        'encodingFormat': 'application/json',
    }

    if nutzung['nutzung_kontext'] is not None:
        json_return['Name'] = nutzung['nutzung_kontext']
    else:
        json_return['Name'] = 'unbekannt'

    tag = nutzung['nutzung_datum_tag']
    monat = nutzung['nutzung_datum_monat']
    jahr = nutzung['nutzung_datum_jahr']
    stunde = nutzung['nutzung_zeit_stunde']
    minute = nutzung['nutzung_zeit_minute']

    # Rückgabe des Datum-Wertes je nach Informationslage:
    # - Datum und Uhrzeit
    # - Datum ohne Uhrzeit
    # - Monat und Jahr
    # - Jahr
    if tag is not None and monat is not None and jahr is not None:
        if stunde is not None and minute is not None:
            json_return['startDate'] = ISO_8601_DATUM_ZEIT.format(jahr=str(jahr), monat=str(monat), tag=str(tag), stunde=str(stunde), minute=str(minute))
        else:
            json_return['startDate'] = ISO_8601_DATUM.format(jahr=str(jahr), monat=str(monat), tag=str(tag))
    elif monat is not None and jahr is not None:
        json_return['startDate'] = ISO_8601_MONAT_JAHR.format(jahr=str(jahr), monat=str(monat))
    elif jahr is not None:
        json_return['startDate'] = ISO_8601_JAHR.format(jahr=str(jahr))

    json_return['Komponist'] = JSON_LD_RUTH_ZECHLIN

    if nutzung['fk_ort_id'] is not None:
        json_return['Ort'] = _get_json_ld_ort(nutzung['fk_ort_id'])

    if gespieltes_werk:
        if nutzung['fk_werk_id'] is not None:
            json_return['Aufgeführtes Werk'] = _get_json_ld_werk(nutzung['fk_werk_id'], False)

    if nutzung['nutzung_beteiligte'] is not None:
        json_return['Beteiligte'] = nutzung['nutzung_beteiligte']

    # Rückgabe im JSON-Format
    return json_return

def _get_json_ld_ort(ort_id):
    """
        Gibt die Entität Ort als JSON-LD Format zurück

        :param ort_id: ID des angefragten Ortes
        :return: JSON-LD des Werkes
        """
    database_cursor = get_database_connection().cursor(dictionary=True)

    database_cursor.execute(
        'SELECT * '
        'FROM ort '
        'WHERE ort_id = ?',
        (ort_id,)
    )
    # Ort auf Basis der Ort-ID
    ort = database_cursor.fetchone()

    # Grundstruktur von JSON-LD (schema.org)
    json_return = {
        '@context': JSON_LD_PLACE_CONTEXT,
        '@type': 'schema:Place',
        '@id': url_for('index.pid', pid=config.pid['prefix'] + config.pid['separator'] + config.pid['objekt']['nutzung'] + config.pid['separator'] + str(ort['ort_id']), _external=True),
        'encodingFormat': 'application/json',
    }

    if ort['ort_name'] is not None:
        json_return['Name'] = ort['ort_name']

    if ort['ort_adresse'] is not None:
        json_return['Adresse'] = {'schema:text': ort['ort_adresse']}

    if ort['ort_latitude'] is not None and ort['ort_longitude'] is not None:
        json_return['Latitude'] = {'schema:text': ort['ort_latitude']}
        json_return['Longitude'] = {'schema:text': ort['ort_longitude']}

    # Rückgabe im JSON-Format
    return json_return